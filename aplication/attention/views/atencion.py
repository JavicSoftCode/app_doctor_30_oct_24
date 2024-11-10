from typing import Dict, Any, List, Set, Tuple

from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.http import JsonResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.translation import gettext as _
from django.views.generic import ListView, DeleteView, DetailView, UpdateView, CreateView

from aplication.attention.forms.atencion import AtencionForm, DetalleAtencionFormset, DetalleAtencionFormsetCreate
from aplication.attention.models import Atencion, DetalleAtencion
from aplication.core.models import Medicamento
from doctor.utils import save_audit


class AtencionListView(ListView):
  model = Atencion
  template_name = "attention/atencion/list.html"
  context_object_name = "atenciones"
  paginate_by = 5

  def get_queryset(self):
    self.query = Q()
    q1 = self.request.GET.get('q')

    if q1:
      if q1.isdigit():
        self.query.add(Q(id=q1), Q.AND)

      self.query.add(Q(paciente__nombres__icontains=q1), Q.OR)
      self.query.add(Q(paciente__apellidos__icontains=q1), Q.OR)
      self.query.add(Q(paciente__cedula__icontains=q1), Q.OR)

      self.query.add(Q(diagnostico__codigo__icontains=q1), Q.OR)

    return self.model.objects.filter(self.query).distinct().order_by('paciente__apellidos')

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context['title1'] = "Listado de Atención"
    context['title2'] = "Nueva Atención"
    return context


class AtencionCreateView(CreateView):
  model = Atencion
  form_class = AtencionForm
  template_name = "attention/atencion/form.html"
  success_url = reverse_lazy("attention:atencion_list")

  def validate_formset_data(self, formset) -> tuple[bool, List[str], List[Any]]:
    """
    Validates formset data and returns validation status, error messages and valid details
    """
    detalles_validos = []
    medicamentos_vistos: Set = set()
    error_mensajes: List[str] = []

    # Check if formset has any valid data
    formset_tiene_datos = any(
      form.has_changed() and not form.cleaned_data.get("DELETE", False)
      for form in formset
    )

    if not formset_tiene_datos:
      error_mensajes.append(_("No se permite guardar esta atención, falta llenar detalle atención."))
      return False, error_mensajes, detalles_validos

    # Validate each detail form
    for form in formset:
      if form.cleaned_data and not form.cleaned_data.get("DELETE", False):
        try:
          detalle = form.save(commit=False)
          self._validate_medicamento(detalle, medicamentos_vistos, error_mensajes)
          self._validate_cantidad(detalle, error_mensajes)

          if not error_mensajes:
            detalles_validos.append(detalle)

        except ValidationError as e:
          error_mensajes.extend(e.messages)

    return not bool(error_mensajes), error_mensajes, detalles_validos

  def _validate_medicamento(self, detalle: DetalleAtencion, medicamentos_vistos: Set,
                            error_mensajes: List[str]) -> None:
    """Validates medication and checks for duplicates"""
    if not detalle.medicamento:
      raise ValidationError(_("Debe seleccionar un medicamento."))

    if detalle.medicamento in medicamentos_vistos:
      error_mensajes.append(f"Medicamento repetido: {detalle.medicamento.nombre}.")
    else:
      medicamentos_vistos.add(detalle.medicamento)

  def _validate_cantidad(self, detalle: DetalleAtencion, error_mensajes: List[str]) -> None:
    """Validates quantity against stock and minimum values"""
    if detalle.cantidad <= 0:
      error_mensajes.append(_("La cantidad no puede ser cero o negativa."))
      return

    if detalle.cantidad > detalle.medicamento.cantidad:
      error_mensajes.append(
        f"Stock insuficiente de {detalle.medicamento.nombre}. "
        f"Disponible: {detalle.medicamento.cantidad}, Solicitado: {detalle.cantidad}"
      )

  def save_atencion(self, form: AtencionForm, detalles_validos: List[DetalleAtencion]) -> Atencion:
    """Saves the attention and its details in a transaction"""
    with transaction.atomic():
      atencion = form.save()

      for detalle in detalles_validos:
        # Update stock
        detalle.medicamento.cantidad -= detalle.cantidad
        detalle.medicamento.save()

        # Save detail
        detalle.atencion = atencion
        detalle.save()

      # Audit log
      save_audit(self.request, atencion, action='A')

      messages.success(
        self.request,
        f"Atención creada exitosamente para el paciente {atencion.paciente}"
      )

      return atencion

  def form_valid(self, form: AtencionForm) -> HttpResponseRedirect:
    """Handle form validation and saving"""
    context = self.get_context_data()
    formset = context['formset']

    if not formset.is_valid():
      messages.error(self.request, _("Hay errores en el detalle de atención. Por favor, revíselos."))
      return self.form_invalid(form)

    is_valid, error_messages, detalles_validos = self.validate_formset_data(formset)

    if not is_valid:
      for mensaje in error_messages:
        messages.error(self.request, mensaje)
      return self.form_invalid(form)

    try:
      self.save_atencion(form, detalles_validos)
      return HttpResponseRedirect(self.success_url)
    except Exception as e:
      messages.error(self.request, f"Error al guardar la atención: {str(e)}")
      return self.form_invalid(form)

  def get_context_data(self, **kwargs) -> Dict[str, Any]:
    """Prepare context data for the template"""
    context = super().get_context_data(**kwargs)
    context.update({
      'back_url': self.success_url,
      'title1': 'Crear Atención',
      'grabar': 'Grabar Atención',
      'formset': DetalleAtencionFormsetCreate(
        self.request.POST if self.request.POST else None,
        instance=self.object
      ),
      'medicamentos': Medicamento.objects.filter(activo=True)
    })
    return context


class AtencionUpdateView(UpdateView):
  model = Atencion
  form_class = AtencionForm
  template_name = "attention/atencion/formUpdate.html"
  success_url = reverse_lazy("attention:atencion_list")

  def validate_formset_data(self, formset) -> Tuple[bool, List[str], List[Any], List[Any]]:
    """
    Validates formset data and returns validation status, error messages,
    valid details and items to delete
    """
    error_mensajes: List[str] = []
    detalles_validos: List[Any] = []
    items_to_delete: List[Any] = []

    # Verificar si hay filas vacías no marcadas para eliminar
    for form in formset:
      if form.cleaned_data and not form.cleaned_data.get("DELETE"):
        if self._is_empty_row(form.cleaned_data):
          error_mensajes.append(_("No se permiten filas vacías. Complete todos los campos o elimine la fila."))
          return False, error_mensajes, [], []

    # Obtener medicamentos ya utilizados en esta atención
    medicamentos_usados = self._get_existing_medications()
    medicamentos_en_formset: Set[int] = set()

    for form in formset:
      if not form.cleaned_data:
        continue

      if form.cleaned_data.get("DELETE"):
        if form.instance.pk:
          items_to_delete.append(form.instance)
        continue

      try:
        instance = form.save(commit=False)
        is_valid, error = self._validate_detail(
          instance,
          medicamentos_usados,
          medicamentos_en_formset
        )

        if not is_valid:
          error_mensajes.append(error)
          continue

        medicamentos_en_formset.add(instance.medicamento.pk)
        detalles_validos.append(instance)

      except ValidationError as e:
        error_mensajes.extend(e.messages)

    return not bool(error_mensajes), error_mensajes, detalles_validos, items_to_delete

  def _is_empty_row(self, cleaned_data: Dict) -> bool:
    """Check if a form row is empty"""
    relevant_fields = ['medicamento', 'cantidad', 'prescripcion', 'duracion_tratamiento']
    return not any(cleaned_data.get(field) for field in relevant_fields)

  def _get_existing_medications(self) -> Set[int]:
    """Get set of medications already used in this attention"""
    return set(
      DetalleAtencion.objects.filter(atencion=self.object)
      .exclude(pk=self.object.pk)  # Excluir el registro actual
      .values_list('medicamento', flat=True)
    )

  def _validate_detail(
    self,
    instance: DetalleAtencion,
    medicamentos_usados: Set[int],
    medicamentos_en_formset: Set[int]
  ) -> Tuple[bool, str]:
    """Validate a single detail instance"""
    medicamento = instance.medicamento

    # Validar duplicados, excluyendo la instancia actual
    if medicamento.pk in medicamentos_usados and not instance.pk:
      return False, f"El medicamento {medicamento.nombre} ya ha sido añadido en esta atención."

    if medicamento.pk in medicamentos_en_formset and not instance.pk:
      return False, f"El medicamento {medicamento.nombre} ya ha sido añadido en esta atención."

    # Calcular diferencia de cantidad
    cantidad_inicial = 0
    if instance.pk:
      detalle_original = DetalleAtencion.objects.get(pk=instance.pk)
      cantidad_inicial = detalle_original.cantidad

    cantidad_diferencia = instance.cantidad - cantidad_inicial

    # Validar cantidad
    if cantidad_diferencia > medicamento.cantidad:
      return False, (
        f"No se puede actualizar porque la cantidad de {medicamento.nombre} "
        f"almacenada ({medicamento.cantidad}) es inferior a la cantidad "
        f"solicitada ({cantidad_diferencia} adicionales)."
      )

    if instance.cantidad <= 0:
      return False, "La cantidad no puede ser cero o negativa."

    return True, ""

  def _process_deletions(self, items_to_delete: List[DetalleAtencion]) -> None:
    """Process items marked for deletion"""
    for obj in items_to_delete:
      medicamento = obj.medicamento
      medicamento.cantidad += obj.cantidad
      medicamento.save()
      obj.delete()

  def _save_valid_details(self, detalles_validos: List[DetalleAtencion]) -> None:
    """Save valid details and update inventory"""
    for instance in detalles_validos:
      cantidad_inicial = 0
      if instance.pk:
        detalle_original = DetalleAtencion.objects.get(pk=instance.pk)
        cantidad_inicial = detalle_original.cantidad

      cantidad_diferencia = instance.cantidad - cantidad_inicial

      # Actualizar inventario
      medicamento = instance.medicamento
      medicamento.cantidad -= cantidad_diferencia
      medicamento.save()

      # Guardar detalle
      instance.atencion = self.object
      instance.save()

  def form_valid(self, form):
    context = self.get_context_data()
    formset = context['formset']

    # Guardar los IDs de las filas que fueron marcadas para eliminar
    deleted_forms = []
    if self.request.POST:
      for form_prefix in range(int(self.request.POST.get('detalleatencion_set-TOTAL_FORMS', 0))):
        delete_field = f'detalleatencion_set-{form_prefix}-DELETE'
        if self.request.POST.get(delete_field):
          deleted_forms.append(form_prefix)

    # Validación del formset
    if not formset.is_valid():
      self._handle_formset_errors(formset)
      return self.form_invalid(form)

    is_valid, error_messages, detalles_validos, items_to_delete = self.validate_formset_data(formset)

    # Nueva validación para impedir guardado si no hay detalles de atención
    if not detalles_validos:
      messages.error(self.request, "Debe incluir al menos un detalle de atención para guardar.")
      return self.form_invalid(form)

    if not is_valid:
      for mensaje in error_messages:
        messages.error(self.request, mensaje)
      return self.form_invalid(form)

    try:
      with transaction.atomic():
        self.object = form.save()
        self._process_deletions(items_to_delete)
        self._save_valid_details(detalles_validos)

        save_audit(self.request, self.object, action='M')
        messages.success(
          self.request,
          f"Atención actualizada exitosamente para el paciente {self.object.paciente}"
        )
        return HttpResponseRedirect(self.success_url)

    except Exception as ex:
      messages.error(self.request, f"Error al actualizar la atención: {str(ex)}")
      return self.form_invalid(form)

  def _handle_formset_errors(self, formset) -> None:
    """Handle and display formset errors"""
    for form in formset:
      for field, errors in form.errors.items():
        for error in errors:
          messages.error(self.request, f"Error en {field}: {error}")

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    if self.request.POST:
      context['formset'] = DetalleAtencionFormset(
        self.request.POST,
        instance=self.object
      )
    else:
      # Crear el formset solo con instancias existentes y no generar filas vacías automáticamente
      context['formset'] = DetalleAtencionFormset(
        instance=self.object,
        queryset=DetalleAtencion.objects.filter(atencion=self.object).exclude(
          pk__in=self.request.POST.getlist('deleted_pks'))
      )

    context.update({
      'title1': 'Actualizar Atención',
      'grabar': 'Actualizar Atención',
      'back_url': self.success_url
    })
    return context


class AtencionDeleteView(DeleteView):
  model = Atencion
  success_url = reverse_lazy("attention:atencion_list")

  def delete(self, request, *args, **kwargs):
    self.object = self.get_object()
    if self.object.tiene_relaciones:  # related name
      messages.error(self.request, "No se puede eliminar esta Atención Médica porque está en uso.")
      return redirect(self.success_url)  # Retorna a la misma página sin eliminar

    success_message = f"Éxito al eliminar lógicamente esta Atencion Médica {self.object.paciente}."
    messages.success(self.request, success_message)
    return super().delete(request, *args, **kwargs)


class AtencionDetailView(DetailView):
  model = Atencion

  # Vista AtencionDetailView corregida
  def get(self, request, *args, **kwargs):
    atencion = self.get_object()
    try:
      data = {
        'id': atencion.id,
        'fecha_atencion': atencion.fecha_atencion.strftime('%Y-%m-%d'),
        'motivo_consulta': atencion.motivo_consulta,
        'tratamiento': atencion.tratamiento,
        'comentario': atencion.comentario or "",
        'diagnostico': [diagnostico.codigo + " " + diagnostico.descripcion for diagnostico in
                        atencion.diagnostico.all()],
        'paciente': {
          'id': atencion.paciente.id,
          'paciente': atencion.paciente.nombre_completo,
          'cedula': atencion.paciente.cedula,
          'email': atencion.paciente.email or "",
          'sexo': atencion.paciente.sexo,
          'fecha_nacimiento': atencion.paciente.fecha_nacimiento.isoformat() if atencion.paciente.fecha_nacimiento else None,
          'edad': atencion.paciente.calcular_edad(atencion.paciente.fecha_nacimiento),
          'foto': atencion.paciente.get_image() if atencion.paciente.foto else '/static/img/paciente_avatar.png',
        },
        'detalles': []
      }

      # Agregar detalles de medicamentos recetados
      for detalle in atencion.atenciones.all():
        medicamento = detalle.medicamento
        detalle_data = {
          'medicamento': {
            'id': medicamento.id,
            'nombre': medicamento.nombre,
            'concentracion': medicamento.concentracion,
            'descripcion': medicamento.descripcion,
            'precio': float(medicamento.precio),
            'imagen': medicamento.get_image() or '/static/img/default_medicamento.png',
          },
          'cantidad': detalle.cantidad,
          'prescripcion': detalle.prescripcion,
          'duracion_tratamiento': detalle.duracion_tratamiento
        }
        data['detalles'].append(detalle_data)

      return JsonResponse(data)

    except Exception as e:
      return JsonResponse({'error': str(e)}, status=500)

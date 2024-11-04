from django.contrib import messages
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView

from aplication.attention.forms.atencion import AtencionForm, DetalleAtencionFormset
from aplication.attention.models import Atencion, DetalleAtencion
from aplication.core.models import Medicamento
from doctor.utils import save_audit


# ListView para mostrar todas las atenciones médicas
class AtencionListView(ListView):
  model = Atencion
  template_name = "attention/atencion/list.html"
  context_object_name = "atenciones"
  paginate_by = 5

  def get_queryset(self):
    self.query = Q()
    q1 = self.request.GET.get('q')  # Término de búsqueda general

    if q1:
      # Busca en los campos del modelo Paciente relacionados con la atención
      self.query.add(Q(paciente__nombres__icontains=q1), Q.OR)
      self.query.add(Q(paciente__apellidos__icontains=q1), Q.OR)
      self.query.add(Q(paciente__cedula__icontains=q1), Q.OR)

      # Busca en el modelo Diagnostico relacionado con la atención
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

  def form_valid(self, form):
    context = self.get_context_data()
    formset = context['formset']

    if formset.is_valid():
      detalles_validos = []
      error_ocurrido = False
      error_mensajes = []

      # Primero validamos las cantidades de medicamentos
      for detalle in formset.save(commit=False):
        medicamento = detalle.medicamento
        if detalle.cantidad > medicamento.cantidad:
          error_mensajes.append(
            f"No se puede crear la atención porque la cantidad de {medicamento.nombre} almacenada es inferior a la cantidad solicitada."
          )
          error_ocurrido = True
        elif detalle.cantidad <= 0:
          error_mensajes.append('La cantidad no puede ser CERO o negativa.')
          error_ocurrido = True
        else:
          detalles_validos.append(detalle)

      # Si ocurrió un error, mostrar los mensajes y retornar form_invalid
      if error_ocurrido:
        for mensaje in error_mensajes:
          messages.error(self.request, mensaje)
        return self.form_invalid(form)

      # Si todo es válido, guardamos en una transacción
      with transaction.atomic():
        atencion = form.save()
        for detalle in detalles_validos:
          medicamento.cantidad -= detalle.cantidad
          medicamento.save()  # Actualiza la cantidad en el medicamento
          detalle.atencion = atencion  # Asigna la atención al detalle
          detalle.save()  # Guarda el detalle

        # Auditoría después de guardar la atención y detalles
        save_audit(self.request, atencion, action='A')
        messages.success(self.request, f"Éxito al crear la atención para el paciente {atencion.paciente}.")
        return HttpResponseRedirect(self.success_url)
    else:
      return self.form_invalid(form)

  def get_context_data(self, **kwargs):
    data = super().get_context_data(**kwargs)
    data['back_url'] = self.success_url
    data['title1'] = 'Crear Atención'
    data['grabar'] = 'Grabar Atención'
    if self.request.POST:
      data['formset'] = DetalleAtencionFormset(self.request.POST)
    else:
      data['formset'] = DetalleAtencionFormset(queryset=self.model.objects.none())
    data['medicamentos'] = Medicamento.objects.filter(activo=True)
    return data


# class AtencionUpdateView(UpdateView):
#   model = Atencion
#   form_class = AtencionForm
#   template_name = "attention/atencion/formUpdate.html"
#   success_url = reverse_lazy("attention:atencion_list")
#
#   def form_valid(self, form):
#     context = self.get_context_data()
#     formset = context['formset']
#
#     if formset.is_valid():
#       try:
#         with transaction.atomic():
#           self.object = form.save()
#
#           # Procesamos el formset
#           instances = formset.save(commit=False)
#
#           # Eliminamos los registros marcados
#           for obj in formset.deleted_objects:
#             obj.delete()
#
#           # Guardamos los nuevos o actualizados
#           for instance in instances:
#             instance.atencion = self.object
#             instance.save()
#
#           messages.success(self.request, "Atención actualizada exitosamente.")
#           return HttpResponseRedirect(self.success_url)
#       except Exception as ex:
#         messages.error(self.request, f"Error al actualizar la atención: {ex}")
#         return self.form_invalid(form)
#     else:
#       messages.error(self.request, "Error en el formulario de detalles.")
#       return self.form_invalid(form)
#
#   def get_context_data(self, **kwargs):
#     data = super().get_context_data(**kwargs)
#     if self.request.POST:
#       data['formset'] = DetalleAtencionFormset(
#         self.request.POST,
#         instance=self.object
#       )
#     else:
#       data['formset'] = DetalleAtencionFormset(
#         instance=self.object
#       )
#     data['title1'] = 'Actualizar Atención'
#     data['grabar'] = 'Actualizar Atención'
#     data['back_url'] = self.success_url
#     return data

class AtencionUpdateView(UpdateView):
  model = Atencion
  form_class = AtencionForm
  template_name = "attention/atencion/formUpdate.html"
  success_url = reverse_lazy("attention:atencion_list")

  def form_valid(self, form):
    context = self.get_context_data()
    formset = context['formset']

    if formset.is_valid():
      try:
        with transaction.atomic():
          self.object = form.save()

          # Procesar las filas del formset
          instances = formset.save(commit=False)
          error_ocurrido = False
          error_mensajes = []

          for instance in instances:
            # Recupera el medicamento y cantidad inicial antes de cualquier modificación
            medicamento = instance.medicamento
            if instance.pk:  # Solo si ya existe en la base de datos
              detalle_original = DetalleAtencion.objects.get(pk=instance.pk)
              cantidad_inicial = detalle_original.cantidad
            else:
              cantidad_inicial = 0  # Si es una fila nueva

            # Calcula la diferencia en cantidad
            cantidad_diferencia = instance.cantidad - cantidad_inicial

            # Validación de cantidades
            if cantidad_diferencia > medicamento.cantidad:
              error_mensajes.append(
                f"No se puede actualizar porque la cantidad de {medicamento.nombre} almacenada es inferior a la cantidad solicitada."
              )
              error_ocurrido = True
            elif instance.cantidad <= 0:
              error_mensajes.append('La cantidad no puede ser CERO o negativa.')
              error_ocurrido = True
            else:
              # Ajusta la cantidad en el inventario de medicamentos
              medicamento.cantidad -= cantidad_diferencia
              medicamento.save()
              instance.atencion = self.object
              instance.save()

          # Procesar eliminaciones de filas
          for obj in formset.deleted_objects:
            medicamento = obj.medicamento
            medicamento.cantidad += obj.cantidad  # Devolver la cantidad al inventario
            medicamento.save()
            obj.delete()

          # Manejar errores de cantidad en el formulario de detalles
          if error_ocurrido:
            for mensaje in error_mensajes:
              messages.error(self.request, mensaje)
            return self.form_invalid(form)

            # Guardar auditoría y mensaje de éxito después de la actualización exitosa
          save_audit(self.request, self.object, action='M')
          messages.success(self.request, f"Éxito al modificar la atención para el paciente {self.object.paciente}.")
        return HttpResponseRedirect(self.success_url)
      except Exception as ex:
        messages.error(self.request, f"Error al actualizar la atención: {ex}")
        return self.form_invalid(form)
    else:
      messages.error(self.request, "Error en el formulario de detalles.")
      return self.form_invalid(form)

  def get_context_data(self, **kwargs):
    data = super().get_context_data(**kwargs)
    if self.request.POST:
      data['formset'] = DetalleAtencionFormset(self.request.POST, instance=self.object)
    else:
      data['formset'] = DetalleAtencionFormset(instance=self.object)
    data['title1'] = 'Actualizar Atención'
    data['grabar'] = 'Actualizar Atención'
    data['back_url'] = self.success_url
    return data


# DeleteView para eliminar una atención médica
class AtencionDeleteView(DeleteView):
  model = Atencion
  success_url = reverse_lazy("attention:atencion_list")

  def delete(self, request, *args, **kwargs):
    self.object = self.get_object()
    messages.success(request, "Atención eliminada exitosamente.")
    return super().delete(request, *args, **kwargs)


# DetailView para consultar o ver los detalles de una atención médica
class AtencionDetailView(DetailView):
  model = Atencion

  # Vista AtencionDetailView corregida
  def get(self, request, *args, **kwargs):
    atencion = self.get_object()
    try:
        data = {
            'id': atencion.id,
            'fecha_atencion': atencion.fecha_atencion.strftime('%Y-%m-%d') ,
            'motivo_consulta': atencion.motivo_consulta,
            'tratamiento': atencion.tratamiento,
            'comentario': atencion.comentario or "",
            'diagnostico': [diagnostico.codigo for diagnostico in atencion.diagnostico.all()],
            'paciente': {
                'id': atencion.paciente.id,
                'nombres': atencion.paciente.nombres,
                'apellidos': atencion.paciente.apellidos,
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


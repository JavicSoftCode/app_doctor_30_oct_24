from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView, DeleteView, DetailView
from django.shortcuts import redirect
from aplication.core.forms.medicineType import MedicineTypeForm
from aplication.core.models import TipoMedicamento
from doctor.utils import save_audit


class MedicineTypeListView(ListView):
  template_name = "core/medicineType/list.html"
  model = TipoMedicamento
  context_object_name = 'tipos_medicina'
  paginate_by = 5
  query = None

  def get_queryset(self):
    self.query = Q()
    q1 = self.request.GET.get('q')
    specialty = self.request.GET.get('tipoMedicina')

    if q1:
      if q1.isdigit():
        self.query.add(Q(id=q1), Q.AND)
      else:
        self.query.add(Q(nombre__icontains=q1), Q.AND)

    if specialty in ["True", "False"]:
      is_active = specialty == "True"
      self.query.add(Q(activo=is_active), Q.AND)

    return self.model.objects.filter(self.query).order_by('nombre')

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context['title1'] = "Listado Tipos de Medicamentos"
    context['title2'] = "Nuevo Tipo de Medicamento"
    return context


class MedicineTypeCreateView(CreateView):
  model = TipoMedicamento
  template_name = 'core/medicineType/form.html'
  form_class = MedicineTypeForm
  success_url = reverse_lazy('core:medicineType_list')

  def get_context_data(self, **kwargs):
    context = super().get_context_data()
    context['title1'] = 'Crear Tipo de Medicamento'
    context['grabar'] = 'Grabar Tipo de Medicamento'
    context['back_url'] = self.success_url
    return context

  def form_valid(self, form):
    response = super().form_valid(form)
    objAudit = self.object
    save_audit(self.request, objAudit, action='A')
    messages.success(self.request, f"Éxito al Crear el Tipo Medicamento {objAudit.nombre}.")
    return response

  def form_invalid(self, form):
    messages.error(self.request, "Error al enviar el formulario. Corrige los errores.")
    print(form.errors)
    return self.render_to_response(self.get_context_data(form=form))


class MedicineTypeUpdateView(UpdateView):
  model = TipoMedicamento
  template_name = 'core/medicineType/form.html'
  form_class = MedicineTypeForm
  success_url = reverse_lazy('core:medicineType_list')

  def get_context_data(self, **kwargs):
    context = super().get_context_data()
    context['title1'] = 'Actualizar Tipo de Medicamento'
    context['grabar'] = 'Actualizar Tipo de Medicamento'
    context['back_url'] = self.success_url
    return context

  def form_valid(self, form):
    response = super().form_valid(form)
    objAudit = self.object
    save_audit(self.request, objAudit, action='M')
    messages.success(self.request, f"Éxito al Modificar el Tipo Medicamento {objAudit.nombre}.")
    return response

  def form_invalid(self, form):
    messages.error(self.request, "Error al Modificar el formulario. Corrige los errores.")
    print(form.errors)
    return self.render_to_response(self.get_context_data(form=form))


class MedicineTypeDeleteView(DeleteView):
  model = TipoMedicamento
  success_url = reverse_lazy('core:medicineType_list')

  def get_context_data(self, **kwargs):
    context = super().get_context_data()
    context['grabar'] = 'Eliminar Tipo de Medicamento'
    context['description'] = f"¿Desea Eliminar el Tipo de Medicamento: {self.object.nombre}?"
    return context

  def delete(self, request, *args, **kwargs):
    self.object = self.get_object()
    if self.object.tiene_relaciones.exists():
      messages.error(self.request, "No se puede eliminar el tipo medicamento porque está en uso.")
      return redirect(self.success_url)

    success_message = f"Éxito al eliminar lógicamente el Tipo Medicamento {self.object.nombre}."
    messages.success(self.request, success_message)
    return super().delete(request, *args, **kwargs)


class MedicineTypeDetailView(DetailView):
  model = TipoMedicamento
  extra_context = {
    "detail": "Detalles del Tipo de Medicamento"
  }

  def get(self, request, *args, **kwargs):
    medicineType = self.get_object()
    data = {
      'id': medicineType.id,
      'nombre': medicineType.nombre,
      'descripcion': medicineType.descripcion,
      'activo': medicineType.activo,
    }
    return JsonResponse(data)

from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView, DeleteView, DetailView

from aplication.core.forms.marcaMedicamento import MarcaMedicamentoForm
from aplication.core.models import MarcaMedicamento
from doctor.utils import save_audit


class MarcaMedicamentoListView(ListView):
  template_name = "core/marcaMedicamento/list.html"
  model = MarcaMedicamento
  context_object_name = 'marcas'
  paginate_by = 5
  query = None

  def get_queryset(self):
    self.query = Q()
    q1 = self.request.GET.get('q')  # Texto de búsqueda
    activo = self.request.GET.get('activo')  # Estado activo o inactivo

    if q1:
      if q1.isdigit():
        self.query.add(Q(id=q1), Q.AND)

      else:
        # Filtra por nombre que contenga el valor ingresado en 'q'
        self.query.add(Q(nombre__icontains=q1), Q.AND)

    if activo in ["True", "False"]:
      # Filtra por el valor booleano de activo
      is_active = activo == "True"  # Convierte a booleano
      self.query.add(Q(activo=is_active), Q.AND)

    return self.model.objects.filter(self.query).order_by('nombre')

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context['title1'] = "Listado de Marcas de Medicamentos"
    context['title2'] = "Nueva Marca de Medicamento"
    return context


class MarcaMedicamentoCreateView(CreateView):
  model = MarcaMedicamento
  template_name = 'core/marcaMedicamento/form.html'
  form_class = MarcaMedicamentoForm
  success_url = reverse_lazy('core:marcaMedicamento_list')

  def get_context_data(self, **kwargs):
    context = super().get_context_data()
    context['title1'] = 'Crear Marca Medicamento'
    context['grabar'] = 'Grabar Marca Medicamento'
    context['back_url'] = self.success_url
    return context

  def form_valid(self, form):
    # print("entro al form_valid")
    response = super().form_valid(form)
    marcaM = self.object
    save_audit(self.request, marcaM, action='A')
    messages.success(self.request, f"Éxito al crear la Marca Medicamento {marcaM.nombre}.")
    return response

  def form_invalid(self, form):
    messages.error(self.request, "Error al enviar el formulario. Corrige los errores.")
    print(form.errors)
    return self.render_to_response(self.get_context_data(form=form))


class MarcaMedicamentoUpdateView(UpdateView):
  model = MarcaMedicamento
  template_name = 'core/marcaMedicamento/form.html'
  form_class = MarcaMedicamentoForm
  success_url = reverse_lazy('core:marcaMedicamento_list')

  def get_context_data(self, **kwargs):
    context = super().get_context_data()
    context['title1'] = 'Actualizar Marca Medicamento'
    context['grabar'] = 'Actualizar Marca Medicamento'
    context['back_url'] = self.success_url
    return context

  def form_valid(self, form):
    response = super().form_valid(form)
    marcaM = self.object
    save_audit(self.request, marcaM, action='M')
    messages.success(self.request, f"Éxito al Modificar la Marca Medicamento {marcaM.nombre}.")
    print("mande mensaje")
    return response

  def form_invalid(self, form):
    messages.error(self.request, "Error al Modificar el formulario. Corrige los errores.")
    print(form.errors)
    return self.render_to_response(self.get_context_data(form=form))


class MarcaMedicamentoDeleteView(DeleteView):
  model = MarcaMedicamento
  success_url = reverse_lazy('core:marcaMedicamento_list')

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context['grabar'] = 'Eliminar Marca Medicamento'
    context['description'] = f"¿Desea Eliminar la Marca Medicamento: {self.object.nombre}?"
    return context

  def delete(self, request, *args, **kwargs):
    self.object = self.get_object()
    specialty_name = self.object.nombre  # Guardamos el nombre de la
    # Guarda la auditoría de la eliminación
    save_audit(self.request, self.object, action='E')

    success_message = f"Éxito al eliminar lógicamente la Marca Medicamento {specialty_name}."
    messages.success(self.request, success_message)

    # Cambiar el estado de eliminado lógico (si es necesario)
    # self.object.deleted = True
    # self.object.save()

    return super().delete(request, *args, **kwargs)


# class SpecialtyDeleteView(DeleteView):
#   model = Especialidad
#   success_url = reverse_lazy('core:specialty_list')
#
#   def get_context_data(self, **kwargs):
#     context = super().get_context_data()
#     context['grabar'] = 'Eliminar Especialidad'
#     context['description'] = f"¿Desea Eliminar la Especialidad: {self.object.nombre}?"
#     return context
#
#   def delete(self, request, *args, **kwargs):
#     self.object = self.get_object()
#     success_message = f"Éxito al eliminar lógicamente la Especialidad {self.object.nombre}."
#     messages.success(self.request, success_message)
#     # Cambiar el estado de eliminado lógico
#     # self.object.deleted = True
#     # self.object.save()
#     return super().delete(request, *args, **kwargs)


class MarcaMedicamentoDetailView(DetailView):
  model = MarcaMedicamento
  extra_context = {
    "detail": "Detalles de la Marca Medicamento"
  }

  def get(self, request, *args, **kwargs):
    marcaM = self.get_object()
    data = {
      'id': marcaM.id,
      'nombre': marcaM.nombre,
      'descripcion': marcaM.descripcion,
      'activo': marcaM.activo,
    }
    return JsonResponse(data)

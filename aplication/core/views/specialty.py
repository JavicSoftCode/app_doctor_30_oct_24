from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView, DeleteView, DetailView

from aplication.core.forms.specialty import SpecialtyForm
from aplication.core.models import Especialidad
from doctor.utils import save_audit


class SpecialtyListView(ListView):
  template_name = "core/specialty/list.html"
  model = Especialidad
  context_object_name = 'especialidades'
  paginate_by = 5
  query = None

  def get_queryset(self):
    self.query = Q()
    q1 = self.request.GET.get('q')  # Texto de búsqueda
    specialty = self.request.GET.get('especialidad')  # Estado activo o inactivo

    if q1:
      # Filtra por nombre que contenga el valor ingresado en 'q'
      self.query.add(Q(nombre__icontains=q1), Q.AND)

    if specialty in ["True", "False"]:
      # Filtra por el valor booleano de activo
      is_active = specialty == "True"  # Convierte a booleano
      self.query.add(Q(activo=is_active), Q.AND)

    return self.model.objects.filter(self.query).order_by('nombre')

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context['title1'] = "Listado de Especialidades"
    context['title2'] = "Nueva Especialidad"
    return context


class SpecialtyCreateView(CreateView):
  model = Especialidad
  template_name = 'core/specialty/form.html'
  form_class = SpecialtyForm
  success_url = reverse_lazy('core:specialty_list')

  def get_context_data(self, **kwargs):
    context = super().get_context_data()
    context['title1'] = 'Crear Especialidad'
    context['grabar'] = 'Grabar Especialidad'
    context['back_url'] = self.success_url
    return context

  def form_valid(self, form):
    # print("entro al form_valid")
    response = super().form_valid(form)
    specialty = self.object
    save_audit(self.request, specialty, action='A')
    messages.success(self.request, f"Éxito al crear la Especialidad {specialty.nombre}.")
    return response

  def form_invalid(self, form):
    messages.error(self.request, "Error al enviar el formulario. Corrige los errores.")
    print(form.errors)
    return self.render_to_response(self.get_context_data(form=form))


class SpecialtyUpdateView(UpdateView):
  model = Especialidad
  template_name = 'core/specialty/form.html'
  form_class = SpecialtyForm
  success_url = reverse_lazy('core:specialty_list')

  def get_context_data(self, **kwargs):
    context = super().get_context_data()
    context['title1'] = 'Actualizar Especialidad'
    context['grabar'] = 'Actualizar Especialidad'
    context['back_url'] = self.success_url
    return context

  def form_valid(self, form):
    response = super().form_valid(form)
    specialty = self.object
    save_audit(self.request, specialty, action='M')
    messages.success(self.request, f"Éxito al Modificar la Especialidad {specialty.nombre}.")
    print("mande mensaje")
    return response

  def form_invalid(self, form):
    messages.error(self.request, "Error al Modificar el formulario. Corrige los errores.")
    print(form.errors)
    return self.render_to_response(self.get_context_data(form=form))


class SpecialtyDeleteView(DeleteView):
  model = Especialidad
  success_url = reverse_lazy('core:specialty_list')

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context['grabar'] = 'Eliminar Especialidad'
    context['description'] = f"¿Desea Eliminar la Especialidad: {self.object.nombre}?"
    return context

  def delete(self, request, *args, **kwargs):
    self.object = self.get_object()
    specialty_name = self.object.nombre  # Guardamos el nombre de la especialidad
    # Guarda la auditoría de la eliminación
    save_audit(self.request, self.object, action='E')

    success_message = f"Éxito al eliminar lógicamente la Especialidad {specialty_name}."
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


class SpecialtyDetailView(DetailView):
  model = Especialidad
  extra_context = {
    "detail": "Detalles de la Especialidad"
  }

  def get(self, request, *args, **kwargs):
    specialty = self.get_object()
    data = {
      'id': specialty.id,
      'nombre': specialty.nombre,
      'descripcion': specialty.descripcion,
      'activo': specialty.activo,
    }
    return JsonResponse(data)

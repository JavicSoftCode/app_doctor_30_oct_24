from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView, DeleteView, DetailView

from aplication.attention.forms.serviciosAdicionales import ServiciosAdicionalesForm
from aplication.attention.models import ServiciosAdicionales
from doctor.utils import save_audit


class ServiciosAdicionalesListView(ListView):
  template_name = "attention/serviciosAdicionales/list.html"
  model = ServiciosAdicionales
  context_object_name = 'servicios'
  paginate_by = 5
  query = None

  def get_queryset(self):
    self.query = Q()
    q1 = self.request.GET.get('q')  # Texto de búsqueda
    specialty = self.request.GET.get('estado')  # Estado activo o inactivo

    if q1:
      if q1.isdigit():
        self.query.add(Q(id=q1), Q.AND)

      else:
        # Filtra por nombre que contenga el valor ingresado en 'q'
        self.query.add(Q(nombre_servicio__icontains=q1), Q.AND)

    if specialty in ["True", "False"]:
      # Filtra por el valor booleano de activo
      is_active = specialty == "True"  # Convierte a booleano
      self.query.add(Q(activo=is_active), Q.AND)

    return self.model.objects.filter(self.query).order_by('nombre_servicio')

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context['title1'] = "Listado de Servicios Adicionales"
    context['title2'] = "Nuevo Servicio Adicional"
    return context


class ServiciosAdicionalesCreateView(CreateView):
  model = ServiciosAdicionales
  template_name = 'attention/serviciosAdicionales/form.html'
  form_class = ServiciosAdicionalesForm
  success_url = reverse_lazy('attention:serviciosAdicionales_list')

  def get_context_data(self, **kwargs):
    context = super().get_context_data()
    context['title1'] = 'Crear Servicio Adicional'
    context['grabar'] = 'Grabar Servicio Adicional'
    context['back_url'] = self.success_url
    return context

  def form_valid(self, form):
    # print("entro al form_valid")
    response = super().form_valid(form)
    servicioAdd = self.object
    save_audit(self.request, servicioAdd, action='A')
    messages.success(self.request, f"Éxito al crear el Servicio Adicional {servicioAdd.nombre_servicio}.")
    return response

  def form_invalid(self, form):
    messages.error(self.request, "Error al enviar el formulario. Corrige los errores.")
    print(form.errors)
    return self.render_to_response(self.get_context_data(form=form))


class ServiciosAdicionalesUpdateView(UpdateView):
  model = ServiciosAdicionales
  template_name = 'attention/serviciosAdicionales/form.html'
  form_class = ServiciosAdicionalesForm
  success_url = reverse_lazy('attention:serviciosAdicionales_list')

  def get_context_data(self, **kwargs):
    context = super().get_context_data()
    context['title1'] = 'Actualizar Servicio Adicional'
    context['grabar'] = 'Actualizar Servicio Adicional'
    context['back_url'] = self.success_url
    return context

  def form_valid(self, form):
    response = super().form_valid(form)
    servicioAdd = self.object
    save_audit(self.request, servicioAdd, action='M')
    messages.success(self.request, f"Éxito al Modificar el Servicio Adicional {servicioAdd.nombre_servicio}.")
    print("mande mensaje")
    return response

  def form_invalid(self, form):
    messages.error(self.request, "Error al Modificar el formulario. Corrige los errores.")
    print(form.errors)
    return self.render_to_response(self.get_context_data(form=form))


class ServiciosAdicionalesDeleteView(DeleteView):
  model = ServiciosAdicionales
  success_url = reverse_lazy('attention:serviciosAdicionales_list')

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context['grabar'] = 'Eliminar Servicio Adicional'
    context['description'] = f"¿Desea Eliminar la Servicio Adicional: {self.object.nombre_servicio}?"
    return context

  def delete(self, request, *args, **kwargs):
    self.object = self.get_object()
    servicio = self.object.nombre  # Guardamos el nombre de la especialidad
    # Guarda la auditoría de la eliminación
    save_audit(self.request, self.object, action='E')

    success_message = f"Éxito al eliminar lógicamente el Servicio Adicional {servicio}."
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


class ServiciosAdicionalesDetailView(DetailView):
  model = ServiciosAdicionales
  extra_context = {
    "detail": "Detalles del Servicio Adicional"
  }

  def get(self, request, *args, **kwargs):
    servicioAdd = self.get_object()
    data = {
      'id': servicioAdd.id,
      'nombre_servicio': servicioAdd.nombre_servicio,
      'costo_servicio': servicioAdd.costo_servicio,
      'descripcion': servicioAdd.descripcion,
      'activo': servicioAdd.activo,
    }
    return JsonResponse(data)

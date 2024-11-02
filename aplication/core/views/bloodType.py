from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView, DeleteView, DetailView

from aplication.core.forms.bloodType import BloodTypeForm
from aplication.core.models import TipoSangre
from doctor.utils import save_audit


class BloodTypeListView(ListView):
  template_name = "core/bloodType/list.html"
  model = TipoSangre
  context_object_name = 'tipos_sangre'
  paginate_by = 5
  query = None

  def get_queryset(self):
    self.query = Q()
    q1 = self.request.GET.get('q')  # ver
    tipoSangre = self.request.GET.get('tip')
    if q1 is not None:
      self.query.add(Q(tipo__icontains=q1), Q.OR)
    if tipoSangre == "+" or tipoSangre == "-": self.query.add(Q(tipo__icontains=tipoSangre), Q.AND)
    return self.model.objects.filter(self.query).order_by('tipo')

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context['title1'] = "Listado Tipos de Sangre"
    context['title2'] = "Nuevo Tipo de Sangre"
    return context


class BloodTypeCreateView(CreateView):
  model = TipoSangre
  template_name = 'core/bloodType/form.html'
  form_class = BloodTypeForm
  success_url = reverse_lazy('core:bloodType_list')

  def get_context_data(self, **kwargs):
    context = super().get_context_data()
    context['title1'] = 'Crear Tipo de Sangre'
    context['grabar'] = 'Grabar Tipo de Sangre'
    context['back_url'] = self.success_url
    return context

  def form_valid(self, form):
    # print("entro al form_valid")
    response = super().form_valid(form)
    bloodType = self.object
    save_audit(self.request, bloodType, action='A')
    messages.success(self.request, f"Éxito al crear el Tipo de Sangre {bloodType.tipo}.")
    return response

    # def form_valid(self, form):
    #   if hasattr(self.request, 'user') and self.request.user.is_authenticated:
    #     form.instance.usuario = self.request.user
    #   else:
    #     # Asigna un valor alternativo o evita la asignación si el usuario no está autenticado
    #     form.instance.usuario = None  # O el valor que consideres adecuado
    #     messages.success(self.request, f"Éxito al Crear el Tipo de Sangre.")

    # return super().form_valid(form)

  def form_invalid(self, form):
    messages.error(self.request, "Error al enviar el formulario. Corrige los errores.")
    print(form.errors)
    return self.render_to_response(self.get_context_data(form=form))


class BloodTypeUpdateView(UpdateView):
  model = TipoSangre
  template_name = 'core/bloodType/form.html'
  form_class = BloodTypeForm
  success_url = reverse_lazy('core:bloodType_list')

  def get_context_data(self, **kwargs):
    context = super().get_context_data()
    context['title1'] = 'Actualizar Tipo de Sangre'
    context['grabar'] = 'Actualizar Tipo de Sangre'
    context['back_url'] = self.success_url
    return context

  def form_valid(self, form):
    response = super().form_valid(form)
    bloodType = self.object
    save_audit(self.request, bloodType, action='M')
    messages.success(self.request, f"Éxito al Modificar el Tipo de Sangre {bloodType.tipo}.")
    print("mande mensaje")
    return response

  # def form_valid(self, form):
  #   bloodType = self.object
  #   if hasattr(self.request, 'user') and self.request.user.is_authenticated:
  #     form.instance.usuario = self.request.user
  #   else:
  #     # Asigna un valor alternativo o evita la asignación si el usuario no está autenticado
  #     form.instance.usuario = None  # O el valor que consideres adecuado
  #     messages.success(self.request, f"Éxito al Modificar el Tipo de Sangre {bloodType.tipo}.")
  #
  #   return super().form_valid(form)

  def form_invalid(self, form):
    messages.error(self.request, "Error al Modificar el formulario. Corrige los errores.")
    print(form.errors)
    return self.render_to_response(self.get_context_data(form=form))


class BloodTypeDeleteView(DeleteView):
  model = TipoSangre
  success_url = reverse_lazy('core:bloodType_list')

  def get_context_data(self, **kwargs):
    context = super().get_context_data()
    context['grabar'] = 'Eliminar Tipo de Sangre'
    context['description'] = f"¿Desea Eliminar el Tipo de Sangre: {self.object.descripcion}?"
    return context

  def delete(self, request, *args, **kwargs):
    self.object = self.get_object()
    success_message = f"Éxito al eliminar lógicamente el Tipo de Sangre {self.object.descripcion}."
    messages.success(self.request, success_message)
    # Cambiar el estado de eliminado lógico
    # self.object.deleted = True
    # self.object.save()
    return super().delete(request, *args, **kwargs), bloodType


class BloodTypeDetailView(DetailView):
  model = TipoSangre
  extra_context = {
    "detail": "Detalles Tipo Sangre"
  }

  def get(self, request, *args, **kwargs):
    bloodType = self.get_object()
    data = {
      'id': bloodType.id,
      'tipo': bloodType.tipo,
      'descripcion': bloodType.descripcion,
    }
    return JsonResponse(data)

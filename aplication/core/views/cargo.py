from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView, DeleteView, DetailView

from aplication.core.forms.cargo import CargoForm
from aplication.core.models import Cargo
from doctor.utils import save_audit


class CargoListView(ListView):
  template_name = "core/cargo/list.html"
  model = Cargo
  context_object_name = 'cargos'
  paginate_by = 5
  query = None

  def get_queryset(self):
    self.query = Q()
    q1 = self.request.GET.get('q')  # Texto de búsqueda
    cargo = self.request.GET.get('cargo')  # Estado activo o inactivo

    if q1:
      if q1.isdigit():
        self.query.add(Q(id=q1), Q.AND)

      else:
        # Filtra por nombre que contenga el valor ingresado en 'q'
        self.query.add(Q(nombre__icontains=q1), Q.AND)

    if cargo in ["True", "False"]:
      # Filtra por el valor booleano de activo
      is_active = cargo == "True"  # Convierte a booleano
      self.query.add(Q(activo=is_active), Q.AND)

    return self.model.objects.filter(self.query).order_by('nombre')

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context['title1'] = "Listado de Cargos"
    context['title2'] = "Nuevo Cargo"
    return context


class CargoCreateView(CreateView):
  model = Cargo
  template_name = 'core/cargo/form.html'
  form_class = CargoForm
  success_url = reverse_lazy('core:cargo_list')

  def get_context_data(self, **kwargs):
    context = super().get_context_data()
    context['title1'] = 'Crear Cargo'
    context['grabar'] = 'Grabar Cargo'
    context['back_url'] = self.success_url
    return context

  def form_valid(self, form):
    response = super().form_valid(form)
    objAudit = self.object
    save_audit(self.request, objAudit, action='A')
    messages.success(self.request, f"Éxito al Crear el Cargo {objAudit.nombre}.")
    return response

  # def form_valid(self, form):
  #   if hasattr(self.request, 'user') and self.request.user.is_authenticated:
  #     form.instance.usuario = self.request.user
  #   else:
  #     # Asigna un valor alternativo o evita la asignación si el usuario no está autenticado
  #     form.instance.usuario = None  # O el valor que consideres adecuado
  #     messages.success(self.request, f"Éxito al Crear el Cargo.")
  #   return super().form_valid(form)

  def form_invalid(self, form):
    messages.error(self.request, "Error al enviar el formulario. Corrige los errores.")
    print(form.errors)
    return self.render_to_response(self.get_context_data(form=form))


class CargoUpdateView(UpdateView):
  model = Cargo
  template_name = 'core/cargo/form.html'
  form_class = CargoForm
  success_url = reverse_lazy('core:cargo_list')

  def get_context_data(self, **kwargs):
    context = super().get_context_data()
    context['title1'] = 'Actualizar Cargo'
    context['grabar'] = 'Actualizar Cargo'
    context['back_url'] = self.success_url
    return context

  # def form_valid(self, form):
  #   response = super().form_valid(form)
  #   specialty = self.object
  #   save_audit(self.request, specialty, action='M')
  #   messages.success(self.request, f"Éxito al Modificar la Especialidad {specialty.nombre}.")
  #   print("mande mensaje")
  #   return response

  def form_valid(self, form):
    response = super().form_valid(form)
    objAudit = self.object
    save_audit(self.request, objAudit, action='M')
    messages.success(self.request, f"Éxito al Modificar el Cargo {objAudit.nombre}.")
    return response

  # def form_valid(self, form):
  #   cargo = self.object
  #   if hasattr(self.request, 'user') and self.request.user.is_authenticated:
  #     form.instance.usuario = self.request.user
  #   else:
  #     # Asigna un valor alternativo o evita la asignación si el usuario no está autenticado
  #     form.instance.usuario = None  # O el valor que consideres adecuado
  #     messages.success(self.request, f"Éxito al Modificar el Cargo {cargo.nombre}.")
  #
  #   return super().form_valid(form)

  def form_invalid(self, form):
    messages.error(self.request, "Error al Modificar el formulario. Corrige los errores.")
    print(form.errors)
    return self.render_to_response(self.get_context_data(form=form))


class CargoDeleteView(DeleteView):
  model = Cargo
  success_url = reverse_lazy('core:cargo_list')

  def get_context_data(self, **kwargs):
    context = super().get_context_data()
    context['grabar'] = 'Eliminar Cargo'
    context['description'] = f"¿Desea Eliminar el Cargo: {self.object.nombre}?"
    return context

  def delete(self, request, *args, **kwargs):
    self.object = self.get_object()
    if self.object.cargos.exists():  # related name
      messages.error(self.request, "No se puede eliminar el cargo porque está en uso.")
      return self.get(request, *args, **kwargs)  # Retorna a la misma página sin eliminar

    success_message = f"Éxito al eliminar lógicamente el Cargo {self.object.nombre}."
    messages.success(self.request, success_message)
    return super().delete(request, *args, **kwargs)

  # def delete(self, request, *args, **kwargs):
  #   self.object = self.get_object()
  #   success_message = f"Éxito al eliminar lógicamente el Cargo {self.object.nombre}."
  #   messages.success(self.request, success_message)
  #   # Cambiar el estado de eliminado lógico
  #   # self.object.deleted = True
  #   # self.object.save()
  #   return super().delete(request, *args, **kwargs)


class CargoDetailView(DetailView):
  model = Cargo
  extra_context = {
    "detail": "Detalles del Cargo"
  }

  def get(self, request, *args, **kwargs):
    cargo = self.get_object()
    data = {
      'id': cargo.id,
      'nombre': cargo.nombre,
      'descripcion': cargo.descripcion,
      'activo': cargo.activo,
    }
    return JsonResponse(data)

from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from django.templatetags.static import static
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView, DeleteView, DetailView

from aplication.core.forms.empleado import EmpleadoForm
from aplication.core.models import Empleado
from doctor.utils import save_audit


class EmpleadoListView(ListView):
  template_name = "core/empleado/list.html"
  model = Empleado
  context_object_name = 'empleados'
  paginate_by = 5
  query = None

  def get_queryset(self):
    self.query = Q()
    q1 = self.request.GET.get('q')  # ver
    empleado = self.request.GET.get('empleado')
    if q1 is not None:
      self.query.add(Q(nombres__icontains=q1), Q.OR)
      self.query.add(Q(apellidos__icontains=q1), Q.OR)
      self.query.add(Q(cedula__icontains=q1), Q.OR)
      self.query.add(Q(email__icontains=q1), Q.OR)
      if empleado in ["True", "False"]:
        is_active = empleado == "True"  # Convierte a booleano
        self.query.add(Q(activo=is_active), Q.AND)
    return self.model.objects.filter(self.query).order_by('apellidos')

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context['title1'] = "Listado Empleados"
    context['title2'] = "Nuevo Empleado"
    return context


class EmpleadoCreateView(CreateView):
  model = Empleado
  template_name = 'core/empleado/form.html'
  form_class = EmpleadoForm
  success_url = reverse_lazy('core:empleado_list')

  def get_context_data(self, **kwargs):
    context = super().get_context_data()
    context['title1'] = 'Crear Empleado'
    context['grabar'] = 'Grabar Empleado'
    context['default_image_url'] = static('img/avatar_empleado.png')
    # context['default_image_url'] = static('img/doctor_avatar.png')
    context['back_url'] = self.success_url
    return context

  def form_valid(self, form):
    response = super().form_valid(form)
    objAudit = self.object
    save_audit(self.request, objAudit, action='A')
    messages.success(self.request, f"Éxito al Crear al Empleado {objAudit.nombre_completo}.")
    return response

  # def form_valid(self, form):
  #   if hasattr(self.request, 'user') and self.request.user.is_authenticated:
  #     form.instance.usuario = self.request.user
  #   else:
  #     # Asigna un valor alternativo o evita la asignación si el usuario no está autenticado
  #     form.instance.usuario = None  # O el valor que consideres adecuado
  #     messages.success(self.request, f"Éxito al Crear al Empleado.")
  #
  #   return super().form_valid(form)

  def form_invalid(self, form):
    messages.error(self.request, "Error al enviar el formulario. Corrige los errores.")
    print(form.errors)
    return self.render_to_response(self.get_context_data(form=form))


class EmpleadoUpdateView(UpdateView):
  model = Empleado
  template_name = 'core/empleado/form.html'
  form_class = EmpleadoForm
  success_url = reverse_lazy('core:empleado_list')

  def get_context_data(self, **kwargs):
    context = super().get_context_data()
    context['title1'] = 'Actualizar Empleado'
    context['grabar'] = 'Actualizar Empleado'
    # context['default_image_url'] = static('img/doctor_avatar.png')
    context['default_image_url'] = static('img/avatar_empleado.png')
    context['current_image_url'] = self.object.foto.url if self.object.foto else static('img/avatar_empleado.png')
    # context['current_image_url'] = self.object.foto.url if self.object.foto else static('img/doctor_avatar.png')
    context['back_url'] = self.success_url
    return context

  def form_valid(self, form):
    response = super().form_valid(form)
    objAudit = self.object
    save_audit(self.request, objAudit, action='M')
    messages.success(self.request, f"Éxito al Modificar al Empleado {objAudit.nombre_completo}.")
    return response

  # def form_valid(self, form):
  #   empleado = self.object
  #   if hasattr(self.request, 'user') and self.request.user.is_authenticated:
  #     form.instance.usuario = self.request.user
  #   else:
  #     # Asigna un valor alternativo o evita la asignación si el usuario no está autenticado
  #     form.instance.usuario = None  # O el valor que consideres adecuado
  #     messages.success(self.request, f"Éxito al Modificar al Empleado {empleado.nombre_completo}.")
  #
  #   return super().form_valid(form)

  def form_invalid(self, form):
    messages.error(self.request, "Error al Modificar el formulario. Corrige los errores.")
    print(form.errors)
    return self.render_to_response(self.get_context_data(form=form))


class EmpleadoDeleteView(DeleteView):
  model = Empleado
  success_url = reverse_lazy('core:empleado_list')

  def get_context_data(self, **kwargs):
    context = super().get_context_data()
    context['grabar'] = 'Eliminar Empleado'
    context['description'] = f"¿Desea Eliminar al Empleado: {self.object.nombre_completo}?"
    return context

  def delete(self, request, *args, **kwargs):
    self.object = self.get_object()
    success_message = f"Éxito al eliminar lógicamente al Empleado {self.object.nombre_completo}."
    messages.success(self.request, success_message)
    # Cambiar el estado de eliminado lógico
    # self.object.deleted = True
    # self.object.save()
    return super().delete(request, *args, **kwargs)


class EmpleadoDetailView(DetailView):
  model = Empleado
  extra_context = {
    "detail": "Detalles del Empleado"
  }

  def get(self, request, *args, **kwargs):
    empleado = self.get_object()
    data = {
      'id': empleado.id,
      'nombres': empleado.nombres,
      'apellidos': empleado.apellidos,
      'cedula': empleado.cedula,
      'fecha_nacimiento': empleado.fecha_nacimiento.isoformat() if empleado.fecha_nacimiento else None,
      'direccion': empleado.direccion,
      'latitud': str(empleado.latitud) if empleado.latitud is not None else None,
      'longitud': str(empleado.longitud) if empleado.longitud is not None else None,
      'cargo': empleado.cargo.nombre,
      'sueldo': empleado.sueldo,
      'telefonos': empleado.telefonos,
      'email': empleado.email,
      'curriculum': empleado.curriculum.url if empleado.curriculum else None,
      'firma_digital': empleado.firma_digital.url if empleado.firma_digital else None,
      'foto': empleado.get_image(),
      'activo': empleado.activo,
    }
    return JsonResponse(data)

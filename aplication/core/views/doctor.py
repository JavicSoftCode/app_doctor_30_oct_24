import json

from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from django.templatetags.static import static
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView, DeleteView, DetailView

from aplication.core.forms.doctor import DoctorForm
from aplication.core.models import Doctor
from doctor.utils import save_audit


class DoctorListView(ListView):
  template_name = "core/doctor/list.html"
  model = Doctor
  context_object_name = 'doctores'
  paginate_by = 5
  query = None

  def get_queryset(self):
    self.query = Q()
    q1 = self.request.GET.get('q')
    doct = self.request.GET.get('doctor')
    if q1 is not None:
      if q1.isdigit():
        self.query.add(Q(id=q1), Q.AND)

      self.query.add(Q(nombres__icontains=q1), Q.OR)
      self.query.add(Q(apellidos__icontains=q1), Q.OR)
      self.query.add(Q(cedula__icontains=q1), Q.OR)
      self.query.add(Q(codigoUnicoDoctor__icontains=q1), Q.OR)
      self.query.add(Q(email__icontains=q1), Q.OR)
      if doct in ["True", "False"]:
        is_active = doct == "True"
        self.query.add(Q(activo=is_active), Q.AND)
    return self.model.objects.filter(self.query).order_by('apellidos')

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context['title1'] = "Listado Doctores"
    context['title2'] = "Nuevo Doctor"
    return context


class DoctorCreateView(CreateView):
  model = Doctor
  template_name = 'core/doctor/form.html'
  form_class = DoctorForm
  success_url = reverse_lazy('core:doctor_list')

  def get_context_data(self, **kwargs):
    context = super().get_context_data()
    context['title1'] = 'Crear Doctor'
    context['grabar'] = 'Grabar Doctor'
    context['default_image_url'] = static('img/doctor_avatar.webp')
    context['back_url'] = self.success_url
    return context

  def form_valid(self, form):
    response = super().form_valid(form)
    objAudit = self.object
    save_audit(self.request, objAudit, action='A')
    messages.success(self.request, f"Éxito al Crear al Doctor {objAudit.nombre_completo}.")
    return response

  def form_invalid(self, form):
    messages.error(self.request, "Error al enviar el formulario. Corrige los errores.")
    print(form.errors)
    return self.render_to_response(self.get_context_data(form=form))


class DoctorUpdateView(UpdateView):
  model = Doctor
  template_name = 'core/doctor/form.html'
  form_class = DoctorForm
  success_url = reverse_lazy('core:doctor_list')

  def get_context_data(self, **kwargs):
    context = super().get_context_data()
    context['title1'] = 'Actualizar Doctor'
    context['grabar'] = 'Actualizar Doctor'
    context['default_image_url'] = static('img/doctor_avatar.webp')
    context['current_image_url'] = self.object.foto.url if self.object.foto else static('img/doctor_avatar.webp')
    context['back_url'] = self.success_url
    context['is_edit_mode'] = True  # Para habilitar edición en el calendario
    return context

  def form_valid(self, form):
    horario_data = form.cleaned_data.get('horario_atencion')
    try:
      if horario_data:
        json.loads(horario_data)
    except json.JSONDecodeError:
      messages.error(self.request, "Error en el formato del horario de atención")
      return self.form_invalid(form)

    response = super().form_valid(form)
    objAudit = self.object
    save_audit(self.request, objAudit, action='M')
    messages.success(self.request, f"Éxito al Modificar al Doctor {objAudit.nombre_completo}.")
    return response


class DoctorDeleteView(DeleteView):
  model = Doctor
  success_url = reverse_lazy('core:doctor_list')

  def get_context_data(self, **kwargs):
    context = super().get_context_data()
    context['grabar'] = 'Eliminar Doctor'
    context['description'] = f"¿Desea Eliminar al Doctor: {self.object.nombre_completo}?"
    return context

  def delete(self, request, *args, **kwargs):
    self.object = self.get_object()
    success_message = f"Éxito al eliminar lógicamente al Doctor {self.object.nombre_completo}."
    messages.success(self.request, success_message)
    return super().delete(request, *args, **kwargs)


class DoctorDetailView(DetailView):
  model = Doctor
  extra_context = {
    "detail": "Detalles del Doctor"
  }

  def get(self, request, *args, **kwargs):
    doctor = self.get_object()
    data = {
      'id': doctor.id,
      'doctor': doctor.nombre_completo,
      'cedula': doctor.cedula,
      'fecha_nacimiento': doctor.fecha_nacimiento.isoformat() if doctor.fecha_nacimiento else None,
      'edad': doctor.calcular_edad(doctor.fecha_nacimiento),
      'direccion': doctor.direccion,
      'latitud': str(doctor.latitud) if doctor.latitud is not None else None,
      'longitud': str(doctor.longitud) if doctor.longitud is not None else None,
      'codigoUnicoDoctor': doctor.codigoUnicoDoctor,
      'especialidad': [especialidad.nombre for especialidad in doctor.especialidad.all()],
      'telefonos': doctor.telefonos,
      'email': doctor.email,
      'duracion_cita': doctor.duracion_cita,
      'curriculum': doctor.curriculum.url if doctor.curriculum else None,
      'firmaDigital': doctor.firmaDigital.url if doctor.firmaDigital else None,
      'foto': doctor.get_image(),
      'imagen_receta': doctor.imagen_receta.url if doctor.imagen_receta else None,
      'activo': doctor.activo,
    }
    return JsonResponse(data)


class DoctorHorarioDetailView(UpdateView):
  model = Doctor
  template_name = 'core/doctor/horario_detail.html'
  form_class = DoctorForm
  success_url = reverse_lazy('core:doctor_list')

  def get_context_data(self, **kwargs):
    context = super().get_context_data()
    context['title1'] = 'Calendario del Doctor'
    context['default_image_url'] = static('img/doctor_avatar.webp')
    context['current_image_url'] = self.object.foto.url if self.object.foto else static('img/doctor_avatar.webp')
    context['back_url'] = self.success_url
    context['is_edit_mode'] = True
    return context

  def form_valid(self, form):
    horario_data = form.cleaned_data.get('horario_atencion')
    try:
      if horario_data:
        json.loads(horario_data)
    except json.JSONDecodeError:
      messages.error(self.request, "Error en el formato del horario de atención")
      return self.form_invalid(form)

    response = super().form_valid(form)
    objAudit = self.object
    save_audit(self.request, objAudit, action='M')
    messages.success(self.request, f"Éxito al Modificar al Doctor {objAudit.nombre_completo}.")
    return response

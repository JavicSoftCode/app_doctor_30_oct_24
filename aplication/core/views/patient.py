from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse, Http404
from django.shortcuts import redirect
from django.templatetags.static import static
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView, DeleteView, DetailView

from aplication.core.forms.patient import PatientForm
from aplication.core.models import Paciente
from doctor.utils import save_audit


class PatientListView(ListView):
  template_name = "core/patient/list.html"
  model = Paciente
  context_object_name = 'pacientes'
  query = None
  paginate_by = 5

  def get_queryset(self):
    self.query = Q()
    q1 = self.request.GET.get('q')
    sex = self.request.GET.get('sex')
    if q1 is not None:
      self.query.add(Q(nombres__icontains=q1), Q.OR)
      self.query.add(Q(apellidos__icontains=q1), Q.OR)
      self.query.add(Q(cedula__icontains=q1), Q.OR)
    if sex == "M" or sex == "F": self.query.add(Q(sexo__icontains=sex), Q.AND)
    return self.model.objects.filter(self.query).order_by('apellidos')

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context['title'] = "Medical"
    context['title1'] = "Consulta de Pacientes"
    return context


class PatientCreateView(CreateView):
  model = Paciente
  template_name = 'core/patient/form.html'
  form_class = PatientForm
  success_url = reverse_lazy('core:patient_list')

  def get_context_data(self, **kwargs):
    context = super().get_context_data()
    context['title1'] = 'Crear Paciente'
    context['grabar'] = 'Grabar Paciente'
    context['default_image_url'] = static('img/paciente_avatar.png')

    context['back_url'] = self.success_url
    return context

  def form_valid(self, form):
    response = super().form_valid(form)
    patient = self.object
    save_audit(self.request, patient, action='A')
    messages.success(self.request, f"Éxito al crear al paciente {patient.nombre_completo}.")
    return response

  def form_invalid(self, form):
    messages.error(self.request, "Error al enviar el formulario. Corrige los errores.")
    print(form.errors)
    return self.render_to_response(self.get_context_data(form=form))


class PatientUpdateView(UpdateView):
  model = Paciente
  template_name = 'core/patient/form.html'
  form_class = PatientForm
  success_url = reverse_lazy('core:patient_list')

  def get_context_data(self, **kwargs):
    context = super().get_context_data()
    context['title1'] = 'Actualizar Paciente'
    context['grabar'] = 'Actualizar Paciente'
    context['default_image_url'] = static('img/paciente_avatar.png')
    context['current_image_url'] = self.object.foto.url if self.object.foto else static('img/paciente_avatar.png')
    context['back_url'] = self.success_url
    return context

  def form_valid(self, form):
    response = super().form_valid(form)
    patient = self.object
    save_audit(self.request, patient, action='M')
    messages.success(self.request, f"Éxito al Modificar el paciente {patient.nombre_completo}.")
    print("mande mensaje")
    return response

  def form_invalid(self, form):
    messages.error(self.request, "Error al Modificar el formulario. Corrige los errores.")
    print(form.errors)
    return self.render_to_response(self.get_context_data(form=form))


class PatientDeleteView(DeleteView):
  model = Paciente
  success_url = reverse_lazy('core:patient_list')

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context['grabar'] = 'Eliminar paciente'
    context['description'] = f"¿Desea eliminar al paciente: {self.object.nombre_completo}?"
    context['back_url'] = self.success_url
    return context

  def delete(self, request, *args, **kwargs):
    self.object = self.get_object()

    # Verifica si el paciente tiene relaciones en `doctores_atencion` o `pacientes_examenes`
    if self.object.tiene_relaciones:
      messages.error(self.request,
                     "No se puede eliminar el paciente porque tiene atención médica o exámenes solicitados.")
      return redirect(self.success_url)

    success_message = f"Éxito al eliminar lógicamente al paciente {self.object.nombre_completo}."
    messages.success(self.request, success_message)
    return super().delete(request, *args, **kwargs)


# class PatientDeleteView(DeleteView):
#   model = Paciente
#   success_url = reverse_lazy('core:patient_list')
#
#   def get_context_data(self, **kwargs):
#     context = super().get_context_data()
#     context['grabar'] = 'Eliminar paciente'
#     context['description'] = f"¿Desea Eliminar al paciente: {self.object.nombre_completo}?"
#     context['back_url'] = self.success_url
#     return context
#
#   def delete(self, request, *args, **kwargs):
#     self.object = self.get_object()
#     if self.object.doctores_atencion.exists():
#       messages.error(self.request, "No se puede eliminar el paciente porque tiene una atención Médica.")
#       return self.get(request, *args, **kwargs)
#
#     success_message = f"Éxito al eliminar lógicamente al Paciente {self.object.nombre_completo}."
#     messages.success(self.request, success_message)
#     return super().delete(request, *args, **kwargs)


class PatientDetailView(DetailView):
  model = Paciente

  def get(self, request, *args, **kwargs):
    try:
      pacient = self.get_object()
      data = {
        'id': pacient.id,
        'paciente': pacient.nombre_completo,
        'foto': pacient.get_image(),
        'fecha_nacimiento': pacient.fecha_nacimiento,
        'edad': pacient.calcular_edad(pacient.fecha_nacimiento),
        'cedula': pacient.cedula,
        'telefono': pacient.telefono,
        'email': pacient.email,
        'sexo': pacient.get_sexo_display() if pacient.sexo else None,
        'estado_civil': pacient.get_estado_civil_display() if pacient.estado_civil else None,
        'direccion': pacient.direccion,
        'latitud': pacient.latitud,
        'longitud': pacient.longitud,
        'tipo_sangre': pacient.tipo_sangre.tipo if pacient.tipo_sangre else None,
        'alergias': pacient.alergias,
        'enfermedades_cronicas': pacient.enfermedades_cronicas,
        'medicacion_actual': pacient.medicacion_actual,
        'cirugias_previas': pacient.cirugias_previas,
        'antecedentes_personales': pacient.antecedentes_personales,
        'antecedentes_familiares': pacient.antecedentes_familiares,
        'activo': pacient.activo,
      }
      return JsonResponse(data)
    except Paciente.DoesNotExist:
      raise Http404("Paciente no encontrado")

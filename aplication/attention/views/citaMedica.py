from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView, DeleteView, DetailView

from aplication.attention.forms.citaMedica import CitaMedicaForm
from aplication.attention.models import CitaMedica
from doctor.utils import save_audit


class CitaMedicaListView(ListView):
  template_name = "attention/citaMedica/list.html"
  model = CitaMedica
  context_object_name = 'citas'
  paginate_by = 5
  query = None

  def get_queryset(self):
    self.query = Q()
    q1 = self.request.GET.get('q')  # Texto de búsqueda
    estado = self.request.GET.get('estado')  # Estado de la cita

    if q1:
        # Si q1 es un número, filtrar solo por ID
        if q1.isdigit():
            self.query.add(Q(id=q1), Q.AND)
            self.query.add(Q(paciente__cedula__icontains=q1), Q.OR)

        else:
            # Si q1 no es un número, buscar por nombres y apellidos del paciente
            self.query.add(Q(paciente__nombres__icontains=q1), Q.OR)
            self.query.add(Q(paciente__apellidos__icontains=q1), Q.OR)

    # Filtrar por estado si es uno de los valores válidos
    if estado in ["P", "C", "R"]:
        self.query.add(Q(estado=estado), Q.AND)

    # Retornar el queryset filtrado, ordenado por nombres y apellidos del paciente
    return self.model.objects.filter(self.query).order_by('paciente__nombres', 'paciente__apellidos')

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context['title1'] = "Listado de Citas Médicas"
    context['title2'] = "Nueva Cita Médica"
    return context


class CitaMedicaCreateView(CreateView):
  model = CitaMedica
  template_name = 'attention/citaMedica/form.html'
  form_class = CitaMedicaForm
  success_url = reverse_lazy('attention:citaMedica_list')

  def get_context_data(self, **kwargs):
    context = super().get_context_data()
    context['title1'] = 'Crear Cita Médica'
    context['grabar'] = 'Grabar Cita Médica'
    context['back_url'] = self.success_url
    return context

  def form_valid(self, form):
    # print("entro al form_valid")
    response = super().form_valid(form)
    citaMedica = self.object
    save_audit(self.request, citaMedica, action='A')
    messages.success(self.request, f"Éxito al Crear la Cita Médica {citaMedica.paciente} - {citaMedica.estado}.")
    return response

  # def form_valid(self, form):
  #   if hasattr(self.request, 'user') and self.request.user.is_authenticated:
  #     form.instance.usuario = self.request.user
  #   else:
  #     # Asigna un valor alternativo o evita la asignación si el usuario no está autenticado
  #     form.instance.usuario = None  # O el valor que consideres adecuado
  #     messages.success(self.request, f"Éxito al Crear la Especialidad.")
  #
  #   return super().form_valid(form)

  def form_invalid(self, form):
    messages.error(self.request, "Error al enviar el formulario. Corrige los errores.")
    print(form.errors)
    return self.render_to_response(self.get_context_data(form=form))


class CitaMedicaUpdateView(UpdateView):
  model = CitaMedica
  template_name = 'attention/citaMedica/form.html'
  form_class = CitaMedicaForm
  success_url = reverse_lazy('attention:citaMedica_list')

  def get_context_data(self, **kwargs):
    context = super().get_context_data()
    context['title1'] = 'Actualizar Cita Médica'
    context['grabar'] = 'Actualizar Cita Médica'
    context['back_url'] = self.success_url
    return context

  def form_valid(self, form):
    response = super().form_valid(form)
    citaMedica = self.object
    save_audit(self.request, citaMedica, action='M')
    messages.success(self.request, f"Éxito al Modificar la Especialidad {citaMedica.paciente} - {citaMedica.estado}.")
    print("mande mensaje")
    return response

  # def form_valid(self, form):
  #   bloodType = self.object
  #   if hasattr(self.request, 'user') and self.request.user.is_authenticated:
  #     form.instance.usuario = self.request.user
  #   else:
  #     # Asigna un valor alternativo o evita la asignación si el usuario no está autenticado
  #     form.instance.usuario = None  # O el valor que consideres adecuado
  #     messages.success(self.request, f"Éxito al Modificar la Especialidad {bloodType.nombre}.")
  #
  #   return super().form_valid(form)

  def form_invalid(self, form):
    messages.error(self.request, "Error al Modificar el formulario. Corrige los errores.")
    print(form.errors)
    return self.render_to_response(self.get_context_data(form=form))


class CitaMedicaDeleteView(DeleteView):
  model = CitaMedica
  success_url = reverse_lazy('attention:citaMedica_list')

  def get_context_data(self, **kwargs):
    context = super().get_context_data()
    context['grabar'] = 'Eliminar Cita Médica'
    context['description'] = f"¿Desea Eliminar la Cita Médica: {self.object.paciente}?"
    return context

  def delete(self, request, *args, **kwargs):
    self.object = self.get_object()
    success_message = f"Éxito al eliminar lógicamente la Cita Médica {self.object.paciente} - {self.object.estado}."
    messages.success(self.request, success_message)
    # Cambiar el estado de eliminado lógico
    # self.object.deleted = True
    # self.object.save()
    return super().delete(request, *args, **kwargs)


class CitaMedicaDetailView(DetailView):
  model = CitaMedica
  extra_context = {
    "detail": "Detalles de la Cita Médica"
  }

  def get(self, request, *args, **kwargs):
    citaMedica = self.get_object()
    data = {
      'id': citaMedica.id,
      'paciente': citaMedica.paciente,
      'fecha': citaMedica.fecha,
      'hora_cita': citaMedica.hora_cita,
      'estado': citaMedica.get_estado_display(),  # Muestra "Programada", "Cancelada" o "Realizada"
    }
    return JsonResponse(data)

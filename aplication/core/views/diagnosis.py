from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView, DeleteView, DetailView

from aplication.core.forms.diagnosis import DiagnosisForm
from aplication.core.models import Diagnostico
from doctor.utils import save_audit


class DiagnosisListView(ListView):
  template_name = "core/diagnosis/list.html"
  model = Diagnostico
  context_object_name = 'diagnosticos'
  paginate_by = 5
  query = None

  def get_queryset(self):
    self.query = Q()
    q1 = self.request.GET.get('q')  # Texto de búsqueda
    diagnosis = self.request.GET.get('diagnostico')  # Estado activo o inactivo

    if q1:
      if q1.isdigit():
        self.query.add(Q(id=q1), Q.AND)

      else:
        # Filtra por nombre que contenga el valor ingresado en 'q'
        self.query.add(Q(codigo__icontains=q1), Q.AND)

    if diagnosis in ["True", "False"]:
      # Filtra por el valor booleano de activo
      is_active = diagnosis == "True"  # Convierte a booleano
      self.query.add(Q(activo=is_active), Q.AND)

    return self.model.objects.filter(self.query).order_by('descripcion')

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context['title1'] = "Listado de Diagnosticos"
    context['title2'] = "Nuevo Diagnostico"
    return context


class DiagnosisCreateView(CreateView):
  model = Diagnostico
  template_name = 'core/diagnosis/form.html'
  form_class = DiagnosisForm
  success_url = reverse_lazy('core:diagnosis_list')

  def get_context_data(self, **kwargs):
    context = super().get_context_data()
    context['title1'] = 'Crear Diagnostico'
    context['grabar'] = 'Grabar Diagnostico'
    context['back_url'] = self.success_url
    return context

  def form_valid(self, form):
    response = super().form_valid(form)
    objAudit = self.object
    save_audit(self.request, objAudit, action='A')
    messages.success(self.request, f"Éxito al Crear el Diagnostico {objAudit.codigo}.")
    return response

  # def form_valid(self, form):
  #   if hasattr(self.request, 'user') and self.request.user.is_authenticated:
  #     form.instance.usuario = self.request.user
  #   else:
  #     # Asigna un valor alternativo o evita la asignación si el usuario no está autenticado
  #     form.instance.usuario = None  # O el valor que consideres adecuado
  #     messages.success(self.request, f"Éxito al Crear el Diagnostico.")
  #
  #   return super().form_valid(form)

  def form_invalid(self, form):
    messages.error(self.request, "Error al enviar el formulario. Corrige los errores.")
    print(form.errors)
    return self.render_to_response(self.get_context_data(form=form))


class DiagnosisUpdateView(UpdateView):
  model = Diagnostico
  template_name = 'core/diagnosis/form.html'
  form_class = DiagnosisForm
  success_url = reverse_lazy('core:diagnosis_list')

  def get_context_data(self, **kwargs):
    context = super().get_context_data()
    context['title1'] = 'Actualizar Diagnostico'
    context['grabar'] = 'Actualizar Diagnostico'
    context['back_url'] = self.success_url
    return context

  def form_valid(self, form):
    response = super().form_valid(form)
    objAudit = self.object
    save_audit(self.request, objAudit, action='M')
    messages.success(self.request, f"Éxito al Modificar el Diagnostico {objAudit.codigo}.")
    return response

  # def form_valid(self, form):
  #   diagnosis = self.object
  #   if hasattr(self.request, 'user') and self.request.user.is_authenticated:
  #     form.instance.usuario = self.request.user
  #   else:
  #     # Asigna un valor alternativo o evita la asignación si el usuario no está autenticado
  #     form.instance.usuario = None  # O el valor que consideres adecuado
  #     messages.success(self.request, f"Éxito al Modificar el Diagnostico {diagnosis.codigo}.")
  #
  #   return super().form_valid(form)

  def form_invalid(self, form):
    messages.error(self.request, "Error al Modificar el formulario. Corrige los errores.")
    print(form.errors)
    return self.render_to_response(self.get_context_data(form=form))


class DiagnosisDeleteView(DeleteView):
  model = Diagnostico
  success_url = reverse_lazy('core:diagnosis_list')

  def get_context_data(self, **kwargs):
    context = super().get_context_data()
    context['grabar'] = 'Eliminar Diagnostico'
    context['description'] = f"¿Desea Eliminar el Diagnostico: {self.object.codigo}?"
    return context

  def delete(self, request, *args, **kwargs):
    self.object = self.get_object()
    success_message = f"Éxito al eliminar lógicamente el Diagnostico {self.object.codigo}."
    messages.success(self.request, success_message)
    # Cambiar el estado de eliminado lógico
    # self.object.deleted = True
    # self.object.save()
    return super().delete(request, *args, **kwargs)


class DiagnosisDetailView(DetailView):
  model = Diagnostico
  extra_context = {
    "detail": "Detalles del Diagnostico"
  }

  def get(self, request, *args, **kwargs):
    diagnosis = self.get_object()
    data = {
      'id': diagnosis.id,
      'codigo': diagnosis.codigo,
      'descripcion': diagnosis.descripcion,
      'datos_adicionales': diagnosis.datos_adicionales,
      'activo': diagnosis.activo,
    }
    return JsonResponse(data)

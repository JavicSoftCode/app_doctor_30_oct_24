from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView, DeleteView, DetailView

from aplication.core.models import AuditUser


class AuditUserListView(ListView):
  template_name = "core/auditUser/list.html"
  model = AuditUser
  context_object_name = 'auditorias'
  paginate_by = 5
  query = None

  def get_queryset(self):
    # Creamos un Q() vacío para acumular las condiciones de búsqueda
    self.query = Q()
    q1 = self.request.GET.get('q')  # Texto de búsqueda
    accion_filter = self.request.GET.get('acciones')  # Filtro de acción (Adición, Modificación, Eliminación)

    if q1:
        # Filtra por usuario, tabla o registroid que contengan el texto ingresado en 'q'
        self.query |= Q(usuario__username__icontains=q1)
        self.query |= Q(tabla__icontains=q1)
        self.query |= Q(registroid__icontains=q1)

    if accion_filter in ["A", "M", "E"]:
        # Filtra por el valor seleccionado en el filtro de acciones
        self.query &= Q(accion=accion_filter)

    # Retorna los resultados ordenados por 'fecha' y 'hora'
    return self.model.objects.filter(self.query).order_by('fecha', 'hora')

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context['title1'] = "Listado de Auditorias de Usuarios"
    context['title2'] = "Auditoria de Usuario"
    return context


class AuditUserDetailView(DetailView):
  model = AuditUser
  extra_context = {
    "detail": "Detalles de la Auditoria de Usuario"
  }

  def get(self, request, *args, **kwargs):
    auditUser = self.get_object()
    data = {
      'id': auditUser.id,
      'usuario': auditUser.usuario.username,
      'tabla': auditUser.tabla,
      'registroid': auditUser.registroid,
      'accion': auditUser.accion,
      'fecha': auditUser.fecha,
      'hora': auditUser.hora,
      'estacion': auditUser.estacion,
    }
    return JsonResponse(data)

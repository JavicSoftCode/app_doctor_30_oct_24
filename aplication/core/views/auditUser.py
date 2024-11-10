from django.db.models import Q
from django.http import JsonResponse
from django.views.generic import ListView, DetailView

from aplication.core.models import AuditUser


# class AuditUserListView(ListView):
#   template_name = "core/auditUser/list.html"
#   model = AuditUser
#   context_object_name = 'auditorias'
#   paginate_by = 5
#   query = None
#
#   def get_queryset(self):
#     self.query = Q()
#     q1 = self.request.GET.get('q')
#     accion_filter = self.request.GET.get('acciones')
#
#     if q1:
#       if q1.isdigit():
#         self.query.add(Q(id=q1), Q.AND)
#
#       else:
#         self.query |= Q(usuario__username__icontains=q1)
#         self.query |= Q(tabla__icontains=q1)
#         self.query |= Q(registroid__icontains=q1)
#
#     if accion_filter in ["A", "M", "E"]:
#       self.query &= Q(accion=accion_filter)
#
#     return self.model.objects.filter(self.query).order_by('fecha', 'hora')
#
#   def get_context_data(self, **kwargs):
#     context = super().get_context_data(**kwargs)
#     context['title1'] = "Listado de Auditorias de Usuarios"
#     context['title2'] = "Auditoria de Usuario"
#     return context

# La clase `AuditUserListView` genera una vista de lista paginada de auditorías de usuario,
# filtrando resultados según criterios de búsqueda y de acción específica.
# Utiliza el modelo `AuditUser` y proporciona un contexto adicional con títulos personalizados.

class AuditUserListView(ListView):
  template_name = "core/auditUser/list.html"
  model = AuditUser
  context_object_name = 'auditorias'
  paginate_by = 5
  query = None

  def get_queryset(self):
    # Inicializa la query como una combinación vacía
    self.query = Q()
    q1 = self.request.GET.get('q')
    accion_filter = self.request.GET.get('acciones')

    # Filtra por ID si `q` es un dígito, o realiza búsquedas parciales en otros campos
    if q1:
      if q1.isdigit():
        self.query.add(Q(id=q1), Q.AND)
      else:
        self.query |= Q(usuario__username__icontains=q1)
        self.query |= Q(tabla__icontains=q1)
        self.query |= Q(registroid__icontains=q1)

    # Filtra por acción específica si coincide con "A", "M" o "E"
    if accion_filter in ["A", "M", "E"]:
      self.query &= Q(accion=accion_filter)

    # Ordena los resultados por fecha y hora
    return self.model.objects.filter(self.query).order_by('fecha', 'hora')

  def get_context_data(self, **kwargs):
    # Agrega títulos personalizados al contexto de la vista
    context = super().get_context_data(**kwargs)
    context['title1'] = "Listado de Auditorias de Usuarios"
    context['title2'] = "Auditoria de Usuario"
    return context


# class AuditUserDetailView(DetailView):
#   model = AuditUser
#   extra_context = {
#     "detail": "Detalles de la Auditoria de Usuario"
#   }
#
#   def get(self, request, *args, **kwargs):
#     auditUser = self.get_object()
#     data = {
#       'id': auditUser.id,
#       'usuario': auditUser.usuario.username,
#       'tabla': auditUser.tabla,
#       'registroid': auditUser.registroid,
#       'accion': auditUser.accion,
#       'fecha': auditUser.fecha,
#       'hora': auditUser.hora,
#       'estacion': auditUser.estacion,
#     }
#     return JsonResponse(data)

# La clase `AuditUserDetailView` proporciona una vista detallada para una auditoría de usuario específica.
# Utiliza el modelo `AuditUser` y devuelve los detalles de la auditoría en formato JSON al realizar una solicitud GET.

class AuditUserDetailView(DetailView):
  model = AuditUser
  extra_context = {
    "detail": "Detalles de la Auditoria de Usuario"
  }

  def get(self, request, *args, **kwargs):
    # Obtiene el objeto de auditoría y lo retorna en formato JSON
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

from django.utils import timezone
from django.views.generic import TemplateView

from aplication.attention.models import CitaMedica, Atencion
from aplication.core.models import Paciente


class HomeTemplateView(TemplateView):
  template_name = 'core/home.html'

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)

    # Obtener la fecha y hora actual
    ahora = timezone.now()

    # Consultar las tres próximas citas programadas
    proximas_citas = CitaMedica.objects.filter(
      fecha__gte=ahora.date(),  # Filtra citas futuras o para hoy
      estado='P'  # Solo las que tienen estado 'P' (programadas)
    ).order_by('fecha', 'hora_cita')[:3]

    # Agregar información al contexto
    context.update({
      "title1": "SaludSync",
      "title2": "Sistema Medico",
      "can_paci": Paciente.cantidad_pacientes(),
      "can_citas": CitaMedica.cantidad_disponible_hoy(),
      "can_atencion": Atencion.cantidad(),
      "proximas_citas": proximas_citas,  # Agregar las citas al contexto
    })

    return context

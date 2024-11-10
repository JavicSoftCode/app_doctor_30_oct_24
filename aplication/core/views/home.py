# import datetime
# from django.utils import timezone
# from django.utils.timesince import timesince
# from django.views.generic import TemplateView
#
# from aplication.attention.models import CitaMedica
# from aplication.core.models import Paciente
#
#
# class HomeTemplateView(TemplateView):
#   template_name = 'core/home.html'
#
#   def get_context_data(self, **kwargs):
#     context = super().get_context_data(**kwargs)
#     ahora = timezone.now().replace(tzinfo=None)  # Elimina la zona horaria de `ahora`
#
#     # Obtener la última cita médica con estado "R" (Realizada)
#     ultima_cita_realizada = CitaMedica.objects.filter(
#       estado='R'
#     ).order_by('-fecha', '-hora_cita').first()
#
#     # Calcular el tiempo transcurrido desde la última cita realizada
#     tiempo_desde_ultima_cita = None
#     if ultima_cita_realizada:
#       # Combina fecha y hora de la cita sin zona horaria
#       fecha_hora_cita = datetime.datetime.combine(
#         ultima_cita_realizada.fecha, ultima_cita_realizada.hora_cita
#       ).replace(tzinfo=None)  # Convierte a "naive" sin zona horaria
#       tiempo_desde_ultima_cita = timesince(fecha_hora_cita, ahora)
#
#     # Obtener el último paciente registrado
#     ultimo_paciente = Paciente.objects.order_by('-fecha_creacion').first()
#
#     # Calcular el tiempo transcurrido desde el último paciente registrado
#     tiempo_desde_ultimo_paciente = None
#     if ultimo_paciente:
#       fecha_creacion_naive = ultimo_paciente.fecha_creacion.replace(tzinfo=None)  # Sin zona horaria
#       tiempo_desde_ultimo_paciente = timesince(fecha_creacion_naive, ahora)
#
#     # Consultar las próximas citas programadas (estado "P") en orden descendente
#     proximas_citas = CitaMedica.objects.filter(
#       fecha__gte=ahora.date(),
#       estado='P'
#     ).order_by('fecha', 'hora_cita')[:3]
#
#     context.update({
#       "title1": "SaludSync",
#       "title2": "Sistema Medico",
#       "can_paci": Paciente.cantidad_pacientes(),
#       "can_citas": CitaMedica.cantidad_disponible_hoy(),
#       "proximas_citas": proximas_citas,
#       "ultima_cita_realizada": ultima_cita_realizada,
#       "tiempo_desde_ultima_cita": tiempo_desde_ultima_cita,
#       "ultimo_paciente": ultimo_paciente,
#       "tiempo_desde_ultimo_paciente": tiempo_desde_ultimo_paciente,
#     })
#
#     return context
import datetime
from django.utils import timezone
from django.utils.timesince import timesince
from django.views.generic import TemplateView

from aplication.attention.models import CitaMedica, Atencion
from aplication.core.models import Paciente


class HomeTemplateView(TemplateView):
    template_name = 'core/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ahora = timezone.now().replace(tzinfo=None)  # Convierte `ahora` a naive

        # Obtener la última cita médica con estado "R" (Realizada)
        ultima_cita_realizada = CitaMedica.objects.filter(
            estado='R'
        ).order_by('-fecha', '-hora_cita').first()

        # Calcular el tiempo transcurrido desde la última cita realizada
        tiempo_desde_ultima_cita = None
        if ultima_cita_realizada:
            # Convierte la fecha y hora de la cita a naive para eliminar zona horaria
            fecha_hora_cita = datetime.datetime.combine(
                ultima_cita_realizada.fecha, ultima_cita_realizada.hora_cita
            ).replace(tzinfo=None)

            # Calcula el tiempo transcurrido en segundos, minutos y horas
            tiempo_transcurrido_segundos = (ahora - fecha_hora_cita).total_seconds()

            # Usa `timesince` para mostrar en formato de tiempo amigable
            tiempo_desde_ultima_cita = timesince(fecha_hora_cita, ahora)

        # Obtener el último paciente registrado
        ultimo_paciente = Paciente.objects.order_by('-fecha_creacion').first()

        # Calcular el tiempo transcurrido desde el último paciente registrado
        tiempo_desde_ultimo_paciente = None
        if ultimo_paciente:
            fecha_creacion_naive = ultimo_paciente.fecha_creacion.replace(tzinfo=None)
            tiempo_desde_ultimo_paciente = timesince(fecha_creacion_naive, ahora)

        # Consultar las próximas citas programadas (estado "P") en orden descendente
        proximas_citas = CitaMedica.objects.filter(
            fecha__gte=ahora.date(),
            estado='P'
        ).order_by('fecha', 'hora_cita')[:3]

        context.update({
            "title1": "SaludSync",
            "title2": "Sistema Medico",
            "can_paci": Paciente.cantidad_pacientes(),
            "can_citas": CitaMedica.cantidad_disponible_hoy(),
            "can_atencion": Atencion.cantidad(),
            "proximas_citas": proximas_citas,
            "ultima_cita_realizada": ultima_cita_realizada,
            "tiempo_desde_ultima_cita": tiempo_desde_ultima_cita,
            "ultimo_paciente": ultimo_paciente,
            "tiempo_desde_ultimo_paciente": tiempo_desde_ultimo_paciente,
        })

        return context

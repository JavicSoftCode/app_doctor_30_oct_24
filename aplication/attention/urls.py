from django.urls import path
from aplication.attention.views.atencion import *
from aplication.attention.views.citaMedica import *
from aplication.attention.views.examenSolicitado import *
from aplication.attention.views.serviciosAdicionales import *

app_name = "attention"

urlpatterns = [

    # URLs atencion
    path('atencion_list/', AtencionListView.as_view(), name='atencion_list'),
    path('atencion_create/', AtencionCreateView.as_view(), name='atencion_create'),
    path('atencion_update/<int:pk>/', AtencionUpdateView.as_view(), name='atencion_update'),
    path('atencion_delete/<int:pk>/', AtencionDeleteView.as_view(), name='atencion_delete'),
    path('atencion_detail/<int:pk>/', AtencionDetailView.as_view(), name='atencion_detail'),

    # URLs cita medica
    path('citaMedica_list/', CitaMedicaListView.as_view(), name='citaMedica_list'),
    path('citaMedica_create/', CitaMedicaCreateView.as_view(), name='citaMedica_create'),
    path('citaMedica_update/<int:pk>/', CitaMedicaUpdateView.as_view(), name='citaMedica_update'),
    path('citaMedica_delete/<int:pk>/', CitaMedicaDeleteView.as_view(), name='citaMedica_delete'),
    path('citaMedica_detail/<int:pk>/', CitaMedicaDetailView.as_view(), name='citaMedica_detail'),

    # URLs examen solicitado
    path('examenSolicitado_list/', ExamenSolicitadoListView.as_view(), name='examenSolicitado_list'),
    path('examenSolicitado_create/', ExamenSolicitadoCreateView.as_view(), name='examenSolicitado_create'),
    path('examenSolicitado_update/<int:pk>/', ExamenSolicitadoUpdateView.as_view(), name='examenSolicitado_update'),
    path('examenSolicitado_delete/<int:pk>/', ExamenSolicitadoDeleteView.as_view(), name='examenSolicitado_delete'),
    path('examenSolicitado_detail/<int:pk>/', ExamenSolicitadoDetailView.as_view(), name='examenSolicitado_detail'),

    # URLs servicios adicionales
    path('serviciosAdicionales_list/', ServiciosAdicionalesListView.as_view(), name='serviciosAdicionales_list'),
    path('serviciosAdicionales_create/', ServiciosAdicionalesCreateView.as_view(), name='serviciosAdicionales_create'),
    path('serviciosAdicionales_update/<int:pk>/', ServiciosAdicionalesUpdateView.as_view(), name='serviciosAdicionales_update'),
    path('serviciosAdicionales_delete/<int:pk>/', ServiciosAdicionalesDeleteView.as_view(), name='serviciosAdicionales_delete'),
    path('serviciosAdicionales_detail/<int:pk>/', ServiciosAdicionalesDetailView.as_view(), name='serviciosAdicionales_detail'),
]

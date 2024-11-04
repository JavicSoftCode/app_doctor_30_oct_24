from django.urls import path
from aplication.attention.views.atencion import *
from aplication.attention.views.citaMedica import *

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
]

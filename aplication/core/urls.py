from django.urls import path

from aplication.core.views.bloodType import *
from aplication.core.views.cargo import *
from aplication.core.views.categoryExamen import *
from aplication.core.views.categoryType import *
from aplication.core.views.diagnosis import *
from aplication.core.views.doctor import *
from aplication.core.views.empleado import *
from aplication.core.views.home import HomeTemplateView
from aplication.core.views.medicine import *
from aplication.core.views.medicineType import *
from aplication.core.views.patient import *
from aplication.core.views.specialty import *
from aplication.core.views.auditUser import *

app_name = 'core'
urlpatterns = [

  # ruta principal
  path('', HomeTemplateView.as_view(), name='home'),

  # URLs de pacientes
  path('patient_list/', PatientListView.as_view(), name="patient_list"),
  path('patient_create/', PatientCreateView.as_view(), name="patient_create"),
  path('patient_update/<int:pk>/', PatientUpdateView.as_view(), name='patient_update'),
  path('patient_delete/<int:pk>/', PatientDeleteView.as_view(), name='patient_delete'),
  path('patient_detail/<int:pk>/', PatientDetailView.as_view(), name='patient_detail'),

  # URLs de tipo sangre
  path('bloodType_list/', BloodTypeListView.as_view(), name="bloodType_list"),
  path('bloodType_create/', BloodTypeCreateView.as_view(), name="bloodType_create"),
  path('bloodType_update/<int:pk>/', BloodTypeUpdateView.as_view(), name='bloodType_update'),
  path('bloodType_delete/<int:pk>/', BloodTypeDeleteView.as_view(), name='bloodType_delete'),
  path('bloodType_detail/<int:pk>/', BloodTypeDetailView.as_view(), name='bloodType_detail'),

  # URLs de especialidad
  path('specialty_list/', SpecialtyListView.as_view(), name="specialty_list"),
  path('specialty_create/', SpecialtyCreateView.as_view(), name="specialty_create"),
  path('specialty_update/<int:pk>/', SpecialtyUpdateView.as_view(), name='specialty_update'),
  path('specialty_delete/<int:pk>/', SpecialtyDeleteView.as_view(), name='specialty_delete'),
  path('specialty_detail/<int:pk>/', SpecialtyDetailView.as_view(), name='specialty_detail'),

  # URLs de doctor
  path('doctor_list/', DoctorListView.as_view(), name="doctor_list"),
  path('doctor_create/', DoctorCreateView.as_view(), name="doctor_create"),
  path('doctor_update/<int:pk>/', DoctorUpdateView.as_view(), name='doctor_update'),
  path('doctor_delete/<int:pk>/', DoctorDeleteView.as_view(), name='doctor_delete'),
  path('doctor_detail/<int:pk>/', DoctorDetailView.as_view(), name='doctor_detail'),

  # URLs de cargos
  path('cargo_list/', CargoListView.as_view(), name="cargo_list"),
  path('cargo_create/', CargoCreateView.as_view(), name="cargo_create"),
  path('cargo_update/<int:pk>/', CargoUpdateView.as_view(), name='cargo_update'),
  path('cargo_delete/<int:pk>/', CargoDeleteView.as_view(), name='cargo_delete'),
  path('cargo_detail/<int:pk>/', CargoDetailView.as_view(), name='cargo_detail'),

  # URLs de empleados
  path('empleado_list/', EmpleadoListView.as_view(), name="empleado_list"),
  path('empleado_create/', EmpleadoCreateView.as_view(), name="empleado_create"),
  path('empleado_update/<int:pk>/', EmpleadoUpdateView.as_view(), name='empleado_update'),
  path('empleado_delete/<int:pk>/', EmpleadoDeleteView.as_view(), name='empleado_delete'),
  path('empleado_detail/<int:pk>/', EmpleadoDetailView.as_view(), name='empleado_detail'),

  # URLs de tipo medicina
  path('medicineType_list/', MedicineTypeListView.as_view(), name="medicineType_list"),
  path('medicineType_create/', MedicineTypeCreateView.as_view(), name="medicineType_create"),
  path('medicineType_update/<int:pk>/', MedicineTypeUpdateView.as_view(), name='medicineType_update'),
  path('medicineType_delete/<int:pk>/', MedicineTypeDeleteView.as_view(), name='medicineType_delete'),
  path('medicineType_detail/<int:pk>/', MedicineTypeDetailView.as_view(), name='medicineType_detail'),

  # URLs de medicina
  path('medicine_list/', MedicineListView.as_view(), name="medicine_list"),
  path('medicine_create/', MedicineCreateView.as_view(), name="medicine_create"),
  path('medicine_update/<int:pk>/', MedicineUpdateView.as_view(), name='medicine_update'),
  path('medicine_delete/<int:pk>/', MedicineDeleteView.as_view(), name='medicine_delete'),
  path('medicine_detail/<int:pk>/', MedicineDetailView.as_view(), name='medicine_detail'),

  # URLs de diagnostico
  path('diagnosis_list/', DiagnosisListView.as_view(), name="diagnosis_list"),
  path('diagnosis_create/', DiagnosisCreateView.as_view(), name="diagnosis_create"),
  path('diagnosis_update/<int:pk>/', DiagnosisUpdateView.as_view(), name='diagnosis_update'),
  path('diagnosis_delete/<int:pk>/', DiagnosisDeleteView.as_view(), name='diagnosis_delete'),
  path('diagnosis_detail/<int:pk>/', DiagnosisDetailView.as_view(), name='diagnosis_detail'),

  # URLs de categoria examen
  path('categoryExamen_list/', CategoryExamenListView.as_view(), name="categoryExamen_list"),
  path('categoryExamen_create/', CategoryExamenCreateView.as_view(), name="categoryExamen_create"),
  path('categoryExamen_update/<int:pk>/', CategoryExamenUpdateView.as_view(), name='categoryExamen_update'),
  path('categoryExamen_delete/<int:pk>/', CategoryExamenDeleteView.as_view(), name='categoryExamen_delete'),
  path('categoryExamen_detail/<int:pk>/', CategoryExamenDetailView.as_view(), name='categoryExamen_detail'),

  # URLs de tipo categoria
  path('categoryType_list/', CategoryTypeListView.as_view(), name="categoryType_list"),
  path('categoryType_create/', CategoryTypeCreateView.as_view(), name="categoryType_create"),
  path('categoryType_update/<int:pk>/', CategoryTypeUpdateView.as_view(), name='categoryType_update'),
  path('categoryType_delete/<int:pk>/', CategoryTypeDeleteView.as_view(), name='categoryType_delete'),
  path('categoryType_detail/<int:pk>/', CategoryTypeDetailView.as_view(), name='categoryType_detail'),

  # URLs de auditoria user
  path('auditUser_list/', AuditUserListView.as_view(), name="auditUser_list"),
  path('auditUser_detail/<int:pk>/', AuditUserDetailView.as_view(), name='auditUser_detail'),
]

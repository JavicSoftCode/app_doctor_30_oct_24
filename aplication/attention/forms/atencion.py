# forms.py
from django import forms
from django.forms import ModelForm
from django.forms import inlineformset_factory

from aplication.attention.models import Atencion, DetalleAtencion


# Formulario para el modelo Atencion
class AtencionForm(ModelForm):
  class Meta:
    model = Atencion
    fields = ["paciente", "tratamiento", "motivo_consulta", "diagnostico", "comentario"]

    error_messages = {
      "paciente": {
        "required": "Seleccione un paciente para la atención.",
      },
      "diagnostico": {
        "required": "Seleccione al menos un diagnóstico.",
      },
      "motivo_consulta": {
        "required": "Ingrese el motivo de consulta.",
      },
      "tratamiento": {
        "required": "Ingrese el tratamiento recomendado.",
      },
    }

    widgets = {
      "paciente": forms.Select(
        attrs={
          "id": "id_paciente",
          "class": "shadow-sm bg-gray-50 border border-gray-300 text-gray-900 rounded-lg focus:ring-blue-500 focus:border-blue-500 w-full p-2.5 dark:bg-principal dark:border-gray-600 dark:placeholder-gray-400 dark:text-gray-400 dark:focus:ring-blue-500 dark:focus:border-blue-500",
        }
      ),
      "diagnostico": forms.CheckboxSelectMultiple(
        attrs={
          "id": "id_diagnostico",
          "class": "diagnosticoMultipleSelect"
          # "class": "shadow-sm bg-gray-50 border border-gray-300 text-gray-900 rounded-lg focus:ring-blue-500 focus:border-blue-500 w-full p-2.5 dark:bg-principal dark:border-gray-600 dark:placeholder-gray-400 dark:text-gray-400 dark:focus:ring-blue-500 dark:focus:border-blue-500",
        }
      ),
      "motivo_consulta": forms.TextInput(
        attrs={
          "id": "id_motivo_consulta",

          "placeholder": "Describa",
          "class": "shadow-sm bg-gray-50 border border-gray-300 text-gray-900 rounded-lg focus:ring-blue-500 focus:border-blue-500 w-full p-2.5 dark:bg-principal dark:border-gray-600 dark:placeholder-gray-400 dark:text-gray-400 dark:focus:ring-blue-500 dark:focus:border-blue-500",
          "rows": 4,
        }
      ),
      "tratamiento": forms.TextInput(
        attrs={
          "id": "id_tratamiento",

          "placeholder": "Recomendado",
          "class": "shadow-sm bg-gray-50 border border-gray-300 text-gray-900 rounded-lg focus:ring-blue-500 focus:border-blue-500 w-full p-2.5 dark:bg-principal dark:border-gray-600 dark:placeholder-gray-400 dark:text-gray-400 dark:focus:ring-blue-500 dark:focus:border-blue-500",
          "rows": 4,
        }
      ),
      "comentario": forms.TextInput(
        attrs={
          "id": "id_comentario",

          "placeholder": "Comentarios adicionales",
          "class": "shadow-sm bg-gray-50 border border-gray-300 text-gray-900 rounded-lg focus:ring-blue-500 focus:border-blue-500 w-full p-2.5 dark:bg-principal dark:border-gray-600 dark:placeholder-gray-400 dark:text-gray-400 dark:focus:ring-blue-500 dark:focus:border-blue-500",
          "rows": 3,
        }
      ),
    }

    labels = {
      "paciente": "Paciente",
      "diagnostico": "Diagnósticos",
      "motivo_consulta": "Motivo de Consulta",
      "tratamiento": "Tratamiento",
      "comentario": "Comentario",
    }


# applicacion.attention.forms.atencion.py
# Formulario para el modelo DetalleAtencion
class DetalleAtencionForm(ModelForm):
  class Meta:
    model = DetalleAtencion
    fields = ["medicamento", "cantidad", "prescripcion", "duracion_tratamiento"]

    error_messages = {
      "medicamento": {
        "required": "Seleccione un medicamento.",
      },
      "cantidad": {
        "required": "Ingrese la cantidad del medicamento.",
        "invalid": "Ingrese un valor numérico válido para la cantidad.",
      },
      "prescripcion": {
        "required": "Ingrese la prescripción.",
      },
    }

    widgets = {
      "medicamento": forms.Select(
        attrs={
          "id": "id_medicamento",

          "class": "shadow-sm bg-gray-50 border border-gray-300 text-gray-900 rounded-lg focus:ring-blue-500 focus:border-blue-500 w-full p-2.5 dark:bg-principal dark:border-gray-600 dark:placeholder-gray-400 dark:text-gray-400 dark:focus:ring-blue-500 dark:focus:border-blue-500",
        }
      ),
      "cantidad": forms.NumberInput(
        attrs={
          "id": "id_cantidad",

          "placeholder": "Cantidad",
          "class": "shadow-sm bg-gray-50 border border-gray-300 text-gray-900 rounded-lg focus:ring-blue-500 focus:border-blue-500 w-full p-2.5 dark:bg-principal dark:border-gray-600 dark:placeholder-gray-400 dark:text-gray-400 dark:focus:ring-blue-500 dark:focus:border-blue-500",
        }
      ),
      "prescripcion": forms.TextInput(
        attrs={
          "id": "id_prescripcion",

          "placeholder": "Para el uso medicamento",
          "class": "shadow-sm bg-gray-50 border border-gray-300 text-gray-900 rounded-lg focus:ring-blue-500 focus:border-blue-500 w-full p-2.5 dark:bg-principal dark:border-gray-600 dark:placeholder-gray-400 dark:text-gray-400 dark:focus:ring-blue-500 dark:focus:border-blue-500",
          "rows": 3,
        }
      ),
      "duracion_tratamiento": forms.NumberInput(
        attrs={
          "id": "id_duracion_tratamiento",

          "placeholder": "Duración en días",
          "class": "shadow-sm bg-gray-50 border border-gray-300 text-gray-900 rounded-lg focus:ring-blue-500 focus:border-blue-500 w-full p-2.5 dark:bg-principal dark:border-gray-600 dark:placeholder-gray-400 dark:text-gray-400 dark:focus:ring-blue-500 dark:focus:border-blue-500",
        }
      ),
    }

    labels = {
      "medicamento": "Medicamento",
      "cantidad": "Cantidad",
      "prescripcion": "Indicaciones",
      "duracion_tratamiento": "Duración del Tratamiento (días)",
    }


# Define el formset usando el modelo y formulario correspondientes
DetalleAtencionFormset = inlineformset_factory(
    Atencion,
    DetalleAtencion,
    form=DetalleAtencionForm,
    extra=1,
    can_delete=True  # Esto es importante
)

from django import forms
from django.forms import ModelForm
from django.forms import inlineformset_factory

from aplication.attention.models import Atencion, DetalleAtencion


class AtencionForm(ModelForm):
  class Meta:
    model = Atencion
    fields = [
      "paciente",
      "tratamiento",
      "motivo_consulta",
      "diagnostico",
      "comentario"
    ]

    error_messages = {
      "paciente": {
        "required": "Seleccionar paciente ⚠️.",
      },
      "diagnostico": {
        "required": "Seleccionar al menos un diagnóstico ⚠️.",
      },
      "motivo_consulta": {
        "required": "Ingresar el motivo de la atención ⚠️.",
      },
      "tratamiento": {
        "required": "Ingresar tratamiento recomendado ⚠️.",
      },
      "comentario": {
        "required": "Ingresar comentario adicional ⚠️.",
      },
    }

    widgets = {
      "paciente": forms.Select(attrs={
        "id": "id_paciente",
        "class": "shadow-sm bg-gray-50 border border-gray-300 text-gray-900 rounded-lg focus:ring-blue-500 focus:border-blue-500 w-full p-2.5 dark:bg-principal dark:border-gray-600 dark:placeholder-gray-400 dark:text-gray-400 dark:focus:ring-blue-500 dark:focus:border-blue-500"},
      ),
      "diagnostico": forms.CheckboxSelectMultiple(attrs={
        "id": "id_diagnostico",
        "class": "diagnosticoMultipleSelect"},
      ),
      "motivo_consulta": forms.TextInput(attrs={
        "id": "id_motivo_consulta",
        "placeholder": "Ingresar motivo de la consulta.",
        "class": "shadow-sm bg-gray-50 border border-gray-300 text-gray-900 rounded-lg focus:ring-blue-500 focus:border-blue-500 w-full p-2.5 dark:bg-principal dark:border-gray-600 dark:placeholder-gray-400 dark:text-gray-400 dark:focus:ring-blue-500 dark:focus:border-blue-500",
        "rows": 4},
      ),
      "tratamiento": forms.TextInput(attrs={
        "id": "id_tratamiento",
        "placeholder": "Ingresar tratamiento recomendado.",
        "class": "shadow-sm bg-gray-50 border border-gray-300 text-gray-900 rounded-lg focus:ring-blue-500 focus:border-blue-500 w-full p-2.5 dark:bg-principal dark:border-gray-600 dark:placeholder-gray-400 dark:text-gray-400 dark:focus:ring-blue-500 dark:focus:border-blue-500",
        "rows": 3},
      ),
      "comentario": forms.TextInput(attrs={
        "id": "id_comentario",
        "placeholder": "Ingresar comentarios adicionales.",
        "class": "shadow-sm bg-gray-50 border border-gray-300 text-gray-900 rounded-lg focus:ring-blue-500 focus:border-blue-500 w-full p-2.5 dark:bg-principal dark:border-gray-600 dark:placeholder-gray-400 dark:text-gray-400 dark:focus:ring-blue-500 dark:focus:border-blue-500",
        "rows": 3},
      ),
    }

    labels = {
      "paciente": "Paciente",
      "diagnostico": "Diagnósticos",
      "motivo_consulta": "Motivo de Consulta",
      "tratamiento": "Tratamiento",
      "comentario": "Comentario",
    }


class DetalleAtencionForm(ModelForm):
  class Meta:
    model = DetalleAtencion
    fields = [
      "medicamento",
      "cantidad",
      "prescripcion",
      "duracion_tratamiento"
    ]

    error_messages = {
      "medicamento": {
        "required": "Seleccionar al menos un medicamento ⚠️.",
      },
      "cantidad": {
        "required": "Ingresar la cantidad del medicamento ⚠️.",
        "invalid": "Ingresar un valor numérico válido para la cantidad ⚠️.",
      },
      "prescripcion": {
        "required": "Ingresar la prescripción ⚠️.",
      },
      "duracion_tratamiento": {
        "required": "Ingresar los días que dura el tratamiento ⚠️.",
      },
    }

    widgets = {
      "medicamento": forms.Select(attrs={
        "id": "id_medicamento",
        "class": "shadow-sm bg-gray-50 border border-gray-300 text-gray-900 rounded-lg focus:ring-blue-500 focus:border-blue-500 w-full p-2.5 dark:bg-principal dark:border-gray-600 dark:placeholder-gray-400 dark:text-gray-400 dark:focus:ring-blue-500 dark:focus:border-blue-500"},
      ),
      "cantidad": forms.NumberInput(attrs={
        "id": "id_cantidad",
        "placeholder": "Ingresar cantidad del medicamento.",
        "class": "shadow-sm bg-gray-50 border border-gray-300 text-gray-900 rounded-lg focus:ring-blue-500 focus:border-blue-500 w-full p-2.5 dark:bg-principal dark:border-gray-600 dark:placeholder-gray-400 dark:text-gray-400 dark:focus:ring-blue-500 dark:focus:border-blue-500"},
      ),
      "prescripcion": forms.TextInput(attrs={
        "id": "id_prescripcion",
        "placeholder": "Ingresar la prescripción.",
        "class": "shadow-sm bg-gray-50 border border-gray-300 text-gray-900 rounded-lg focus:ring-blue-500 focus:border-blue-500 w-full p-2.5 dark:bg-principal dark:border-gray-600 dark:placeholder-gray-400 dark:text-gray-400 dark:focus:ring-blue-500 dark:focus:border-blue-500",
        "rows": 3},
      ),
      "duracion_tratamiento": forms.NumberInput(attrs={
        "id": "id_duracion_tratamiento",
        "placeholder": "Ingresar los días del tratamiento.",
        "class": "shadow-sm bg-gray-50 border border-gray-300 text-gray-900 rounded-lg focus:ring-blue-500 focus:border-blue-500 w-full p-2.5 dark:bg-principal dark:border-gray-600 dark:placeholder-gray-400 dark:text-gray-400 dark:focus:ring-blue-500 dark:focus:border-blue-500"},
      ),
    }

    labels = {
      "medicamento": "Medicamento",
      "cantidad": "Cantidad",
      "prescripcion": "Prescripción",
      "duracion_tratamiento": "Duración del Tratamiento (días)",
    }


DetalleAtencionFormsetCreate = inlineformset_factory(
  Atencion,
  DetalleAtencion,
  form=DetalleAtencionForm,
  extra=1,
  # extra=1,
  can_delete=True
)

# Define el formset usando el modelo y formulario correspondientes
DetalleAtencionFormset = inlineformset_factory(
  Atencion,
  DetalleAtencion,
  form=DetalleAtencionForm,
  extra=0,
  # extra=1,
  can_delete=True
)

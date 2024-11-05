from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView, DeleteView, DetailView

from aplication.core.forms.categoryExamen import CategoryExamenForm
from aplication.core.models import CategoriaExamen
from doctor.utils import save_audit


class CategoryExamenListView(ListView):
  template_name = "core/categoryExamen/list.html"
  model = CategoriaExamen
  context_object_name = 'categorias_examen'
  paginate_by = 5
  query = None

  def get_queryset(self):
    self.query = Q()
    q1 = self.request.GET.get('q')  # Texto de búsqueda
    categoryExamen = self.request.GET.get('categoryExamen')  # Estado activo o inactivo

    if q1:
      if q1.isdigit():
        self.query.add(Q(id=q1), Q.AND)

      else:
        # Filtra por nombre que contenga el valor ingresado en 'q'
        self.query.add(Q(nombre__icontains=q1), Q.AND)

    if categoryExamen in ["True", "False"]:
      # Filtra por el valor booleano de activo
      is_active = categoryExamen == "True"  # Convierte a booleano
      self.query.add(Q(activo=is_active), Q.AND)

    return self.model.objects.filter(self.query).order_by('nombre')

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context['title1'] = "Listado de Categorías Examen"
    context['title2'] = "Nueva Categoría Examen"
    return context


class CategoryExamenCreateView(CreateView):
  model = CategoriaExamen
  template_name = 'core/categoryExamen/form.html'
  form_class = CategoryExamenForm
  success_url = reverse_lazy('core:categoryExamen_list')

  def get_context_data(self, **kwargs):
    context = super().get_context_data()
    context['title1'] = 'Crear Categoría Examen'
    context['grabar'] = 'Grabar Categoría Examen'
    context['back_url'] = self.success_url
    return context

  def form_valid(self, form):
    response = super().form_valid(form)
    objAudit = self.object
    save_audit(self.request, objAudit, action='A')
    messages.success(self.request, f"Éxito al Crear la Categoría Examen {objAudit.nombre}.")
    return response

  # def form_valid(self, form):
  #   if hasattr(self.request, 'user') and self.request.user.is_authenticated:
  #     form.instance.usuario = self.request.user
  #   else:
  #     # Asigna un valor alternativo o evita la asignación si el usuario no está autenticado
  #     form.instance.usuario = None  # O el valor que consideres adecuado
  #     messages.success(self.request, f"Éxito al Crear la Categoría Examen.")
  #
  #   return super().form_valid(form)

  def form_invalid(self, form):
    messages.error(self.request, "Error al enviar el formulario. Corrige los errores.")
    print(form.errors)
    return self.render_to_response(self.get_context_data(form=form))


class CategoryExamenUpdateView(UpdateView):
  model = CategoriaExamen
  template_name = 'core/categoryExamen/form.html'
  form_class = CategoryExamenForm
  success_url = reverse_lazy('core:categoryExamen_list')

  def get_context_data(self, **kwargs):
    context = super().get_context_data()
    context['title1'] = 'Actualizar Categoría de Examen'
    context['grabar'] = 'Actualizar Categoría de Examen'
    context['back_url'] = self.success_url
    return context

  def form_valid(self, form):
    response = super().form_valid(form)
    objAudit = self.object
    save_audit(self.request, objAudit, action='M')
    messages.success(self.request, f"Éxito al Modificar la Categoría Examen {objAudit.nombre}.")
    return response

  # def form_valid(self, form):
  #   categoryExamen = self.object
  #   if hasattr(self.request, 'user') and self.request.user.is_authenticated:
  #     form.instance.usuario = self.request.user
  #   else:
  #     # Asigna un valor alternativo o evita la asignación si el usuario no está autenticado
  #     form.instance.usuario = None  # O el valor que consideres adecuado
  #     messages.success(self.request, f"Éxito al Modificar la Categorpía de Examen {categoryExamen.nombre}.")
  #
  #   return super().form_valid(form)

  def form_invalid(self, form):
    messages.error(self.request, "Error al Modificar el formulario. Corrige los errores.")
    print(form.errors)
    return self.render_to_response(self.get_context_data(form=form))


class CategoryExamenDeleteView(DeleteView):
  model = CategoriaExamen
  success_url = reverse_lazy('core:categoryExamen_list')

  def get_context_data(self, **kwargs):
    context = super().get_context_data()
    context['grabar'] = 'Eliminar Categoría Examen'
    context['description'] = f"¿Desea Eliminar la Categoría Examen: {self.object.nombre}?"
    return context

  def delete(self, request, *args, **kwargs):
    self.object = self.get_object()
    success_message = f"Éxito al eliminar lógicamente la Categoría de Examen {self.object.nombre}."
    messages.success(self.request, success_message)
    # Cambiar el estado de eliminado lógico
    # self.object.deleted = True
    # self.object.save()
    return super().delete(request, *args, **kwargs)


class CategoryExamenDetailView(DetailView):
  model = CategoriaExamen
  extra_context = {
    "detail": "Detalles de la Categoría de Examen"
  }

  def get(self, request, *args, **kwargs):
    categoryExamen = self.get_object()
    data = {
      'id': categoryExamen.id,
      'nombre': categoryExamen.nombre,
      'descripcion': categoryExamen.descripcion,
      'activo': categoryExamen.activo,
    }
    return JsonResponse(data)

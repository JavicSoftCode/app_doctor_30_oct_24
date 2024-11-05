from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView, DeleteView, DetailView

from aplication.core.forms.categoryType import CategoryTypeForm
from aplication.core.models import TipoCategoria
from doctor.utils import save_audit


class CategoryTypeListView(ListView):
    template_name = "core/categoryType/list.html"
    model = TipoCategoria
    context_object_name = 'tipos_categorias'
    paginate_by = 5
    query = None

    def get_queryset(self):
        self.query = Q()
        q1 = self.request.GET.get('q')  # Texto de búsqueda
        is_active = self.request.GET.get('activo')  # Estado activo o inactivo

        if q1:
            if q1.isdigit():
                self.query.add(Q(id=q1), Q.AND)

            else:
                # Filtra por nombre que contenga el valor ingresado en 'q'
                self.query.add(Q(nombre__icontains=q1), Q.AND)

        if is_active in ["True", "False"]:
            # Filtra por el valor booleano de activo
            self.query.add(Q(activo=(is_active == "True")), Q.AND)

        return self.model.objects.filter(self.query).order_by('nombre')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title1'] = "Listado de Tipos de Exámenes"
        context['title2'] = "Nuevo Tipo de Examen"
        return context


class CategoryTypeCreateView(CreateView):
    model = TipoCategoria
    template_name = 'core/categoryType/form.html'
    form_class = CategoryTypeForm
    success_url = reverse_lazy('core:categoryType_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['title1'] = 'Crear Tipo de Examen'
        context['grabar'] = 'Grabar Tipo de Examen'
        context['back_url'] = self.success_url
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        objAudit = self.object
        save_audit(self.request, objAudit, action='A')
        messages.success(self.request, f"Éxito al Crear el Tipo Categoria {objAudit.nombre}.")
        return response

    # def form_valid(self, form):
    #     if hasattr(self.request, 'user') and self.request.user.is_authenticated:
    #         form.instance.usuario = self.request.user
    #     else:
    #         form.instance.usuario = None
    #     messages.success(self.request, "Éxito al crear el Tipo de Examen.")
    #     return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Error al enviar el formulario. Corrige los errores.")
        print(form.errors)
        return self.render_to_response(self.get_context_data(form=form))


class CategoryTypeUpdateView(UpdateView):
    model = TipoCategoria
    template_name = 'core/categoryType/form.html'
    form_class = CategoryTypeForm
    success_url = reverse_lazy('core:categoryType_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['title1'] = 'Actualizar Tipo de Examen'
        context['grabar'] = 'Actualizar Tipo de Examen'
        context['back_url'] = self.success_url
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        objAudit = self.object
        save_audit(self.request, objAudit, action='M')
        messages.success(self.request, f"Éxito al Modificar el Tipo Categoria {objAudit.nombre}.")
        return response

    def form_invalid(self, form):
        messages.error(self.request, "Error al modificar el formulario. Corrige los errores.")
        print(form.errors)
        return self.render_to_response(self.get_context_data(form=form))


class CategoryTypeDeleteView(DeleteView):
    model = TipoCategoria
    success_url = reverse_lazy('core:categoryType_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['grabar'] = 'Eliminar Tipo de Examen'
        context['description'] = f"¿Desea eliminar el Tipo de Examen: {self.object.nombre}?"
        return context

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_message = f"Éxito al eliminar lógicamente el Tipo de Examen {self.object.nombre}."
        messages.success(self.request, success_message)
        return super().delete(request, *args, **kwargs)


class CategoryTypeDetailView(DetailView):
    model = TipoCategoria
    extra_context = {
        "detail": "Detalles del Tipo de Examen"
    }

    def get(self, request, *args, **kwargs):
        tipo_categoria = self.get_object()
        data = {
            'id': tipo_categoria.id,
            'categoria_examen': tipo_categoria.categoria_examen.nombre,  # assuming CategoriaExamen has 'nombre' attribute
            'nombre': tipo_categoria.nombre,
            'descripcion': tipo_categoria.descripcion,
            'valor_minimo': tipo_categoria.valor_minimo,
            'valor_maximo': tipo_categoria.valor_maximo,
            'activo': tipo_categoria.activo,
        }
        return JsonResponse(data)

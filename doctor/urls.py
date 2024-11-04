from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
                path('admin/', admin.site.urls),
                path('', include('aplication.core.urls', namespace='core')),
                path('', include('aplication.attention.urls', namespace='attention')),

              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)  # configuracion imagenes

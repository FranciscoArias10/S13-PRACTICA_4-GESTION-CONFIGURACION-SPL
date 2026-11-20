"""Enrutamiento raíz con include() condicional por variante SPL (Sesión 3)."""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('accounts/', include('accounts.urls')),
    path('files/', include('file_manager.urls')),
]

# Ruteo condicional para funcionalidades opcionales de la línea de productos
if settings.ENABLE_REPORTS:
    urlpatterns.append(path('reports/', include('reports.urls')))

if settings.ENABLE_NOTIFICATIONS:
    urlpatterns.append(path('notifications/', include('notifications.urls')))

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

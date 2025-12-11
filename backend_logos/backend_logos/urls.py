from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic.base import RedirectView

# Importar las vistas de autenticación directamente desde la app
from app_logos import views as app_views

urlpatterns = [
    path('admin/', admin.site.urls),

    # --- RUTAS DE AUTENTICACIÓN CENTRALIZADAS ---
    # Se mueven aquí para asegurar que tengan la máxima prioridad y no sean ignoradas.
    path('login/', app_views.login_view, name='login'),
    path('logout/', app_views.logout_view, name='logout'),
    
    # Redirección de seguridad para el problema persistente de /accounts/login/
    path('accounts/login/', RedirectView.as_view(url='/login/', permanent=True)),

    # Incluir el resto de las URLs de la aplicación
    path('', include('app_logos.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

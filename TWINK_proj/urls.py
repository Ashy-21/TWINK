from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from chat import views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.welcome_view, name='welcome'),
    path('chat/', include('chat.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

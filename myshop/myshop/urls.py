from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from shopapp.views import LoginView, RegisterView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('shopapp.urls')),
    # Временные URL для входа/регистрации (замените на свои)
    path('login/', LoginView.as_view(), name='login'),
    path('register/', RegisterView.as_view(), name='register'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
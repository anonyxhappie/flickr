from django.contrib import admin
from django.urls import path, include

from django.conf import settings
from django.conf.urls.static import static

from rest_framework_swagger.views import get_swagger_view

from flickr_api import views

urlpatterns = [
    path('', get_swagger_view(title='Flickr-Clone API')),
    path('admin/', admin.site.urls),
    path('api/v1/', include('flickr_api.urls')),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
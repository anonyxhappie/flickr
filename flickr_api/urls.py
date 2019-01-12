from django.urls import path, include
from django.conf.urls import url

from rest_framework.routers import DefaultRouter
from rest_auth.views import LoginView, LogoutView

from .views import *

router = DefaultRouter()
router.register(r'groups', GroupViewSet, basename='group')
router.register(r'photos', PhotoViewSet, basename='photo')

urlpatterns = [  
    url(r'^login/$', LoginView.as_view(), name='rest_login'),
    url(r'^logout/$', LogoutView.as_view(), name='rest_logout'),
    url(r'^', include(router.urls)),

    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]
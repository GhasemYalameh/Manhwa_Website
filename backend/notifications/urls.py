from django.urls import include, path
from . import views
from rest_framework import routers

router = routers.DefaultRouter()
router.register('notifications', views.NotificationViewSet, basename='notification')


urlpatterns = [
    path('', include(router.urls)),
    # path('notifications/', views.NotificationViewSet.as_view(), name='notifications'),
]
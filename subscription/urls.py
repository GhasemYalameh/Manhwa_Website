from django.urls import path

from . import views


urlpatterns = [
    path('', views.SubscriptionApi.as_view(), name='subscription'),
    path('verify/', views.subscription_verify, name='subscription-verify'),
]
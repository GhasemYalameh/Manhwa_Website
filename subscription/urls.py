from django.urls import path

from . import views


urlpatterns = [
    path('', views.SubscriptionApi.as_view(), name='subscription'),
    path('verify/', views.subscription_verify, name='subscription-verify'),
    path('plan/', views.subscription_plan_list, name='subscription-plan-list')
]
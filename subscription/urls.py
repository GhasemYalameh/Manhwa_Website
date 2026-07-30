from django.urls import path

from . import views


urlpatterns = [
    path('', views.SubscriptionApi.as_view(), name='subscription'),
    path('verify/', views.SubscriptionVerify.as_view(), name='subscription-verify'),
    path('plan/', views.SubscriptionPlanList.as_view(), name='subscription-plan-list')
]
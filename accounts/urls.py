from django.urls import path

from . import views

urlpatterns = [
    path('profile/', views.profile_view, name='signup'),
    path('otp/', views.GenerateOTPView.as_view()),
    path('otp/verify/', views.VerifyOTPView.as_view()),
]

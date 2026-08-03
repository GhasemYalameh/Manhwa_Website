from django.urls import path

from . import views

urlpatterns = [
    path('otp/', views.GenerateOTPApiView.as_view()),
    path('otp/verify/', views.VerifyOTPApiView.as_view()),
    path('login/password/', views.LoginWithPasswordApiView.as_view()),
    path('signin/password/', views.SignInWithPasswordApiView.as_view()),
]

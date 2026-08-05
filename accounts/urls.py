from django.urls import path

from . import views

urlpatterns = [
    path('otp/', views.GenerateOTPApiView.as_view(), name='generate-otp'),
    path('otp/verify/', views.VerifyOTPApiView.as_view(), name='verify-otp'),
    path('otp/completion/', views.CompleteSignInWithOTPApiView.as_view(), name='complete-signin-otp'),
    path('login/password/', views.LoginWithPasswordApiView.as_view(), name='login-pass'),
    path('signin/password/', views.SignInWithPasswordApiView.as_view(), name='signin-pass'),
]

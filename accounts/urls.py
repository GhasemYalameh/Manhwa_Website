from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView, TokenBlacklistView, TokenVerifyView

from . import views

urlpatterns = [
    path('jwt/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('jwt/verify/', TokenVerifyView.as_view(), name='token-verify'),
    path('jwt/blacklist/', TokenBlacklistView.as_view(), name='token-blacklist'),

    path('otp/', views.GenerateOTPApiView.as_view(), name='generate-otp'),
    path('otp/verify/', views.VerifyOTPApiView.as_view(), name='verify-otp'),
    path('otp/completion/', views.CompleteSignUpWithOTPApiView.as_view(), name='complete-signin-otp'),
    path('login/password/', views.LoginWithPasswordApiView.as_view(), name='login-pass'),
    path('signup/password/', views.SignUpWithPasswordApiView.as_view(), name='signin-pass'),
]

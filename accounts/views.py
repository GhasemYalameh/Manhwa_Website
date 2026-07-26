from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib import messages
from django.utils.translation import gettext as _
from rest_framework import status

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .forms import CustomUserCreationForm, CustomAuthenticationForm
from .models import CustomUser
from .services import OTP



class CustomLoginView(LoginView):
    form_class = CustomAuthenticationForm
    template_name = 'registration/login.html'

    def form_valid(self, form):
        messages.success(self.request, 'با موفقیت وارد شدید!')
        return super().form_valid(form)


class CustomLogoutView(LogoutView):
    def dispatch(self, request, *args, **kwargs):
        messages.success(request, _('successfully you are logged out'))
        return super().dispatch(request, *args, **kwargs)


def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # خودکار لاگین کردن بعد از ثبت نام
            phone_number = form.cleaned_data.get('phone_number')
            password = form.cleaned_data.get('password1')
            user = authenticate(phone_number=phone_number, password=password)
            if user:
                login(request, user)
                messages.success(request, 'حساب کاربری شما با موفقیت ایجاد شد!')
                return redirect('home')  # به home page برو
    else:
        form = CustomUserCreationForm()

    return render(request, 'registration/register.html', {'form': form})


def profile_view(request):
    # watch_list = CustomUser.objects.prefetch_related('watch_list').filter(id=request.user.id)

    return render(request, 'accounts/profile.html',)


class GenerateOTPView(APIView):
    def post(self, request):
        phone_number = request.data.get('phone_number')
        otp = OTP(phone_number)  # creating otp object.

        if otp.is_blacklisted():  # check if user in blacklist
            return Response('your now in blacklist. please try again later', status=status.HTTP_403_FORBIDDEN)

        if not otp.is_valid_phone_number():  # check phone number validation
            return Response('phone number is not valid.', status=status.HTTP_400_BAD_REQUEST)

        if not CustomUser.objects.filter(phone_number=phone_number).exists():  # check user with this phone number is exist
            return Response('there no any account with this phone number. please sign up first. ', status=status.HTTP_400_BAD_REQUEST)

        otp_code = otp.generate_otp_code()
        self.send_sms(phone_number, otp_code)  # sms the otp here

        return Response('your otp code generated. please send it to us for verification', status=status.HTTP_201_CREATED)

    def get(self, request):
        return Response('send your Phone number with post methode.')

    def send_sms(self, phone_number, otp_code):
        print("#" * 100)
        print(f"your otp code is: {otp_code}".upper())
        print("#" * 100)


class VerifyOTPView(APIView):
    def post(self, request):
        otp_code = request.data.get('otp_code')
        phone_number = request.data.get('phone_number')

        otp = OTP(phone_number)  # creating otp object.

        if not (otp.is_valid_otp_code(otp_code) and otp.is_valid_phone_number()):
            return Response('phone number or OTP code is not valid.', status=status.HTTP_400_BAD_REQUEST)

        is_verified = otp.verify_otp_code(otp_code)
        if is_verified:
            otp.delete_cached_keys()
            user = get_object_or_404(CustomUser, phone_number=phone_number)
            refresh = RefreshToken.for_user(user)
            return Response({'refresh_token': str(refresh), 'access_token': str(refresh.access_token)})

        attempt_count = otp.check_attempts()
        if attempt_count == -1:
            return Response('you are added to blacklist because of most attempt.', status=status.HTTP_403_FORBIDDEN)

        return Response(f'incorrect OTP code!. remaining attempt is : {otp.MAX_ATTEMPTS - attempt_count + 1}', status=status.HTTP_400_BAD_REQUEST)
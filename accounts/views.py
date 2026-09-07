from djoser import serializers
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated

from accounts.services.otp import BlackListManager
from .models import CustomUser
from .services import OTP
from .serializers import (
    CompleteSignUpWithOTPSerializer, GetPhoneNumberSerializer, LoginWithPasswordSerializer, GetMeSerializer, 
    OTPCodeVerifySerializer, PatchMeSerializer,  SignUpWithPasswordSerializer,
)


class MeApiView(APIView):
    permission_classes=[IsAuthenticated]

    def get(self, request):
        user = CustomUser.objects.prefetch_related('subscription').get(pk=request.user.id)
        serializer = GetMeSerializer(user)
        return Response(serializer.data)

    def patch(self, request):
        serializer = PatchMeSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class GenerateOTPApiView(APIView):
    """
    generating OTP and send via sms.
    """
    def post(self, request):
        serializer = GetPhoneNumberSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone_number = serializer.validated_data['phone_number']
        otp = OTP(phone_number)

        if otp.is_blacklisted():  # check if user in blacklist
            return Response('your now in blacklist. please try again later', status=status.HTTP_403_FORBIDDEN)

        otp_code = otp.generate_otp_code()
        if not otp_code:
            return Response('the OTP code is already generated. please send it for verification.', status=status.HTTP_406_NOT_ACCEPTABLE)

        otp.send_sms(otp_code)  # sms the otp here
        return Response('your otp code generated. please send it to us for verification', status=status.HTTP_201_CREATED)


class VerifyOTPApiView(APIView):
    """
    verify otp code and register user.
    returns access token and refresh token.
    """
    def post(self, request):
        serializer = OTPCodeVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone_number = serializer.validated_data['phone_number']
        otp = serializer.validated_data['otp']
        otp_service = OTP(phone_number)  

        if otp_service.is_blacklisted():  # check if user in blacklist
            return Response('your now in blacklist. please try again later', status=status.HTTP_403_FORBIDDEN)

        # Wrong OTP code condition
        is_verified = otp_service.verify_otp_code(otp)
        if not is_verified:
            attempt_count = otp_service.check_attempts()
            if attempt_count == -1:
                return Response('you are added to blacklist because of most attempt.', status=status.HTTP_403_FORBIDDEN)

            return Response(f'incorrect OTP code!. remaining attempt is : {otp_service.max_attempts - attempt_count}', status=status.HTTP_400_BAD_REQUEST)

        otp_service.delete_cached_keys()

        user_query = CustomUser.objects.filter(phone_number=phone_number)
        user = user_query.first() if user_query.exists() else CustomUser.objects.create_user_via_otp(phone_number=phone_number)
        is_new_user = user.is_new_user
        refresh = RefreshToken.for_user(user)
        return Response(
            {
                'refresh_token': str(refresh),
                'access_token': str(refresh.access_token),
                'is_new_user': is_new_user,
            },
            status=status.HTTP_200_OK
        )


class CompleteSignUpWithOTPApiView(APIView):
    """
    after creating new user, user must redirected to this view for completion of signin.
    """
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = CompleteSignUpWithOTPSerializer(data=request.data, instance=request.user, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(is_new_user=False)
        return Response('sign up completed', status=status.HTTP_200_OK)


class SignUpWithPasswordApiView(APIView):
    def post(self, request):
        serializer = SignUpWithPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response({"refresh_token": str(refresh), "access_token": str(refresh.access_token)}, status=status.HTTP_200_OK)


class LoginWithPasswordApiView(APIView):
    def post(self, request):
        serializer = LoginWithPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone_number = serializer.validated_data['phone_number']
        password = serializer.validated_data['password']

        # user blacklisted condition
        blk_service = BlackListManager(phone_number)
        if blk_service.is_blacklisted():
            return Response("you are black listed now. please try again later.", status=status.HTTP_403_FORBIDDEN)

        # wrong password condition
        user = CustomUser.objects.get(phone_number=phone_number)
        if not user.check_password(password):
            attempts_count = blk_service.check_attempts()
            if attempts_count == -1:
                return Response('you added to black list  because of many wrong attempts.', status=status.HTTP_400_BAD_REQUEST)
            return Response(
                f'invalid password. remaining attempts: {blk_service.max_attempts - attempts_count}',
                status=status.HTTP_400_BAD_REQUEST
            )
        
        refresh = RefreshToken.for_user(user)
        return Response({"refresh_token": str(refresh), "access_token": str(refresh.access_token)}, status=status.HTTP_200_OK)
        
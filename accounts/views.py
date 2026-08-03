from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .models import CustomUser
from .services import OTP
from .serializers import GetPhoneNumberSerializer, LoginWithPasswordSerializer, OTPCodeVerifySerializer, SignInWithPasswordSerializer


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
        otp_service = OTP(phone_number)  # creating otp object.
        is_verified = otp_service.verify_otp_code(otp)

        if not is_verified:
            attempt_count = otp_service.check_attempts()
            if attempt_count == -1:
                return Response('you are added to blacklist because of most attempt.', status=status.HTTP_403_FORBIDDEN)

            return Response(f'incorrect OTP code!. remaining attempt is : {otp_service.MAX_ATTEMPTS - attempt_count + 1}', status=status.HTTP_400_BAD_REQUEST)

        otp_service.delete_cached_keys()
        user_query = CustomUser.objects.filter(phone_number=phone_number)
        # login or signin
        user = user_query.first() if user_query.exists() else CustomUser.objects.create_user(phone_number=phone_number)
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


class SignInWithPasswordApiView(APIView):
    def post(self, request):
        serializer = SignInWithPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        if CustomUser.objects.filter(phone_number=data['phone_number']).exists():
            return Response('an user with this phone number is already exist. please login.', status=status.HTTP_400_BAD_REQUEST)
        
        user = CustomUser.objects.create_user(
            phone_number = getattr(data, "phone_number"),
            first_name=getattr(data, "first_name"),
            last_name=getattr(data, "last_name", ""),
            email=getattr(data, "email", ""),
            password=getattr(data, "password")
        )
        refresh = RefreshToken.for_user(user)
        return Response({"refresh_token": str(refresh), "access_token": str(refresh.access_token)}, status=status.HTTP_200_OK)


class LoginWithPasswordApiView(APIView):
    def post(self, request):
        serializer = LoginWithPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        user_query = CustomUser.objects.filter(phone_number=data['phone_number'])
        if not user_query.exists():
            return Response('user with that phone number is not exist. please sign in.', status=status.HTTP_400_BAD_REQUEST)

        refresh = RefreshToken.for_user(user_query.first())
        return Response({"refresh_token": str(refresh), "access_token": str(refresh.access_token)}, status=status.HTTP_200_OK)
        
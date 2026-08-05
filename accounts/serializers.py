from django.core.validators import RegexValidator, 
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from .models import CustomUser

phone_regex = RegexValidator(
    regex=r"^09\d{9}$",
    message="phone number is not valid."
)
otp_regex = RegexValidator(
    regex=r"^\d+$",
    message="OTP must contain only numbers and const length."
)


def pass_validation(value):
    try:
        validate_password(value)
    except DjangoValidationError as e:
        raise serializers.ValidationError(list(e.messages))


class GetPhoneNumberSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=11, validators=[phone_regex,])


class OTPCodeVerifySerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=11, validators=[phone_regex])
    otp = serializers.CharField(max_length=8, validators=[otp_regex])


class SignUpWithPasswordSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=11, validators=[phone_regex,])
    first_name = serializers.CharField(max_length=25)
    last_name = serializers.CharField(max_length=25, required=False)
    email = serializers.EmailField(required=False)
    password = serializers.CharField(required=True, write_only=True, validators=[pass_validation,])
    password2 = serializers.CharField(required=True, write_only=True)

    def validate_phone_number(self, value):
        if CustomUser.objects.filter(phone_number=value).exists():
            raise serializers.ValidationError('an user with this phone number is already exist. please login.')
        return value
    
    def validate(self, fields):
        if fields.get('password') != fields.get('password2'):
            raise serializers.ValidationError({"password2": "passwords not same."})
        return fields


class LoginWithPasswordSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=11, validators=[phone_regex,])
    password = serializers.CharField(required=True, write_only=True, validators=[pass_validation,])

    def validate_phone_number(self, value):
        if not CustomUser.objects.filter(phone_number=value).exists():
            raise serializers.ValidationError('user with that phone number is not exist. please signup first.')
        return value

    
class CompleteSignUpWithOTPSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=25)
    last_name = serializers.CharField(max_length=25, required=False)
    email = serializers.EmailField(required=False)

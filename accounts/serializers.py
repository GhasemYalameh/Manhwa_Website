from django.core.validators import RegexValidator
from rest_framework import serializers

phone_regex = RegexValidator(
    regex=r"^09\d{9}$",
    message="phone number is not valid."
)
otp_regex = RegexValidator(
    regex=r"^\d+$",
    message="OTP must contain only numbers and const length."
)


class GetPhoneNumberSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=11, validators=[phone_regex,])


class OTPCodeVerifySerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=11, validators=[phone_regex])
    otp = serializers.CharField(max_length=8, validators=[otp_regex])


from unittest import expectedFailure

from rest_framework_simplejwt.tokens import RefreshToken
from django_redis import get_redis_connection
import secrets
from re import fullmatch

OTP_DEFAULT_LENGTH = 5
OTP_TTL = 120
ATTEMPT_TTL = 300
BLACKLIST_TTL = 180
MAX_ATTEMPTS = 3

def create_otp(length:int=OTP_DEFAULT_LENGTH)-> str:
    otp_string = ''.join(secrets.choice('0123456789') for _ in range(length))
    return otp_string

class OTP:
    def __init__(self, phone_number):
        self.redis = get_redis_connection('default')
        self.otp_key = 'otp:{}'  # fill with phone_number
        self.otp_attempt_key = 'otp:attempt:{}'
        self.otp_blackList_key = 'otp:blacklist:{}'
        self.phone_number = phone_number

    def generate_otp_code(self, length=None):
        """Generating the OTP code. Returns None if the user condition is missed. else returns otp_code"""
        if length is None:
            length = OTP_DEFAULT_LENGTH

        if self.is_blacklisted():
            return None

        otp_key = self.otp_key.format(self.phone_number)
        if not self.redis.exists(otp_key):
            otp_code = create_otp(length)
            self.redis.set(otp_key, otp_code, ex=OTP_TTL)
            return otp_code

        return None

    def check_otp_code(self, user_otp_code):
        otp_key = self.otp_key.format(self.phone_number)
        expected_otp_code = self.redis.get(otp_key) # decoding otp_code to string

        if expected_otp_code and secrets.compare_digest(expected_otp_code.decode() , user_otp_code):
            return True

        return False

    def verify_otp_code(self, otp_code):
        otp_attempt_key = self.otp_attempt_key.format(self.phone_number)
        otp_key = self.otp_key.format(self.phone_number)
        response = {
            'user_status': 'blacklisted',  # not verified or verified
            'remaining_attempts': 0,
        }

        if self.is_blacklisted():  # checking phone number limit
           return response

        if not self.check_otp_code(otp_code):  # if otp code is not true
            attempts_count = self.check_attempts()
            response['remaining_attempts'] -= attempts_count

        # if verify is true
        self.redis.delete(otp_attempt_key)
        self.redis.delete(otp_key)
        return True

    def check_attempts(self):
        otp_attempt_key = self.otp_attempt_key.format(self.phone_number)
        attempt_count = self.redis.incr(otp_attempt_key)  # how many user attempts to verify

        if attempt_count == 1:  # add expire time
            self.redis.expire(otp_attempt_key, ATTEMPT_TTL)

        if attempt_count > MAX_ATTEMPTS:
            self.add_to_blacklist()  # send phone number to otp_black_list
            return -1

        return attempt_count

    def is_blacklisted(self):
        otp_black_list_key = self.otp_blackList_key.format(self.phone_number)
        otp_black_list = self.redis.get(otp_black_list_key)
        return True if otp_black_list else False # if number is in otp_blacklist

    def add_to_blacklist(self):
        otp_black_list_key = self.otp_blackList_key.format(self.phone_number)
        otp_attempt_key = self.otp_attempt_key.format(self.phone_number)
        if not self.redis.exists(otp_black_list_key):
            self.redis.set(otp_black_list_key, self.phone_number, ex=BLACKLIST_TTL)
            self.redis.delete(otp_attempt_key)

    def is_valid_phone_number(self):
        """insure the phone number have true structure like 09*** """
        regex = '09\d{9}'
        return True if fullmatch(regex, self.phone_number) else False

    def is_valid_otp_code(self, otp_code):
        if otp_code.isdigit() and len(otp_code) == OTP_DEFAULT_LENGTH:
            return True
        return False
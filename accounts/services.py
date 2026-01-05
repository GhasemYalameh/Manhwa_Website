from unittest import expectedFailure

from rest_framework_simplejwt.tokens import RefreshToken
from django_redis import get_redis_connection
import secrets

OTP_TTL = 120
ATTEMPT_TTL = 300
BLACKLIST_TTL = 180
MAX_ATTEMPTS = 3

def create_otp(length:int=5)-> str:
    otp_string = ''.join(secrets.choice('0123456789') for _ in range(length))
    return otp_string

class OTP:
    def __init__(self):
        self.redis = get_redis_connection('default')
        self.otp_key = 'otp:{}'  # fill with phone_number
        self.otp_attempt_key = 'otp:attempt:{}'
        self.otp_blackList_key = 'otp:blacklist:{}'

    def set_otp_code(self, phone_number):
        if self.is_blacklisted(phone_number):
            return False

        otp_key = self.otp_key.format(phone_number)
        if not self.redis.exists(otp_key):
            otp_code = create_otp()
            self.redis.set(otp_key, otp_code, timeout=OTP_TTL)
        return True

    def check_otp_code(self, user_otp_code, phone_number):
        otp_key = self.otp_key.format(phone_number)
        expected_otp_code = self.redis.get(otp_key).decode()  # decoding otp_code to string
        # TODO: check existing of a key.
        if expected_otp_code and secrets.compare_digest(expected_otp_code, user_otp_code):
            return True
        else:
            return False

    def verify_otp_code(self, otp_code, phone_number):
        otp_attempt_key = self.otp_attempt_key.format(phone_number)
        otp_key = self.otp_key.format(phone_number)

        if self.is_blacklisted(phone_number):  # checking phone number limit
            return False

        if not self.check_otp_code(otp_code, phone_number):  # if otp code is not true
            attempt_count = self.redis.incr(otp_attempt_key)

            if attempt_count == 1:  # add expire time
                self.redis.expire(otp_attempt_key, ATTEMPT_TTL)

            if attempt_count > MAX_ATTEMPTS :
                self.add_black_list(phone_number)  # send phone number to otp_black_list
            return False

        # if verify is true
        self.redis.delete(otp_attempt_key)
        self.redis.delete(otp_key)
        return True

    def is_blacklisted(self, phone_number):
        otp_black_list_key = self.otp_blackList_key.format(phone_number)
        otp_black_list = self.redis.get(otp_black_list_key)
        return True if otp_black_list else False # if number is in otp_blacklist

    def add_black_list(self, phone_number):
        otp_black_list_key = self.otp_blackList_key.format(phone_number)
        otp_attempt_key = self.otp_attempt_key.format(phone_number)
        if not self.redis.exists(otp_black_list_key):
            self.redis.set(otp_black_list_key, phone_number, timeout=BLACKLIST_TTL)
            self.redis.delete(otp_attempt_key)

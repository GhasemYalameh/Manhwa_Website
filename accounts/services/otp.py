from django_redis import get_redis_connection
import secrets
from re import fullmatch
from .conf import (
    OTP_DEFAULT_LENGTH, OTP_TTL, ATTEMPT_TTL, BLACKLIST_TTL,
    MAX_ATTEMPTS, OTP_ATTEMPT_REDIS_KEY, OTP_BLACKLISTED_REDIS_KEY, 
    OTP_REDIS_KEY,
)


class OTP:
    """
        a service for generating OTP code.
        the black list system is supporting.
    """

    def __init__(self, phone_number, length=None):
        self.redis = get_redis_connection('default')
        self.phone_number = phone_number
        
        # filling redis keys with phone_number
        self.otp_key = OTP_REDIS_KEY.format(phone_number) 
        self.otp_attempt_key = OTP_ATTEMPT_REDIS_KEY.format(phone_number)
        self.otp_blacklisted_key = OTP_BLACKLISTED_REDIS_KEY.format(phone_number)

        self.otp_default_length = length or OTP_DEFAULT_LENGTH
        self.otp_ttl = OTP_TTL
        self.attempt_ttl = ATTEMPT_TTL
        self.blacklist_ttl = BLACKLIST_TTL
        self.max_attempts = MAX_ATTEMPTS

    def generate_otp_code(self, length=None):
        """Generating the OTP code. Returns None if the user condition is missed. else returns otp_code"""
        if length is None:
            length = self.otp_default_length

        if not self.redis.exists(self.otp_key):
            otp_code = self.create_otp(length)  # generating OTP code
            self.redis.set(self.otp_key, otp_code, ex=self.OTP_TTL)
            return otp_code

        return None

    def verify_otp_code(self, user_otp_code):
        """verifies the user otp code."""
        expected_otp_code = self.redis.get(self.otp_key) # decoding otp_code to string

        if expected_otp_code and secrets.compare_digest(expected_otp_code.decode() , user_otp_code):
            return True

        return False

    def check_attempts(self):
        attempt_count = self.redis.incr(self.otp_attempt_key)  # how many user attempts to verify

        if attempt_count == 1:  # add expire time
            self.redis.expire(self.otp_attempt_key, self.attempt_ttl)

        if attempt_count > self.max_attempts:
            self.add_to_blacklist()  # send phone number to otp_black_list
            return -1

        return attempt_count

    def is_blacklisted(self):
        otp_blacklisted_obj = self.redis.get(self.otp_blacklisted_key)
        return True if otp_blacklisted_obj else False # if number is in otp_blacklist

    def add_to_blacklist(self):
        if not self.redis.exists(self.otp_blacklisted_key):
            self.redis.set(self.otp_blacklisted_key, 1, ex=self.blacklist_ttl)
            self.redis.delete(self.otp_attempt_key)
            self.redis.delete(self.otp_key)

    def create_otp(self, length=None) -> str:
        if not length:
            length = self.otp_default_length

        otp_string = ''.join(secrets.choice('0123456789') for _ in range(length))
        return otp_string

    def send_sms(self, otp_code):
        print("#" * 100)
        print(f"your otp code is: {otp_code}".upper())
        print("#" * 100)

    def delete_cached_keys(self):
        """deleting all cached keys."""
        for key in (self.otp_blacklisted_key, self.otp_attempt_key, self.otp_key):
            self.redis.delete(key)

    def get_blacklisted_ttl(self):
        return self.redis.ttl(self.otp_blacklisted_key)

    def get_otp_code_ttl(self):
        return self.redis.ttl(self.otp_key)

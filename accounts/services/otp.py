from django_redis import get_redis_connection
import secrets
from .conf import (
    OTP_DEFAULT_LENGTH, OTP_TTL, ATTEMPT_TTL, BLACKLIST_TTL,
    MAX_ATTEMPTS, OTP_ATTEMPT_REDIS_KEY, OTP_BLACKLISTED_REDIS_KEY, 
    OTP_REDIS_KEY, PASS_ATTEMPT_REDIS_KEY, PASS_BLACKLISTED_REDIS_KEY,

)


class BlackListManager():
    def __init__(self, phone_number):
        self.redis = get_redis_connection('default')
        self.phone_number = phone_number
        
        # filling redis keys with phone_number
        self.attempt_key = PASS_ATTEMPT_REDIS_KEY.format(phone_number)
        self.blacklisted_key = PASS_BLACKLISTED_REDIS_KEY.format(phone_number)

        self.attempt_ttl = ATTEMPT_TTL
        self.blacklist_ttl = BLACKLIST_TTL
        self.max_attempts = MAX_ATTEMPTS

    def check_attempts(self):
        attempt_count = self.redis.incr(self.attempt_key)  # how many user attempts to verify

        if attempt_count == 1:  # add expire time
            self.redis.expire(self.attempt_key, self.attempt_ttl)

        if attempt_count >= self.max_attempts:
            self.add_to_blacklist()  # add phone number to otp_black_list
            return -1

        return attempt_count

    def is_blacklisted(self):
        blacklisted_obj = self.redis.get(self.blacklisted_key)
        return True if blacklisted_obj else False # if number is in otp_blacklist

    def add_to_blacklist(self):
        if not self.redis.exists(self.blacklisted_key):
            self.redis.set(self.blacklisted_key, 1, ex=self.blacklist_ttl)
            self.delete_keys_after_blacklisted()

    def delete_keys_after_blacklisted(self):
        """
        when user goes to blacklist, some key must remove from cache. 
        """
        self.redis.delete(self.attempt_key)

    def delete_cached_keys(self):
        """deleting all cached keys."""
        for key in (self.blacklisted_key, self.attempt_key):
            self.redis.delete(key)

    def get_blacklisted_ttl(self):
        return self.redis.ttl(self.blacklisted_key)


class OTP(BlackListManager):
    """
        a service for generating OTP code.
        the black list system is supporting.
    """

    def __init__(self, phone_number, length=None):
        super().__init__(phone_number)
        
        # filling redis keys with phone_number
        self.otp_key = OTP_REDIS_KEY.format(phone_number) 
        self.attempt_key = OTP_ATTEMPT_REDIS_KEY.format(phone_number)
        self.blacklisted_key = OTP_BLACKLISTED_REDIS_KEY.format(phone_number)

        self.otp_default_length = length or OTP_DEFAULT_LENGTH
        self.otp_ttl = OTP_TTL

    def generate_otp_code(self, length=None):
        """Generating the OTP code. Returns None if the user condition is missed. else returns otp_code"""
        if length is None:
            length = self.otp_default_length

        if not self.redis.exists(self.otp_key):
            otp_code = self._create_otp(length)  # generating OTP code
            self.redis.set(self.otp_key, otp_code, ex=self.otp_ttl)
            return otp_code

        return None

    def verify_otp_code(self, user_otp_code):
        """verifies the user otp code."""
        expected_otp_code = self.redis.get(self.otp_key) # decoding otp_code to string

        if expected_otp_code and secrets.compare_digest(expected_otp_code.decode() , user_otp_code):
            return True

        return False
    
    def _create_otp(self, length=None) -> str:
        length = length or self.otp_default_length

        otp_string = ''.join(secrets.choice('0123456789') for _ in range(length))
        return otp_string

    def delete_keys_after_blacklisted(self):
        super().delete_keys_after_blacklisted()
        self.redis.delete(self.otp_key)

    def send_sms(self, otp_code):
        print("#" * 100)
        print(f"your otp code is: {otp_code}".upper())
        print("#" * 100)

    def delete_cached_keys(self):
        super().delete_cached_keys()
        self.redis.delete(self.otp_key)

    def get_otp_code_ttl(self):
        return self.redis.ttl(self.otp_key)


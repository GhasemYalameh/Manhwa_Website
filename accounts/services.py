from django_redis import get_redis_connection
import secrets
from re import fullmatch





class OTP:
    """
        a service for generating and validating OTP code.
        the black list system is supporting.
    """
    OTP_DEFAULT_LENGTH = 5
    OTP_TTL = 120
    ATTEMPT_TTL = 300
    BLACKLIST_TTL = 180
    MAX_ATTEMPTS = 3

    def __init__(self, phone_number, length=None):
        if length is not None:
            self.OTP_DEFAULT_LENGTH = length

        self.redis = get_redis_connection('default')
        self.phone_number = phone_number
        self.otp_key = f'otp:{phone_number}'  # fill with phone_number
        self.otp_attempt_key = f'otp:attempt:{phone_number}'
        self.otp_blacklisted_key = f'otp:blacklisted:{phone_number}'

    def generate_otp_code(self, length=None):
        """Generating the OTP code. Returns None if the user condition is missed. else returns otp_code"""
        if length is None:
            length = self.OTP_DEFAULT_LENGTH

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
            self.redis.expire(self.otp_attempt_key, self.ATTEMPT_TTL)

        if attempt_count > self.MAX_ATTEMPTS:
            self.add_to_blacklist()  # send phone number to otp_black_list
            return -1

        return attempt_count

    def is_blacklisted(self):
        otp_blacklisted_obj = self.redis.get(self.otp_blacklisted_key)
        return True if otp_blacklisted_obj else False # if number is in otp_blacklist

    def add_to_blacklist(self):
        if not self.redis.exists(self.otp_blacklisted_key):
            self.redis.set(self.otp_blacklisted_key, 1, ex=self.BLACKLIST_TTL)
            self.redis.delete(self.otp_attempt_key)
            self.redis.delete(self.otp_key)

    def is_valid_phone_number(self):
        """insure the phone number have true structure like 09*** """
        regex = '09\d{9}'
        return True if fullmatch(regex, self.phone_number) else False

    def is_valid_otp_code(self, otp_code):
        """insure all characters are digits and OTP code have true length."""
        if otp_code.isdigit() and len(otp_code) == self.OTP_DEFAULT_LENGTH:
            return True
        return False

    def create_otp(self, length: int = OTP_DEFAULT_LENGTH) -> str:
        otp_string = ''.join(secrets.choice('0123456789') for _ in range(length))
        return otp_string

    def delete_cached_keys(self):
        """deleting all cached keys."""
        for key in (self.otp_blacklisted_key, self.otp_attempt_key, self.otp_key):
            self.redis.delete(key)

    def get_blacklisted_ttl(self):
        return self.redis.ttl(self.otp_blacklisted_key)

    def get_otp_code_ttl(self):
        return self.redis.ttl(self.otp_key)

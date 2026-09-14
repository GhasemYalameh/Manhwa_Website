import uuid

from django.contrib.auth.models import PermissionsMixin, AbstractBaseUser, BaseUserManager
from django.db import models
from django.core.validators import RegexValidator
from django.utils import timezone

from subscription.models import Subscription
from .services import user_avatar_upload_to

class CustomUserManager(BaseUserManager):
    def create_user(self, phone_number, password=None, **extra_fields):
        """
        creating a normal user
        """
        if not phone_number:
            raise ValueError("phone number is required.")
        if not password:
            raise ValueError("password is required.")

        user = self.model(phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, password=None, **extra_fields):
        """
        creating an superuser
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("superuser must have is_staff=True")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("superuser must have is_superuser=True.")

        return self.create_user(phone_number, password, **extra_fields)

    def create_user_via_otp(self, phone_number, **extra_fields):
        """"
        creating an user with unusable password hash. just with phone number
        """
        if not phone_number:
            raise ValueError("phone number is required.")

        user = self.model(phone_number=phone_number, **extra_fields)
        user.set_unusable_password()
        user.save(using=self._db)
        return user


class CustomUser(AbstractBaseUser, PermissionsMixin):
    phone_regex = RegexValidator(regex=r'^09\d{9}$',
        message="mobile format must be 09xxxxxxxxx (11 digits)."
    )
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    phone_number = models.CharField(max_length=11, unique=True, validators=[phone_regex],)
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    bio = models.CharField(max_length=150, blank=True)
    email = models.EmailField(blank=True, null=True)
    avatar = models.ImageField(upload_to=user_avatar_upload_to, default='User/default.jpg')

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_new_user = models.BooleanField(default=True) 

    date_joined = models.DateTimeField(default=timezone.now)

    objects = CustomUserManager()

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = []    

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return self.phone_number
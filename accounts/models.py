from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator


class CustomUser(AbstractUser):
    phone_regex = RegexValidator(
        regex=r'^09\d{9}$',
        message='شماره موبایل باید 11 رقم و با 09 شروع شود'
    )

    phone_number = models.CharField(
        validators=[phone_regex],
        max_length=11,
        unique=True,
        verbose_name='شماره موبایل'
    )

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.phone_number

    def save(self, *args, **kwargs):
        # اگر username خالی بود، phone_number رو بذار
        if not self.username:
            self.username = self.phone_number
        super().save(*args, **kwargs)

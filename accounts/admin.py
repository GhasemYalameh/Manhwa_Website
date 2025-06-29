from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser


class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + ('Custom Fields', {'fields': ['phone_number']},)
    add_fieldsets = UserAdmin.add_fieldsets + ('Custom Fields', {'fields': ['phone_number']},)


admin.site.register(CustomUser, CustomUserAdmin)


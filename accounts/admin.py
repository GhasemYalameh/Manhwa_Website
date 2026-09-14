from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


class CustomUserAdmin(UserAdmin):
    # فیلدهای نمایش در لیست
    list_display = ['phone_number', 'id', 'first_name', 'is_staff', 'is_active', 'is_new_user',]

    # فیلدهای جستجو
    search_fields = ['phone_number', 'first_name', 'last_name']

    # فیلدهای فیلتر
    list_filter = ['is_active', 'is_staff', 'date_joined']

    # autocomplete_fields = ('watch_list',)

    # ترتیب نمایش
    ordering = ['phone_number']

    # تنظیمات فرم ویرایش
    fieldsets = (
        (None, {'fields': ('phone_number', 'password')}),
        ('اطلاعات شخصی', {'fields': ('first_name', 'last_name', 'email', 'is_new_user',)}),
        ('دسترسی‌ها', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        # ('manhwa', {'fields': ('watch_list',)}),
        ('تاریخ‌ها', {'fields': ('last_login', 'date_joined')}),
    )

    # تنظیمات فرم اضافه کردن
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone_number', 'password1', 'password2'),
        }),
    )


admin.site.register(CustomUser, CustomUserAdmin)


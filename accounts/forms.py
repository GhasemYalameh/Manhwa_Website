from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser


class CustomUserCreationForm(UserCreationForm):
    phone_number = forms.CharField(
        max_length=11,
        widget=forms.TextInput(attrs={
            'placeholder': '09123456789',
            'class': 'form-control'
        }),
        label='شماره موبایل'
    )

    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'placeholder': 'نام کاربری',
            'class': 'form-control'
        }),
        label='نام کاربری'
    )

    class Meta:
        model = CustomUser
        fields = ('phone_number', 'username', 'password1', 'password2')

    def clean_phone_number(self):
        phone = self.cleaned_data.get('phone_number')
        if not phone.startswith('09') or len(phone) != 11:
            raise forms.ValidationError('شماره موبایل باید 11 رقم و با 09 شروع شود')
        if not phone.isdigit():
            raise forms.ValidationError('شماره موبایل فقط شامل عدد باشد')
        return phone


class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'placeholder': 'شماره موبایل',
            'class': 'form-control',
            'autofocus': True
        }),
        label='شماره موبایل'
    )

    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'رمز عبور',
            'class': 'form-control'
        }),
        label='رمز عبور'
    )

from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser


class CustomCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'phone_number', 'password1', 'password2')


class CustomChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'phone_number',)

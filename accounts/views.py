from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.views import LoginView
from django.contrib import messages
from .forms import CustomUserCreationForm, CustomAuthenticationForm
from .models import CustomUser


class CustomLoginView(LoginView):
    form_class = CustomAuthenticationForm
    template_name = 'registration/login.html'

    def form_valid(self, form):
        messages.success(self.request, 'با موفقیت وارد شدید!')
        return super().form_valid(form)


def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # خودکار لاگین کردن بعد از ثبت نام
            phone_number = form.cleaned_data.get('phone_number')
            password = form.cleaned_data.get('password1')
            user = authenticate(phone_number=phone_number, password=password)
            if user:
                login(request, user)
                messages.success(request, 'حساب کاربری شما با موفقیت ایجاد شد!')
                return redirect('home')  # به home page برو
    else:
        form = CustomUserCreationForm()

    return render(request, 'registration/register.html', {'form': form})


def profile_view(request):
    # watch_list = CustomUser.objects.prefetch_related('watch_list').filter(id=request.user.id)

    return render(request, 'accounts/profile.html',)

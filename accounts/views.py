from django.shortcuts import render, redirect

from .forms import CustomCreationForm, CustomChangeForm


def sign_up(request):

    if request.method == 'POST':
        form = CustomCreationForm(request.POST)
        if form.is_valid():
            form.save()
            print("f")
            return redirect('home')

    form = CustomCreationForm()
    return render(request, 'accounts/signup.html', context={'form': form})



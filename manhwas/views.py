from django.shortcuts import render
from .models import Manhwa
from django.db.models import Avg, Value
from django.db.models.functions import Coalesce


def home_page(request):
    manhwas = Manhwa.objects.annotate(avg_rating=Coalesce(Avg("rates__rating"), Value(0)))
    return render(request, 'home.html', context={'manhwas': manhwas})

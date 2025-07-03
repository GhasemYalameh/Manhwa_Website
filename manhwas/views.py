from django.shortcuts import render
from .models import Manhwa
from django.db.models import Avg, Value, IntegerField, FloatField
from django.db.models.functions import Coalesce, Cast


def home_page(request):
    manhwas = Manhwa.objects.annotate(avg_rating=Coalesce(Avg(Cast("rates__rating", output_field=FloatField())), Value(0.0)))
    return render(request, 'home.html', context={'manhwas': manhwas})

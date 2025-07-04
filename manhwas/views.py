from django.shortcuts import render
from .models import Manhwa
from django.db.models import Avg, Count, Value, Max, When, Case, CharField
from django.db.models.functions import Coalesce, LPad, Concat, Cast


def home_page(request):
    # manhwas = Manhwa.objects.annotate(
    #     avg_rating=Coalesce(Avg('rates__rating'), Value(0.0)),
    #     rating_count=Count('rates'
    #     ))
    manhwas = Manhwa.objects.only(
        'id',
        'en_title',
        'season',
        'cover',
        'views',
    ).annotate(
        avg_rating=Coalesce(Avg('rates__rating'), Value(0.0)),
        last_episode=Max('episodes__number'),
        last_upload=Case(
            When(last_episode=0, then=Value('اپلود نشده')),
            When(last_episode__isnull=True, then=Value("اپلود نشده")),
            default=Concat(
                Value('S'), Cast('season', CharField()), Value('-E'),
                Case(
                    When(last_episode__lt=10, then=Concat(Value('0'), Cast('last_episode', CharField()))),
                    default=Cast('last_episode', CharField())
                ),
                output_field=CharField())
            ))
    return render(request, 'home.html', context={'manhwas': manhwas})


def test_view(request):
    manhwas = Manhwa.objects.only(
        'id',
        'en_title',
        'season',
        'cover',
        'views',
    ).annotate(
        avg_rating=Coalesce(Avg('rates__rating'), Value(0.0)),
        last_episode=Max('episodes__number'),
        last_upload=Case(
            When(last_episode=0, then=Value('اپلود نشده')),
            When(last_episode__isnull=True, then=Value("اپلود نشده")),
            default=Concat(
                Value('S'), 'season', Value('-E'),
                LPad('last_episode', 2, Value("0")),
                output_field=CharField())
            ),

                            )

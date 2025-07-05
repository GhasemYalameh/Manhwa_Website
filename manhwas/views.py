from django.shortcuts import render, get_object_or_404
from .models import Manhwa, View
from django.db.models import Avg, Value, Max, When, Case, CharField
from django.db.models.functions import Coalesce, Concat, Cast


def home_page(request):
    manhwas = Manhwa.objects.only(
        'id',
        'en_title',
        'season',
        'cover',
        'views_count',
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


def manhwa_detail(request, pk):
    manhwa = get_object_or_404(
        Manhwa.objects.prefetch_related('episodes', 'genres'),
        pk=pk
    )
    if request.user.is_authenticated:

        # if user viewed the manhwa in past created=False
        #  else create a view and created=True
        view_obj, created = View.objects.get_or_create(
            user=request.user,
            manhwa=manhwa,
        )
        if created:
            manhwa.views_count += 1
            manhwa.save(update_fields=['views_count'])

    return render(request, 'manhwas/manhwa_detail_view.html', context={'manhwa': manhwa})

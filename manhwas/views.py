from django.db import IntegrityError
from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.db.models import Avg, F, Value, Max, When, Case, CharField
from django.db.models.functions import Coalesce, Concat, Cast
from django.utils.translation import gettext as _
from django.contrib import messages

from .forms import CommentForm
from .models import Manhwa, View



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
            When(last_episode=0, then=Value(_('No uploaded'))),
            When(last_episode__isnull=True, then=Value(_('No uploaded'))),
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
        Manhwa.objects.select_related('studio').prefetch_related(
            'episodes', 'genres',
            'rates', 'comments__author',
        ),
        pk=pk
    )
    if request.user.is_authenticated:

        # if user viewed the manhwa in past created=False
        #  else create a view and created=True
        view_obj, created = View.objects.get_or_create(
            user=request.user,
            manhwa_id=pk,
        )
        if created:
            Manhwa.objects.filter(pk=pk).update(
                views_count=F('views_count')+1
            )

    form = CommentForm()

    return render(request, 'manhwas/manhwa_detail_view.html', context={'manhwa': manhwa, 'form': form})


def add_comment_manhwa(request, pk):
    form = CommentForm(request.POST)
    if form.is_valid():
        obj = form.save(commit=False)
        obj.manhwa_id = pk
        obj.author = request.user
        try:
            obj.save()
        except IntegrityError:
            messages.error(request, _("you cant send same text for your comments"))

    return redirect('manhwa_detail', pk=pk)

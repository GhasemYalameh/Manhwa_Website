from django.db import IntegrityError
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.db.models import Avg, F, Value, Max, When, Case, CharField, Subquery, OuterRef
from django.db.models.functions import Coalesce, Concat, Cast
from django.utils.timesince import timesince
from django.utils.translation import gettext as _
from django.views.decorators.http import require_POST

from .forms import CommentForm
from .models import Manhwa, View, CommentReAction, Comment

import json


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
            )).order_by('-datetime_created')
    return render(request, 'home.html', context={'manhwas': manhwas})


def manhwa_detail(request, pk):
    manhwa = get_object_or_404(
        Manhwa.objects.select_related('studio').prefetch_related(
            'episodes', 'genres',
            'rates',
        ),
        pk=pk
    )

    if request.user.is_authenticated:

        user_reacted_subquery = CommentReAction.objects.filter(
            user_id=request.user.id,
            comment_id=OuterRef('pk')
        ).values('reaction')

        comments = Comment.objects.filter(manhwa_id=pk).select_related('author').annotate(
            user_reaction=Coalesce(
                Subquery(user_reacted_subquery),
                Value('no-reaction')
            )
        )
    else:
        comments = Comment.objects.filter(manhwa_id=pk).select_related('author').all()

    return render(
        request,
        'manhwas/manhwa_detail_view.html',
        context={
            'manhwa': manhwa,
            'comments': comments
        }
      )


@require_POST
def change_or_create_reaction(request, pk):
    data = json.loads(request.body)
    reaction = data.get('reaction')

    allow_reactions = [CommentReAction.LIKE, CommentReAction.DISLIKE]

    if reaction not in allow_reactions:
        return JsonResponse({'status': False, 'error': 'reaction not true', 'message':_('reaction not true')})

    try:
        # if reaction does exist

        reaction_obj = CommentReAction.objects.get(
            user=request.user,
            comment_id=pk
        )

        # if reaction repeated. then delete reaction
        if reaction_obj.reaction == reaction:
            reaction_obj.delete()

            # decrease comment likes or dislikes count field
            if reaction == CommentReAction.LIKE:
                Comment.objects.filter(pk=pk).update(likes_count=F('likes_count') - 1)
            else:
                Comment.objects.filter(pk=pk).update(dis_likes_count=F('dis_likes_count') - 1)

            comment = get_object_or_404(Comment, pk=pk)
            response = {
                'status': True,
                'reaction': '',
                'message': _('reaction removed'),
                'likes_count': comment.likes_count,
                'dis_likes_count': comment.dis_likes_count
            }

        else:  # if reaction is different

            reaction_obj.reaction = reaction
            reaction_obj.save()

            # change comment likes and dislikes count
            if reaction == CommentReAction.LIKE:
                Comment.objects.filter(pk=pk).update(
                    likes_count=F('likes_count') + 1,
                    dis_likes_count=F('dis_likes_count') - 1
                )

            else:
                Comment.objects.filter(pk=pk).update(
                    likes_count=F('likes_count') - 1,
                    dis_likes_count=F('dis_likes_count') + 1
                )

            comment = get_object_or_404(Comment, pk=pk)

            response = {
                'status': True,
                'reaction': 'like' if reaction == CommentReAction.LIKE else 'dislike',
                'message': _('your reaction changed'),
                'likes_count': comment.likes_count,
                'dis_likes_count': comment.dis_likes_count
            }

    except CommentReAction.DoesNotExist:  # if reaction is not in db created it
        CommentReAction.objects.create(
            user=request.user,
            comment_id=pk,
            reaction=reaction
        )

        # increase likes or dislikes count
        if reaction == CommentReAction.LIKE:
            Comment.objects.filter(pk=pk).update(likes_count=F('likes_count') + 1)
        else:
            Comment.objects.filter(pk=pk).update(dis_likes_count=F('dis_likes_count') + 1)

        comment = get_object_or_404(Comment, pk=pk)

        response = {
            'status': True,
            'reaction': 'like' if reaction == CommentReAction.LIKE else 'dislike',
            'message': _('your reaction added'),
            'likes_count': comment.likes_count,
            'dis_likes_count': comment.dis_likes_count
        }
    return JsonResponse(response)


@require_POST
def add_comment_manhwa(request, pk):
    data = json.loads(request.body)

    form_data = {
        'text': data.get('body')
    }
    form = CommentForm(form_data)

    if form.is_valid():
        obj = form.save(commit=False)
        obj.author = request.user
        obj.manhwa_id = pk
        try:
            obj.save()
            response = {
                'status': True,
                'comment_id': obj.id,
                'author_name': request.user.username,
                'body': data.get('body'),
                'datetime_modified': timesince(obj.datetime_modified),
                'message': _('comment successfully added.')
                }
        except IntegrityError:
            response = {'status': False, 'message': _('you can not send same text for comments.')}

    else:
        response = {
            'status': False,
            'errors': form.errors,
            'message': 'your text is not valid. please dont use html tags.'
        }

    return JsonResponse(response)


@require_POST
def set_user_view_for_manhwa(request, pk):
    response = {
        'status': False,
        'error': 'user is not authenticated',
        'message': ''
    }

    if request.user.is_authenticated:

        view_obj, created = View.objects.get_or_create(
            user_id=request.user.id,
            manhwa_id=pk
        )

        if created:
            Manhwa.objects.filter(id=pk).update(views_count=F('views_count') + 1)
            response['status'] = True
            response['message'] = _('user view added to manhwa.')

        else:
            response['message'] = _('user viewed in past')

    return JsonResponse(response)

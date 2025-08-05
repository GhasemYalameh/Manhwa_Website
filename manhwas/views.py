from django.db import IntegrityError, transaction
from django.db.models import Avg, Count, F, Value, Max, When, Case, CharField, Subquery, OuterRef, Exists
from django.db.models.functions import Coalesce, Concat, Cast
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.utils.timesince import timesince
from django.utils.translation import gettext as _
from django.views.decorators.http import require_POST

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .forms import CommentForm
from .models import Manhwa, View, CommentReAction, Comment, CommentReply
from .serializers import (
    CommentDetailSerializer,
    CommentReactionSerializer,
    CommentReectionToggleSerializer,
    CommentSerializer,
    ManhwaSerializer,
    ViewSerializer
)

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

        is_replied_subquery = Exists(CommentReply.objects.filter(replied_comment_id=OuterRef('pk')))

        comments = Comment.objects.filter(manhwa_id=pk).select_related('author').prefetch_related('replies').annotate(

            user_reaction=Coalesce(
                Subquery(user_reacted_subquery),
                Value('no-reaction')),

            is_replied=is_replied_subquery,
            replies_count=Count('replies')

        ).filter(is_replied=False)

    else:
        is_replied_subquery = Exists(CommentReply.objects.filter(replied_comment_id=OuterRef('pk')))
        comments = Comment.objects.filter(manhwa_id=pk).select_related('author').annotate(
            is_replied=is_replied_subquery

        ).filter(is_replied=False)

    return render(
        request,
        'manhwas/manhwa_detail_view.html',
        context={
            'manhwa': manhwa,
            'comments': comments.order_by('-datetime_created')
        }
      )


@require_POST
def show_replied_comment(request, pk):
    data = request.POST
    comment_object = get_object_or_404(
        Comment.objects.prefetch_related('replies__replied_comment__author').select_related('author'),
        manhwa_id=pk,
        id=data['comment_id']
    )
    return render(request, 'manhwas/comment_replies.html', context={'comment': comment_object})


@api_view()
def api_manhwa_list(request):
    query_set = Manhwa.objects.prefetch_related('comments__author').all()
    serializer = ManhwaSerializer(query_set, many=True)
    return Response(serializer.data)


@api_view()
def api_manhwa_detail(request, pk):
    manhwa = get_object_or_404(Manhwa, pk=pk)
    serializer = ManhwaSerializer(manhwa)
    return Response(serializer.data)


@api_view(['POST'])
def api_create_manhwa_comment(request):
    response = {'message': '', 'comment': None}
    if request.method == 'POST':
        serializer = CommentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(author=request.user)

        response['comment'] = serializer.data
        response['message'] = 'comment successfully added.'

        if request.data.get('replied_to'):  # if comment type is replied to another comment
            try:
                CommentReply.objects.create(
                    main_comment_id=request.data.get('replied_to'),
                    replied_comment_id=serializer.data['id']
                )
                response['message'] = 'comment successfully replied.'

            except IntegrityError:
                return Response({'replied_to': _('comment with this id not exist')}, status=status.HTTP_400_BAD_REQUEST)

        return Response(response, status=status.HTTP_201_CREATED)

    elif request.method == 'GET':
        return Response('wellcome')


@api_view()
def api_get_manhwa_comments(request, pk):
    comment_query = Comment.objects.prefetch_related('replies').select_related('author').filter(manhwa_id=pk).annotate(
        is_replied_comment=Exists(CommentReply.objects.filter(replied_comment_id=OuterRef('pk')))
    ).filter(is_replied_comment=False)
    serializer = CommentSerializer(comment_query, many=True)
    return Response(serializer.data)


@api_view()
def api_get_comment_replies(request, manhwa_id, comment_id):
    query_set = get_object_or_404(
        Comment.objects.select_related('author').prefetch_related('replies__replied_comment__author'),
        manhwa_id=manhwa_id,
        pk=comment_id
    )

    serializer = CommentDetailSerializer(query_set)
    return Response(serializer.data)


@api_view(['POST'])
def api_reaction_handler(request):
    serializer = CommentReectionToggleSerializer(data=request.data)

    serializer.is_valid(raise_exception=True)

    comment_id = serializer.validated_data.get('comment_id')
    reaction = serializer.validated_data.get('reaction')
    try:
        reaction_obj, action = CommentReAction.objects.toggle_reaction(
            request.user,
            comment_id=comment_id,
            reaction=reaction
        )

        # get reaction count from db
        comment_data = Comment.objects.only('likes_count', 'dis_likes_count').get(pk=comment_id)
        comment_data = {'likes_count': comment_data.likes_count, 'dis_likes_count': comment_data.dis_likes_count}

        reaction_data = None
        if action != 'deleted':
            reaction_data = CommentReactionSerializer(reaction_obj).data

        response = {
            'action': action,
            'reaction': reaction_data,
            'comment': comment_data
        }
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response(response, status=status.HTTP_200_OK)


@api_view(['POST'])
def api_set_user_view_for_manhwa(request):
    serializer = ViewSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    manhwa_id = serializer.validated_data.get('manhwa_id')

    with transaction.atomic():
        view_obj, created = View.objects.get_or_create(
            manhwa_id=manhwa_id,
            user=request.user
        )

        if created:
            Manhwa.objects.filter(pk=manhwa_id).update(views_count=F('views_count') + 1)
            return Response({'action': 'created'})

        return Response({'action': 'was exists'})

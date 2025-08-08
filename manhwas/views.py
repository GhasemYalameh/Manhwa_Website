from django.db import IntegrityError, transaction, connection
from django.db.models import Avg, Count, F, Value, Max, When, Case, CharField, Subquery, OuterRef, Exists
from django.db.models.functions import Coalesce, Concat, Cast
from django.shortcuts import render, get_object_or_404
from django.utils.translation import gettext as _
from django.views.decorators.http import require_POST

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Manhwa, View, CommentReAction, Comment, CommentReply, NewComment
from . import serializers as srilzr


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

    comments_query = NewComment.objects.select_related('author').prefetch_related('childes').filter(level=0).annotate(
        replies_count=Count('childes')
    )

    if request.user.is_authenticated:

        user_reacted_subquery = CommentReAction.objects.filter(
            user_id=request.user.id,
            comment_id=OuterRef('pk')
        ).values('reaction')

        comments_query = comments_query.annotate(
            user_reaction=Coalesce(
                Subquery(user_reacted_subquery),
                Value('no-reaction')),
        ).order_by('-created_at')
    return render(
        request,
        'manhwas/manhwa_detail_view.html',
        context={
            'manhwa': manhwa,
            'comments': comments_query
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
    serializer = srilzr.ManhwaSerializer(query_set, many=True)
    return Response(serializer.data)


@api_view()
def api_manhwa_detail(request, pk):
    manhwa = get_object_or_404(Manhwa, pk=pk)
    serializer = srilzr.ManhwaSerializer(manhwa)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_create_manhwa_comment(request):
    response = {'message': '', 'comment': None}
    if request.method == 'POST':
        serializer = srilzr.CommentSerializer(data=request.data)
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
    serializer = srilzr.CommentSerializer(comment_query, many=True)
    return Response(serializer.data)


@api_view()
def api_get_comment_replies(request, manhwa_id, comment_id):
    query_set = get_object_or_404(
        Comment.objects.select_related('author').prefetch_related('replies__replied_comment__author'),
        manhwa_id=manhwa_id,
        pk=comment_id
    )

    serializer = srilzr.CommentDetailSerializer(query_set)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_reaction_handler(request):
    serializer = srilzr.CommentReectionToggleSerializer(data=request.data)
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
        comment_data = NewComment.objects.only('id', 'likes_count', 'dis_likes_count').get(pk=comment_id)
        comment_data = {'likes_count': comment_data.likes_count, 'dis_likes_count': comment_data.dis_likes_count}

        reaction_data = srilzr.CommentReactionSerializer(reaction_obj).data if action != 'deleted' else None

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
    serializer = srilzr.ViewSerializer(data=request.data)
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


@api_view(['GET', 'POST'])
def get_new_comments(request, manhwa_id):
    query_set = NewComment.objects.select_related('author').filter(manhwa_id=manhwa_id)
    serializer = srilzr.NewCommentSerializer(query_set, many=True)

    if request.method == 'POST':
        serializer = srilzr.NewCommentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(author=request.user, manhwa_id=manhwa_id)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    return Response(serializer.data)


@api_view()
def api_new_comment_childes(request, pk):
    try:
        comment = NewComment.objects.prefetch_related('childes').get(pk=pk)
        serializer = srilzr.NewCommentSerializer(comment.childes.all(), many=True)
        return Response(serializer.data)
    except NewComment.DoesNotExist:
        return Response('error', status=status.HTTP_400_BAD_REQUEST)


def delete_db(model_class):
    table_name = model_class._meta.db_table
    with connection.cursor() as cursor:
        cursor.execute(f"DELETE FROM {table_name}")
        cursor.execute(f"DELETE FROM sqlite_sequence WHERE name='{table_name}'")


@api_view(['GET', 'POST'])
def moving_data_db(request):
    if request.method == 'POST':
        parents = {'': 0}
        not_replied = Comment.objects.annotate(
            is_replied=Exists(CommentReply.objects.filter(replied_comment_id=OuterRef('pk')))
        ).filter(is_replied=False)

        delete_db(NewComment)

        for comment_obj in not_replied:
            comment = NewComment.objects.create(
                author_id=comment_obj.author_id,
                text=comment_obj.text,
                manhwa_id=comment_obj.manhwa_id,
                created_at=comment_obj.datetime_created,
                updated_at=comment_obj.datetime_modified
            )
            parents[str(comment_obj.id)] = comment.id

        print(NewComment.objects.count(), 'created in new comment!')
        print(parents)

        for replied_obj in CommentReply.objects.all():
            comment_obj = replied_obj.replied_comment
            try:
                NewComment.objects.create(
                    author_id=comment_obj.author_id,
                    text=comment_obj.text,
                    manhwa_id=comment_obj.manhwa_id,
                    parent_id=parents[str(replied_obj.main_comment_id)],
                    created_at=comment_obj.datetime_created,
                    updated_at=comment_obj.datetime_modified
                )
            except Exception as e:
                print('excepted:', replied_obj.id, str(e))

    return Response({'ssss'})


@api_view(['GET', 'POST'])
def moving_reaction_db(request):

    if request.method == 'POST':
        delete_db(CommentReAction)

    return Response({'dddd'})
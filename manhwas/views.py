import requests
from django.db import transaction, connection
from django.db.models import Avg, Count, F, Value, Max, When, Case, CharField, Subquery, OuterRef, Exists
from django.db.models.functions import Coalesce, Concat, Cast
from django.shortcuts import render, get_object_or_404
from django.template.loader import render_to_string
from django.utils.functional import cached_property
from django.utils.translation import gettext as _
from django.views.decorators.http import require_POST
from django.http import JsonResponse

from rest_framework import status, mixins
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ReadOnlyModelViewSet

from . import serializers as srilzr
from .paginations import CustomPagination
from .models import Manhwa, View, CommentReAction, NewComment


def home_page(request):
    manhwas = Manhwa.objects.only(
        'id', 'en_title', 'season',
        'cover', 'views_count', 'last_upload'
    ).annotate(
        avg_rating=Coalesce(Avg('rates__rating'), Value(0.0)),
    ).order_by('-datetime_created')

    return render(request, 'home.html', context={'manhwas': manhwas})


def manhwa_detail(request, pk):
    manhwa = get_object_or_404(
        Manhwa.objects.select_related('studio').prefetch_related(
            'episodes', 'genres',
            'rates',
        ),
        pk=pk
    )
    # if request from AJAX
    if request.headers.get('Tab-Load') == 'comments':
        comments_query = NewComment.objects.\
            select_related('author').\
            prefetch_related('childes').\
            filter(level=0, manhwa_id=pk).annotate(
                replies_count=Count('childes'))

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

        html = render_to_string('manhwas/_comments.html', context={'comments': comments_query, 'manhwa_id': manhwa.id})
        return JsonResponse({'html': html})

    return render(
        request,
        'manhwas/manhwa_detail_view.html',
        context={
            'manhwa': manhwa,
        }
      )


def show_replied_comment(request, manhwa_id, comment_id):
    url = request.build_absolute_uri(f'/api/manhwas/{manhwa_id}/comments/{comment_id}/replies/')
    response = requests.get(url)
    data = response.json()
    return render(request, 'manhwas/comment_replies.html', context={'comment': data})


class CommentViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    GenericViewSet
):
    pagination_class = CustomPagination

    @cached_property
    def manhwa(self):
        manhwa_pk = self.kwargs['manhwa_pk']
        return get_object_or_404(Manhwa, pk=manhwa_pk)

    def get_permissions(self):
        # must be login for comment creation
        return [IsAuthenticated() if self.action == 'create' else AllowAny()]

    def get_queryset(self):
        pk = self.kwargs.get('pk')

        base_qs = NewComment.objects.prefetch_related('childes__author').select_related('author').filter(
            manhwa=self.manhwa
        )

        if self.action == 'list':
            return base_qs.filter(level=0)

        elif self.action == 'replies':
            return base_qs.filter(pk=pk)

        return base_qs.filter(pk=pk)  # create, detail

    def get_serializer_class(self):
        if self.action == 'replies':
            return srilzr.CommentDetailSerializer
        return srilzr.NewCommentSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, manhwa=self.manhwa)

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)

        response.data = {
            'comment': response.data,
            'message': 'comment successfully added.'
        }
        return response


    @action(detail=True, methods=['get'])
    def replies(self, request, manhwa_pk=None, pk=None):
        replies_query_set = self.get_queryset()
        serializer = self.get_serializer(replies_query_set, many=True)
        return Response(serializer.data)


class ManhwaViewSet(ReadOnlyModelViewSet):
    serializer_class = srilzr.ManhwaSerializer
    queryset = Manhwa.objects.prefetch_related('comments__author').all()

    def get_permissions(self):
        return [IsAuthenticated() if self.action == 'set_view' else AllowAny()]

    @action(detail=True, methods=['post'])
    def set_view(self, request, pk):
        with transaction.atomic():
            view_obj, created = View.objects.get_or_create(
                user=request.user,
                manhwa_id=pk
            )
            if created:
                Manhwa.objects.filter(pk=pk).update(views_count=F('views_count') + 1)
                return Response({'action': 'created'})

            return Response({'action': 'was exists'})


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


def delete_db(model_class):
    table_name = model_class._meta.db_table
    with connection.cursor() as cursor:
        cursor.execute(f"DELETE FROM {table_name}")
        cursor.execute(f"DELETE FROM sqlite_sequence WHERE name='{table_name}'")

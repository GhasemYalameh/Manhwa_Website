import requests

from django.db import transaction, connection
from django.db.models import Avg, F, Value, Subquery, OuterRef, Prefetch
from django.db.models.functions import Coalesce
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.template.loader import render_to_string
from django.utils.functional import cached_property

from rest_framework import status, mixins
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.generics import ListCreateAPIView, RetrieveAPIView, GenericAPIView, CreateAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ReadOnlyModelViewSet, ModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend

from . import serializers as srilzr
from .models import Manhwa, View, CommentReAction, Comment, Episode, Ticket, Rate
from .paginations import CustomPagination
from .permissions import IsOwnerOrAdmin


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
        url = request.build_absolute_uri(f'/api/manhwas/{manhwa.id}/comments/')
        response = requests.get(url, cookies={'sessionid': request.COOKIES.get('sessionid')})
        data = response.json()
        html = render_to_string('manhwas/_comments.html', context={'comments': data.get('results'), 'manhwa_id': manhwa.id})
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


class TicketApiView(ListCreateAPIView):
    permission_classes = (IsAuthenticated,)
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('viewing_status',)

    def get_queryset(self):
        query = Ticket.objects.prefetch_related('messages').all()
        if self.request.method == 'GET' and not self.request.user.is_staff:
            return query.filter(user=self.request.user)
        return query

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return srilzr.CreateTicketSerializer
        elif self.request.method == 'GET':
            return srilzr.ListTicketSerializer
        return srilzr.ListTicketSerializer


class TicketMessageApiView(RetrieveAPIView, CreateAPIView, GenericAPIView):
    queryset = Ticket.objects.prefetch_related('messages').all()
    permission_classes = [IsOwnerOrAdmin]


    def get_serializer_context(self):
        context = {'ticket': self.kwargs['pk'],}
        return {**context, **super().get_serializer_context()}

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return srilzr.RetrieveTicketMessagesSerializer
        return srilzr.CreateTicketMessageSerializer


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

        base_qs = Comment.objects.prefetch_related(
            Prefetch(
                'children',
                queryset=Comment.objects.select_related('author')
            )
        ).select_related('author').filter(
            manhwa=self.manhwa
        )

        if self.action == 'list':
            query = base_qs.filter(level=0)
            return query if not self.request.user.is_authenticated else query.annotate(
                user_reaction=Coalesce(
                    Subquery(CommentReAction.objects.filter(
                        user_id=self.request.user.id,
                        comment_id=OuterRef('pk')
                        ).values('reaction')),
                    Value('no-reaction')
                ),
            )
        elif self.action == 'replies':
            return get_object_or_404(base_qs, pk=pk)

        return base_qs.filter(pk=pk)  # create, detail

    def get_serializer_class(self):
        if self.action == 'replies':
            return srilzr.CommentDetailSerializer
        elif self.action == 'create':
            return srilzr.CreateCommentSerializer
        return srilzr.RetrieveCommentSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, manhwa=self.manhwa)


    @action(detail=True, methods=['GET'])
    def replies(self, request, manhwa_pk=None, pk=None):
        replies_query_set = self.get_queryset()
        serializer = self.get_serializer(replies_query_set)
        return Response(serializer.data)


class ManhwaViewSet(ModelViewSet):
    pagination_class = CustomPagination
    filter_backends = [SearchFilter, DjangoFilterBackend, OrderingFilter]
    search_fields = ('en_title',)
    ordering_fields = ('publication_datetime', 'avg_rating')
    filterset_fields = ('day_of_week', 'genres', 'studio')
    # filterset_class = ManhwaFilter
    queryset = Manhwa.objects.prefetch_related( 'comments' ,'rates')

# ---- many query in filter --------
    def get_queryset(self):
        base_query = Manhwa.objects.prefetch_related('comments').all()
        if self.action == 'list':
            return base_query.prefetch_related('rates').annotate(
                avg_rating=Coalesce(Avg('rates__rating'), Value(0.0)),
            )
        # elif self.action in ('create',):
        #     return base_query.prefetch_related('genres')
        return base_query

    def get_serializer_class(self):
        match self.action:
            case 'rate':
                return srilzr.ManhwaRatingSerializer
            case 'set_view':
                return srilzr.SetViewManhwaSerializer
            case 'retrieve':
                return srilzr.DetailManhwaSerializer
            case 'create':
                return srilzr.CreateManhwaSerializer
            case _:
                return srilzr.ManhwaSerializer

    def get_permissions(self):
        if self.action in ('create', 'update', 'partial_update', 'destroy'):
            return [IsAdminUser()]
        elif self.action in ('set_view', 'rate'):
            return [IsAuthenticated()]
        return [AllowAny()]

    @action(detail=True, methods=['post'])
    def set_view(self, request, pk=None):
        view_obj, created = View.objects.get_or_create(
            user=request.user,
            manhwa_id=pk
        )
        if created:
            Manhwa.objects.filter(pk=pk).update(views_count=F('views_count') + 1)
            return Response(status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_200_OK)

    @action(detail=True, methods=['post', 'get'])
    def rate(self, request, pk=None):
        serializer_class = self.get_serializer_class()

        if request.method == 'GET':
            serializer = serializer_class(get_object_or_404(Rate, user=request.user, manhwa_id=pk))
            return Response(serializer.data, status=status.HTTP_200_OK)

        serializer = serializer_class(data=request.data, context={'request': request, 'manhwa_id': pk})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED if serializer.was_created else status.HTTP_200_OK)


class EpisodeViewSet(ReadOnlyModelViewSet):
    serializer_class = srilzr.EpisodeSerializer

    def get_queryset(self):
        manhwa_pk = self.kwargs.get('manhwa_pk')
        return Episode.objects.filter(manhwa_id=manhwa_pk)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_reaction_handler(request):
    serializer = srilzr.CommentReactionToggleSerializer(data=request.data)
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
        comment_data = Comment.objects.only('id', 'likes_count', 'dis_likes_count').get(pk=comment_id)
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

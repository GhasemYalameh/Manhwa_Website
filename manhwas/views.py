import requests

from django.db import connection
from django.db.models import Avg, F, Value, Subquery, OuterRef, Prefetch
from django.db.models.functions import Coalesce
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.template.loader import render_to_string
from django.utils.functional import cached_property

from rest_framework import status
from rest_framework.decorators import action, api_view
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet, ModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend

from . import serializers as srilzr
from .models import Manhwa, View, CommentReAction, Comment, Episode, Ticket, Rate, TicketMessage
from .paginations import CustomPagination
from .permissions import IsOwnerOrAdmin
from .services import ManhwaService


def health_check(request):
    return JsonResponse({'status': 'ok'})


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


# class TicketApiView(ListCreateAPIView):
#     permission_classes = (IsAuthenticated,)
#     filter_backends = (DjangoFilterBackend,)
#     filterset_fields = ('viewing_status',)
#
#     def get_queryset(self):
#         query = Ticket.objects.prefetch_related('messages').all()
#         if self.request.method == 'GET' and not self.request.user.is_staff:
#             return query.filter(user=self.request.user)
#         return query
#
#     def get_serializer_class(self):
#         if self.request.method == 'POST':
#             return srilzr.CreateTicketSerializer
#         elif self.request.method == 'GET':
#             return srilzr.ListTicketSerializer
#         return srilzr.ListTicketSerializer
#

class TicketViewSet(ModelViewSet):
    http_method_names = ('get', 'post',)
    permission_classes = (IsOwnerOrAdmin, IsAuthenticated)
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('viewing_status',)

    def get_queryset(self):
        query = Ticket.objects.select_related('user').prefetch_related('messages').all()
        if self.action == 'list' and not self.request.user.is_staff:
            return query.filter(user=self.request.user)
        return query

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return srilzr.CreateTicketSerializer
        elif self.request.method == 'GET':
            return srilzr.ListTicketSerializer
        return srilzr.ListTicketSerializer


class TicketMessageViewSet(ModelViewSet):
    permission_classes = [IsOwnerOrAdmin]
    http_method_names = ('get', 'post', 'patch', 'delete',)

    def list(self, request, *args, **kwargs):
        # check owner of ticket
        ticket_obj = self.check_ticket_object_owner(request, pk=self.kwargs['ticket_pk'])
        serializer = self.get_serializer(ticket_obj)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        # check ticket owner
        self.check_ticket_object_owner(request, pk=self.kwargs.get('pk'))
        return super().create(request, *args, **kwargs)

    def get_queryset(self):
        ticket_id = int(self.kwargs['ticket_pk'])
        if self.action in ('list', 'create'):
            return Ticket.objects.select_related('user').filter(pk=ticket_id)
        return TicketMessage.objects.select_related('user').filter(ticket_id=ticket_id)

    def get_serializer_context(self):
        context = {'ticket_id': self.kwargs['ticket_pk'],}
        return {**context, **super().get_serializer_context()}

    def get_serializer_class(self):
        match self.action:
            case 'list':
                return srilzr.ListTicketMessagesSerializer
            case 'partial_update':
                return srilzr.UpdateTicketMessageSerializer
            case 'retrieve':
                return srilzr.GetTicketMessageSerializer
            case _:
                return srilzr.CreateTicketMessageSerializer

    def check_ticket_object_owner(self, request, pk):
        """
        check Ticket owner permission before create or list TicketMessages.
        returns Ticket object if permission trusted.
        """
        queryset = self.get_queryset()
        ticket_obj = get_object_or_404(queryset, pk=pk)
        self.check_object_permissions(request, ticket_obj)
        return ticket_obj

# class TicketMessagesApiView(RetrieveAPIView, CreateAPIView):
#     queryset = Ticket.objects.prefetch_related('messages').all()
#     permission_classes = [IsOwnerOrAdmin]
#
#     def post(self, request, *args, **kwargs):
#         self.get_object()
#         return super().post(request, *args, **kwargs)
#
#     def get_serializer_context(self):
#         context = {'ticket': self.kwargs['pk'],}
#         return {**context, **super().get_serializer_context()}
#
#     def get_serializer_class(self):
#         if self.request.method == 'GET':
#             return srilzr.ListTicketMessagesSerializer
#         return srilzr.CreateTicketMessageSerializer


class CommentViewSet(ModelViewSet):
    pagination_class = CustomPagination
    http_method_names = ['get', 'post', 'patch', 'delete']

    @cached_property
    def manhwa(self):
        manhwa_pk = self.kwargs['manhwa_pk']
        return get_object_or_404(Manhwa, pk=manhwa_pk)

    def get_permissions(self):
        match self.action:
            case 'create':
                return [IsAuthenticated()]
            case 'partial_update' | 'destroy':
                return [IsOwnerOrAdmin()]
            case _:
                return [AllowAny()]
# ------ use cache for updating reactions instead  of directly to db -------
    def get_queryset(self):
        pk = self.kwargs.get('pk')
        base_qs = Comment.objects.filter(manhwa=self.manhwa)
        optimized_qs = base_qs.prefetch_related(
            Prefetch('children',queryset=Comment.objects.select_related('author'))
        ).select_related('author')

        match self.action:
            case 'create':
                return base_qs
            case 'list':
                query = optimized_qs.filter(level=0)
                return query if not self.request.user.is_authenticated else query.annotate(
                    user_reaction=Coalesce(
                        Subquery(CommentReAction.objects.filter(
                            user_id=self.request.user.id,
                            comment_id=OuterRef('pk')
                            ).values('reaction')),
                        Value('no-reaction')
                    ),
                )

        return base_qs.filter(pk=pk)  # create, detail

    def get_serializer_class(self):
        match self.action:
            case 'replies':
                return srilzr.CommentDetailSerializer
            case 'create':
                return srilzr.CreateCommentSerializer
            case 'reaction':
                return srilzr.CommentReActionSerializer
            case 'partial_update':
                return srilzr.UpdateCommentSerializer
            case _:
                return srilzr.RetrieveCommentSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, manhwa=self.manhwa)


    @action(detail=True, methods=['GET'])
    def replies(self, request, manhwa_pk=None, pk=None):
        comment_obj = self.get_object()
        serializer = self.get_serializer(comment_obj)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def reaction(self, request, manhwa_pk=None, pk=None):
        comment = self.get_object()
        serializer = self.get_serializer(data=request.data, context={'request': request, 'comment_id': pk})
        serializer.is_valid(raise_exception=True)
        serializer.save()

        comment.refresh_from_db()
        comment_data = {'likes_count': comment.likes_count, 'dis_likes_count': comment.dis_likes_count}

        return Response({'action': serializer.action, 'comment': comment_data, 'reaction': serializer.data}, status=status.HTTP_200_OK)


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
        base_query = Manhwa.objects.prefetch_related('rates', 'comments').all()
        if self.action == 'list':
            return base_query.annotate(
                avg_rating=Coalesce(Avg('rates__rating'), Value(0.0)),
            )
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
        elif self.action in ('set_view', 'rate', 'cache_view'):
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
        self.get_object()
        if request.method == 'GET':
            serializer = self.get_serializer(get_object_or_404(Rate, user=request.user, manhwa_id=pk))
            return Response(serializer.data, status=status.HTTP_200_OK)

        serializer = self.get_serializer(data=request.data, context={'request': request, 'manhwa_id': pk})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED if serializer.was_created else status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def cache_view(self, request, pk=None):
        self.get_object()
        if ManhwaService().is_exist_view(manhwa_id=pk, user_id=request.user.pk):
            return Response({'tracked': False, 'message': 'view exists in cache.'}, status=status.HTTP_200_OK)

        if View.objects.filter(user=request.user, manhwa_id=pk).exists():
            return Response({'tracked': False, 'message': 'view exists in db.'}, status=status.HTTP_200_OK)

        ManhwaService().track_view(user_id=request.user.id, manhwa_id=pk)
        return Response({'tracked': True, 'message': 'view added.'}, status=status.HTTP_200_OK)


class EpisodeViewSet(ReadOnlyModelViewSet):
    serializer_class = srilzr.EpisodeSerializer

    def get_queryset(self):
        manhwa_pk = self.kwargs.get('manhwa_pk')
        return Episode.objects.filter(manhwa_id=manhwa_pk)


def delete_db(model_class):
    table_name = model_class._meta.db_table
    with connection.cursor() as cursor:
        cursor.execute(f"DELETE FROM {table_name}")
        cursor.execute(f"DELETE FROM sqlite_sequence WHERE name='{table_name}'")

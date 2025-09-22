from pyexpat.errors import messages
from re import search

from django.db.transaction import atomic
from django.template.defaultfilters import title
from rest_framework import serializers

from django.db import IntegrityError, transaction
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

from .models import Manhwa, CommentReAction, Comment, Episode, Ticket, TicketMessage, Rate


class CreateCommentSerializer(serializers.ModelSerializer):
    author = serializers.CharField(source='author.username', read_only=True)

    class Meta:
        model = Comment
        fields = ('id', 'author', 'text', 'parent',)

    def validate_text(self, value):
        is_html = search(r'<[^>]+>', value)
        if is_html:
            raise serializers.ValidationError('text cant be included html tags.')

        return value

    def create(self, validated_data):
        try:
            return Comment.objects.create(**validated_data)

        except ValidationError as e:
            raise serializers.ValidationError(e.message_dict)

        except IntegrityError as e:
            raise serializers.ValidationError({
                'non_field_error': _('same text for comment not allowed.')
            })


class RetrieveCommentSerializer(serializers.ModelSerializer):
    author = serializers.CharField(source='author.username', read_only=True)
    replies_count = serializers.SerializerMethodField()
    user_reaction = serializers.CharField(max_length=1, read_only=True)

    class Meta:
        model = Comment
        fields = (
            'id', 'author', 'text', 'parent',
            'level', 'likes_count', 'dis_likes_count',
            'replies_count', 'user_reaction'
        )

    def get_replies_count(self, obj):
        return obj.children.count()


class CommentDetailSerializer(serializers.ModelSerializer):
    author = serializers.CharField(source='author.username', read_only=True)
    replies = RetrieveCommentSerializer(source='children', many=True, read_only=True)
    replies_count = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ('id', 'author', 'text', 'parent', 'level', 'likes_count', 'dis_likes_count', 'replies_count', 'replies')

    def get_replies_count(self, obj):
        return obj.children.count()


class ManhwaSerializer(serializers.ModelSerializer):
    comments_count = serializers.IntegerField(source='comments.count', read_only=True)
    cover = serializers.URLField(source='cover.url', read_only=True)
    avg_rating = serializers.DecimalField(max_digits=3, decimal_places=1)

    class Meta:
        model = Manhwa
        fields = ['id', 'en_title', 'avg_rating', 'season', 'day_of_week', 'last_upload', 'views_count', 'comments_count', 'cover']  # + 'comments'


class ManhwaRatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rate
        fields = ('rating',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._was_created = False

    def create(self, validated_data):
        manhwa_id = self.context['manhwa_id']
        user = self.context['request'].user
        rate_obj, self._was_created = Rate.objects.update_or_create(user=user, manhwa_id=manhwa_id, defaults=validated_data)
        return rate_obj

    @property
    def was_created(self):
        return self._was_created


class CommentReactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommentReAction
        fields = ('id', 'user', 'comment', 'reaction',)
        read_only_fields = ('id', 'user')


class CommentReectionToggleSerializer(serializers.Serializer):
    comment_id = serializers.IntegerField()
    reaction = serializers.ChoiceField(choices=CommentReAction.COMMENT_REACTIONS)

    def validate_comment_id(self, value):
        """check existing of comment"""
        try:
            Comment.objects.get(pk=value)
        except Comment.DoesNotExist:
            raise serializers.ValidationError("comment not fount")

        return value


class ManhwaViewSerializer(serializers.Serializer):
    manhwa_id = serializers.IntegerField()

    def validate_manhwa_id(self, value):
        try:
            Manhwa.objects.get(pk=value)
        except Manhwa.DoesNotExist:
            raise serializers.ValidationError('manhwa not found')

        return value


class EpisodeSerializer(serializers.ModelSerializer):
    file = serializers.URLField(source='file.url')

    class Meta:
        model = Episode
        fields = ['id', 'number', 'file', 'datetime_created']


class ListTicketSerializer(serializers.ModelSerializer):
    messages_count = serializers.IntegerField(source='messages.count')
    class Meta:
        model = Ticket
        fields = ('id', 'title', 'user', 'viewing_status', 'messages_count', 'created_at',)


class CreateTicketSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=150, default='No Title')
    text = serializers.CharField(max_length=500, write_only=True)

    @transaction.atomic
    def create(self, validated_data):
        """
        create a ticket object and TicketMessage object.
        need to send user obj through the context.
        """
        ticket_obj = Ticket.objects.create(
            title=validated_data.get('title'),
            user=self.context['request'].user,
        )
        TicketMessage.objects.create(
            ticket=ticket_obj,
            text=validated_data['text'],
            user=self.context['request'].user,
        )
        return ticket_obj


class TicketMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = TicketMessage
        fields = ('text', 'message_sender', 'created_at', 'modified_at',)


class RetrieveTicketMessagesSerializer(serializers.ModelSerializer):
    messages = TicketMessageSerializer(many=True, read_only=True)
    class Meta:
        model = Ticket
        fields = ('id', 'title', 'user', 'messages',)


class CreateTicketMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = TicketMessage
        fields = ('id', 'text', 'created_at')
        read_only_fields = ('id', 'created_at',)

    def save(self, **kwargs):
        is_admin = self.context['request'].user.is_staff
        data = {
            'ticket_id': self.context['ticket'],
            'user': self.context['request'].user,
            'message_sender': TicketMessage.ADMIN if is_admin else TicketMessage.USER,
        }
        return super().save(**kwargs, **data)



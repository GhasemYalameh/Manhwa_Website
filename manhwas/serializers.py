from re import search

from django.db.models import Exists, OuterRef
from rest_framework import serializers

from django.db import IntegrityError
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

from .models import Manhwa, Comment, CommentReAction, CommentReply, View


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.CharField(source='author.username', read_only=True)

    class Meta:
        model = Comment
        fields = ('id', 'author', 'text', 'manhwa', 'likes_count', 'dis_likes_count')

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

        except IntegrityError:
            raise serializers.ValidationError({
                'non_field_error': _('same text for comment not allowed.')
            })


class CommentDetailSerializer(serializers.ModelSerializer):
    author = serializers.CharField(source='author.username', read_only=True)
    replies = CommentSerializer(source='comment_replies', many=True, read_only=True)
    replies_count = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ('id', 'author', 'text', 'likes_count', 'dis_likes_count', 'replies_count', 'replies')

    def get_replies_count(self, obj):
        return obj.replies.count()


class ManhwaSerializer(serializers.ModelSerializer):
    # comments = CommentSerializer(many=True, read_only=True)
    comments_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Manhwa
        fields = ['id', 'en_title', 'season', 'day_of_week', 'views_count', 'comments_count']  # + 'comments'

    #  <------ N+1 Query issue ---------->
    def get_comments_count(self, obj: Manhwa):
        return obj.comments.prefetch_related('comments').annotate(
            is_replied=Exists(CommentReply.objects.filter(replied_comment_id=OuterRef('pk')))
        ).filter(is_replied=False).count()
    # <------- Handle this part ---------->


class CommentReactionSerializer(serializers.ModelSerializer):
    likes_count = serializers.IntegerField(source='comment.likes_count')
    dis_likes_count = serializers.IntegerField(source='comment.dis_likes_count')

    class Meta:
        model = CommentReAction
        fields = ('id', 'user', 'comment', 'reaction',  'likes_count', 'dis_likes_count')
        read_only_fields = ('id', 'user', 'likes_count', 'dis_likes_count')


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


class ViewSerializer(serializers.Serializer):
    manhwa_id = serializers.IntegerField()

    def validate_manhwa_id(self, value):
        try:
            Manhwa.objects.get(pk=value)
        except Manhwa.DoesNotExist:
            raise serializers.ValidationError('manhwa not found')

        return value

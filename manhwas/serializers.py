from re import search

from rest_framework import serializers

from django.db import IntegrityError
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

from .models import Manhwa, CommentReAction, NewComment


class NewCommentSerializer(serializers.ModelSerializer):
    author = serializers.CharField(source='author.username', read_only=True)
    replies_count = serializers.SerializerMethodField()

    class Meta:
        model = NewComment
        fields = ('id', 'author', 'text', 'parent', 'level', 'likes_count', 'dis_likes_count', 'replies_count')
        read_only_fields = ('id', 'level', 'likes_count', 'dis_likes_count', 'replies_count')

    def get_replies_count(self, obj):
        return obj.childes.count()

    def validate_text(self, value):
        is_html = search(r'<[^>]+>', value)
        if is_html:
            raise serializers.ValidationError('text cant be included html tags.')

        return value

    def create(self, validated_data):
        try:
            return NewComment.objects.create(**validated_data)

        except ValidationError as e:
            raise serializers.ValidationError(e.message_dict)

        except IntegrityError as e:
            raise serializers.ValidationError({
                'non_field_error': _('same text for comment not allowed.')
            })


class CommentDetailSerializer(serializers.ModelSerializer):
    author = serializers.CharField(source='author.username', read_only=True)
    replies = NewCommentSerializer(source='childes', many=True, read_only=True)
    replies_count = serializers.SerializerMethodField()

    class Meta:
        model = NewComment
        fields = ('id', 'author', 'text', 'parent', 'level', 'likes_count', 'dis_likes_count', 'replies_count', 'replies')

    def get_replies_count(self, obj):
        return obj.childes.count()


class ManhwaSerializer(serializers.ModelSerializer):
    comments_count = serializers.IntegerField(source='comments.count', read_only=True)

    class Meta:
        model = Manhwa
        fields = ['id', 'en_title', 'season', 'day_of_week', 'views_count', 'comments_count']  # + 'comments'


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
            NewComment.objects.get(pk=value)
        except NewComment.DoesNotExist:
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

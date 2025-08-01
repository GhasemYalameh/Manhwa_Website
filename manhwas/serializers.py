from re import search

from rest_framework import serializers

from django.db import IntegrityError
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

from .models import Manhwa, Genre, Comment


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.CharField(source='author.username', read_only=True)
    replies_count = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ('id', 'author', 'text', 'manhwa', 'likes_count', 'dis_likes_count', 'replies_count')

    def get_replies_count(self, obj):
        return obj.replies.count()

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


class RepliedCommentSerializer(serializers.ModelSerializer):
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

    def get_comments_count(self, obj: Manhwa):
        return obj.comments.count()



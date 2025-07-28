from rest_framework import serializers

from .models import Manhwa, Genre, Comment


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField()

    class Meta:
        model = Comment
        fields = ('id', 'author', 'text', 'likes_count', 'dis_likes_count')


class ManhwaSerializer(serializers.ModelSerializer):
    comments = CommentSerializer(many=True, read_only=True)
    comments_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Manhwa
        fields = ['id', 'en_title', 'season', 'day_of_week', 'views_count', 'comments_count', 'comments']

    def get_comments_count(self, obj: Manhwa):
        return obj.comments.count()

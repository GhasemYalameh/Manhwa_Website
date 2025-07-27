from rest_framework import serializers

from .models import Manhwa, Genre, Comment


class ManhwaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Manhwa
        fields = ['id', 'en_title', 'season', 'day_of_week', 'views_count']

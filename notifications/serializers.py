from rest_framework import serializers

from .models import Notification
from manhwas.serializers import EpisodeSerializer, RetrieveCommentSerializer
from manhwas.models import Episode, Comment


class ListNotificationSerializer(serializers.ModelSerializer):
    target_content_type = serializers.SerializerMethodField()
    target_object = serializers.SerializerMethodField()
    class Meta:
        model = Notification
        fields = (
            'id','sender', 'target_content_type', 'target_object', 'is_read',
            'notif_level','notif_type', 'created_at',
        )

    def get_target_content_type(self, obj):
        if obj.target_content_type:
            return obj.target_content_type.model
        return None

    def get_target_object(self, obj):
        if not obj.target_object:
            return None
        obj = obj.target_object
        if isinstance(obj, Episode):
            return EpisodeSerializer(obj).data
        elif isinstance(obj, Comment):
            return RetrieveCommentSerializer(obj).data
        return None


class PatchNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ('is_read',)
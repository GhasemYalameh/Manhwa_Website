from rest_framework import serializers

from .models import Notification


class ListNotificationSerializer(serializers.ModelSerializer):
    target_content_type = serializers.SerializerMethodField()
    class Meta:
        model = Notification
        fields = (
            'id','sender', 'target_content_type', 'is_read',
            'notif_level','notif_type', 'created_at',
        )

    def get_target_content_type(self, obj):
        if obj.target_content_type:
            return obj.target_content_type.model
        return None


class PatchNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ('is_read',)
from rest_framework import serializers

from .models import Notification


class ListNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = (
            'recipient', 'sender', 'is_read', 'notif_level',
            'notif_type', 'created_at', 'target_content_type',
            'target_object',
        )


class PatchNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ('is_read',)
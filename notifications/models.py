from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from config.settings import AUTH_USER_MODEL


class Notification(models.Model):
    NOTIFICATION_LEVEL = (
        (SUCCESS:= 'SUC', 'Success'),   (INFO:= 'INF', 'Info'),
        (WARNING:= 'WAR', 'Warning'),   (FAIL:= 'FAL', 'Fail'),
    )

    recipient = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    sender = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.SET_NULL)

    title = models.CharField(max_length=200)
    message = models.TextField(blank=True)
    is_read = models.BooleanField(default=False)
    level = models.CharField(choices=NOTIFICATION_LEVEL, max_length=10)

    target_content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    target_object_id = models.PositiveIntegerField()
    target_object = GenericForeignKey('target_content_type', 'target_object_id')

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-created_at',)
        indexes=(
            models.Index(fields=['target_content_type', 'target_object_id']),
            models.Index(fields=['recipient', 'is_read']),
        )

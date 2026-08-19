from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from manhwas.paginations import CustomPagination
from .models import Notification
from .serializers import ListNotificationSerializer, PatchNotificationSerializer


class NotificationViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    http_method_names = ('get', 'patch',)
    pagination_class = CustomPagination

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ListNotificationSerializer
        return PatchNotificationSerializer

    def get_queryset(self):
        base_q = Notification.objects.select_related('sender', 'target_content_type').order_by('-created_at').all()
        user = self.request.user
        if user.is_staff :
            return base_q
        return base_q.filter(recipient_id=user.id)



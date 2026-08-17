from rest_framework.generics import GenericAPIView
from rest_framework.mixins import UpdateModelMixin, ListModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from .models import Notification
from .serializers import ListNotificationSerializer, PatchNotificationSerializer

# Create your views here.
class NotificationViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    http_method_names = ('get', 'patch',)

    # def get(self, request, *args, **kwargs):
    #     return self.list(request, *args, **kwargs)

    # def patch(self, request, *args, **kwargs):
    #     return self.partial_update(request, *args, **kwargs)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ListNotificationSerializer
        return PatchNotificationSerializer

    def get_queryset(self):
        base_q = Notification.objects.all()
        user = self.request.user
        if user.is_staff :
            return base_q
        return base_q.filter(recipient_id=user.id)



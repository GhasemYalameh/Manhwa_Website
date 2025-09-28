from rest_framework import permissions
from .models import Comment, Ticket, TicketMessage


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    a permission class to check a user is an owner of an object or is an admin.
    """
    def has_object_permission(self, request, view, obj):
        if isinstance(obj, Ticket):
            return bool(request.user and (request.user.is_staff or request.user == obj.user))
        elif isinstance(obj, Comment):
            return bool(request.user and (request.user.is_staff or request.user == obj.author))
        return False

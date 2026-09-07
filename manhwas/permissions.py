from django.shortcuts import get_object_or_404
from rest_framework import permissions
from .models import Comment, Ticket, TicketMessage


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    a permission class to check a user is an owner of an object or is an admin.

    this permission used for Comment, Ticket and TicketMessage models.
    """
    # def has_object_permission(self, request, view, obj):
    #     # if isinstance(obj, (Ticket, TicketMessage)):
    #     #     return bool(request.user and (request.user.is_staff or request.user == obj.user))
    #     if isinstance(obj, Comment):
    #         return bool(request.user and (request.user.is_staff or request.user == obj.author))
    #     return False
    
    def has_permission(self, request, view):
        ticket_id = view.kwargs.get('ticket_pk') 

        ticket_obj = get_object_or_404(Ticket, id=ticket_id)
        if ticket_obj.is_accessible_by(request.user):
            return True
        return False
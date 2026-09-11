from django.shortcuts import get_object_or_404
from rest_framework import permissions
from .models import Comment, Ticket, TicketMessage


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    a permission class to check a user is an owner of an object or is an admin.
    this permission used for TicketMessage models.
    """
    def has_permission(self, request, view):
        ticket_id = view.kwargs.get('ticket_pk') 

        ticket_obj = get_object_or_404(Ticket, id=ticket_id)
        if ticket_obj.is_accessible_by(request.user):
            return True
        return False
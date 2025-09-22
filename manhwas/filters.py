from django_filters import FilterSet

from .models import Ticket, TicketMessage

class TicketFilter(FilterSet):
    class Meta:
        model = Ticket
        fields = {
            'ticket': ('exact',),
            'viewing_status': ('exact',)
        }
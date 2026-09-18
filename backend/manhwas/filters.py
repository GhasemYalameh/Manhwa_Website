from django_filters import FilterSet

from .models import Manhwa

class ManhwaFilter(FilterSet):
    class Meta:
        model = Manhwa
        fields = {
            'day_of_week': ('exact',),
            'genres': ('exact',),
            'studio': ('exact',),
            'avg_rating': ('exact',),
        }
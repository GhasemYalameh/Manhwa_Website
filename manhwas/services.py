from django.core.cache import cache
from django.db.models import F

from .models import Manhwa

class ViewTracker:
    @staticmethod
    def track_view(manhwa_id:int, user_id:int)-> bool:
        """"""
        manhwa_view_key = f'manhwa:{manhwa_id}:viewed_by:{user_id}'
        if cache.get(manhwa_view_key):
            return False

        cache.set(manhwa_view_key, "1", 60*60)
        counter_key = f'manhwa:{manhwa_id}:pending_views'
        cache.add(counter_key, 0, None)  # if key not exist, add it and set its value to 0
        cache.incr(counter_key, 1)
        return True

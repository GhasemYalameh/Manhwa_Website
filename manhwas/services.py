from django.db.models import Avg, Count, When, Case
from django.db.models.functions import Round
from django.shortcuts import get_object_or_404
from django_redis import get_redis_connection
from django.core.cache import cache

from manhwas.models import Manhwa


class ManhwaService:
    def __init__(self):
        self.redis = get_redis_connection('default')
        self.manhwa_viewers_key = 'manhwa:{}:viewers_id'
        self.manhwa_rating_data_key = 'manhwa:{}:rating_data'


    def get_rating_data(self, obj)-> dict:
        """
        return rating data for given manhwa_id from cache.
        """
        manhwa_rating_key = self.manhwa_rating_data_key.format(obj.id)
        rating_data = cache.get(manhwa_rating_key)
        if rating_data:
            return rating_data

        query_set = obj.rates.aggregate(
            avg_rating=Avg('rating', ),
            raters_count=Count('id'),
            fives_count=Count(Case(When(rating=5, then=1))),
            fours_count=Count(Case(When(rating=4, then=1))),
            threes_count=Count(Case(When(rating=3, then=1))),
            twos_count=Count(Case(When(rating=2, then=1))),
            ones_count=Count(Case(When(rating=1, then=1)))
        )
        rating_data = dict(query_set)
        cache.set(manhwa_rating_key, rating_data, timeout=600)
        return rating_data


    def track_view(self, manhwa_id:int, user_id:int)-> bool:
        """
        adding user_id to cache. check user_id exists in cache.
        returns true if user exists in cache, false otherwise.
        """
        manhwa_viewers_key = self.manhwa_viewers_key.format(manhwa_id)
        added = self.redis.sadd(manhwa_viewers_key, user_id) # returns true if user_id added to set.
        return added


    def is_exist_view(self, manhwa_id, user_id)-> bool:
        manhwa_viewers_key = self.manhwa_viewers_key.format(manhwa_id)
        is_member = self.redis.sismember(manhwa_viewers_key, user_id)
        return is_member

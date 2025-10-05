from django_redis import get_redis_connection

class ViewTracker:
    def __init__(self):
        self.redis = get_redis_connection('default')

    def track_view(self, manhwa_id:int, user_id:int)-> bool:
        """
        adding user_id to cache. check user_id exists in cache.
        returns true if user exists in cache, false otherwise.
        """
        manhwa_users_set_key = f'manhwa:{manhwa_id}:users_id'
        added = self.redis.sadd(manhwa_users_set_key, user_id, ex=15*60)  # returns True if user id added to set.
        if not added:
            return False

        return True

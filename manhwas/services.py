from django_redis import get_redis_connection

class ViewTracker:
    def __init__(self):
        self.redis = get_redis_connection('default')
        self.manhwa_viewers_key = 'manhwa:{}:viewers_id'

    def track_view(self, manhwa_id:int, user_id:int)-> bool:
        """
        adding user_id to cache. check user_id exists in cache.
        returns true if user exists in cache, false otherwise.
        """
        manhwa_viewers_key = self.manhwa_viewers_key.format(manhwa_id)
        added = self.redis.sadd(manhwa_viewers_key, user_id) # returns true if user_id added to set.
        return added


    def is_exist(self, manhwa_id, user_id):
        manhwa_viewers_key = self.manhwa_viewers_key.format(manhwa_id)
        is_member = self.redis.sismember(manhwa_viewers_key, user_id)
        return is_member

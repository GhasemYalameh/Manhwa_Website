from django.db.models import Avg, Count, When, Case
from django.utils.text import slugify
from django_redis import get_redis_connection
from django.core.cache import cache

import os

class ManhwaService:
    def __init__(self):
        self.redis = get_redis_connection('default')
        self.manhwa_viewers_key = 'manhwa:{}:viewers_id'
        self.manhwa_rating_data_key = 'manhwa:{}:rating_data'


    def get_rating_data(self, obj)-> dict:
        """
        return rating data from cache for given manhwa_id.
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


STOP_WORDS = {
    'the', 'a', 'an', 'of', 'to', 'in', 'on', 'at', 'for', 'with', 'by',
    'from', 'up', 'about', 'into', 'over', 'after', 'why', 'how', 'what',
    'when', 'where', 'who', 'which', 'is', 'are', 'was', 'were', 'be', 'been',
    'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
    'could', 'should', 'may', 'might', 'must', 'shall', 'can', 'need',
    'i', 'my', 'me', 'we', 'our', 'you', 'your', 'he', 'she', 'it', 'they',
    'and', 'or', 'but', 'so', 'if', 'as', 'than', 'that', 'this', 'these',
    'those', 'then', 'there', 'here', 'just', 'only', 'also', 'even', 'still'
}

def generate_manhwa_slug(title: str, max_length: int = 50) -> str:
    """
    using slugify for base slug. then removing Stop Words like 
    or, the, you, so, etc from the sentence. 
    and also keep the length of slug less than Max Length by removing 
    last word.
    """
    base = slugify(title)

    if not base:
        return "untitled"
    
    words = base.split('-')
    filtered = [w for w in words if w and w not in STOP_WORDS]
    
    if not filtered:  # if all words removed, use words
        filtered = words
    
    while filtered:
        candidate = '-'.join(filtered)
        if len(candidate) <= max_length:
            return candidate
        filtered.pop() 
    
    return '-'.join(words)[:max_length].rstrip('-')


def manhwa_file_upload_to(instance, filename):
    """
    creating manhwa file path by using manhwa title, season number and
    Episode number.
    output: Manhwa/<manhwa_title>/season-<season_number>/Episode/<file_name>
    """
    manhwa_title = instance.manhwa.en_title
    manhwa_season = instance.manhwa.season
    season = str(manhwa_season)

    return os.path.join('Manhwa', slugify(manhwa_title), slugify('Season ' + season), 'Episodes', filename)

def manhwa_cover_upload_to(instance, filename):
    """
    creating manhwa cover path by using manhwa title, season and file name.
    
    output: Manhwas/<manhwa_title>/season-<manhwa_season>/Covers/filename
    """
    manhwa_title = instance.en_title
    manhwa_season = instance.season
    season = str(manhwa_season)

    # manhwas/title/season/covers/filename
    return os.path.join('Manhwa', slugify(manhwa_title), slugify("Season " + season), 'Covers', filename)

def N(number) -> str:
    """
    making the numbers in two digits 
    like 3 -> 03 or 9 -> 09
    """
    # if number less than 10
    #  1-9  -> 01-09
    return f'0{number}' if number < 10 else str(number)

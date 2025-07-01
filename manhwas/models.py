import os.path

from django.db import models
from django.utils.text import slugify


def manhwa_file_upload_to(instance, filename):
    # استفاده از slugify برای تمیز کردن عنوان و جلوگیری از مشکلات مسیر
    manhwa_title = instance.manhwa.title
    manhwa_season = instance.manhwa.season
    title = manhwa_title[:10] if len(manhwa_title > 10) else manhwa_title  # length of title most be less than 10
    season = str(manhwa_season)

    # manhwas/title/season/episodes/filename
    return os.path.join('manhwa', slugify(title), slugify(season), 'episodes', filename)


def manhwa_cover_upload_to(instance, filename):
    manhwa_title = instance.manhwa.title
    manhwa_season = instance.manhwa.season
    title = manhwa_title[:10] if len(manhwa_title > 10) else manhwa_title  # length of title most be less than 10
    season = str(manhwa_season)

    # manhwas/title/season/covers/filename
    return os.path.join('manhwa', slugify(title), slugify(season), 'covers', filename)


class Genre(models.Model):
    title = models.CharField(max_length=200)
    description = models.CharField(max_length=500)


class Studio(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()


class Manhwa(models.Model):
    DAY_OF_THE_WEEK = (
        ('sat', 'Saturday'),
        ('sun', 'Sunday'),
        ('mon', 'Monday'),
        ('tue', 'Tuesday'),
        ('wed', 'Wednesday'),
        ('thu', 'thursday'),
        ('fri', 'Friday'),
    )
    AGE_RANGE = (
        ('all', 'All people'),
        ('adult', 'older than 18'),
        ('child', 'less than 13'),
        ('teen', 'older than 13'),
    )
    fa_title = models.CharField(max_length=500, blank=True)
    en_title = models.CharField(max_length=500)
    summary = models.TextField()
    season = models.PositiveIntegerField(default=1)
    day_of_week = models.CharField(max_length=30, choices=DAY_OF_THE_WEEK)
    cover = models.ImageField(upload_to=manhwa_cover_upload_to)
    publication_datetime = models.DateTimeField()
    # genre method
    studio = models.ForeignKey(Studio, on_delete=models.PROTECT, related_name='manhwas')
    views = models.PositiveIntegerField(default=0)

    datetime_created = models.DateTimeField(auto_now_add=True)
    datetime_modified = models.DateTimeField(auto_now=True)

    # status
    # rating
    # IMDB rating

    # add views
    # age_limit


class ManhwaGenre(models.Model):
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE, related_name='manhwas')
    manhwa = models.ForeignKey(Manhwa, on_delete=models.CASCADE, related_name='genres')


class Episode(models.Model):
    number = models.PositiveIntegerField(default=1)
    manhwa = models.ForeignKey(Manhwa, on_delete=models.PROTECT, related_name='episodes')
    file = models.FileField(upload_to=manhwa_file_upload_to)
    downloads_count = models.PositiveIntegerField(default=0)

    datetime_created = models.DateTimeField(auto_now_add=True)
    datetime_modified = models.DateTimeField(auto_now=True)



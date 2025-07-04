import os.path

from django.db import models
from django.utils.text import slugify
from django.contrib.auth import get_user_model


def manhwa_file_upload_to(instance, filename):
    # استفاده از slugify برای تمیز کردن عنوان و جلوگیری از مشکلات مسیر
    manhwa_title = instance.manhwa.en_title
    manhwa_season = instance.manhwa.season
    season = str(manhwa_season)

    # manhwas/title/season/episodes/filename
    return os.path.join('Manhwa', slugify(manhwa_title), slugify('Season '+season), 'Episodes', filename)


def manhwa_cover_upload_to(instance, filename):
    manhwa_title = instance.en_title
    manhwa_season = instance.season
    season = str(manhwa_season)

    # manhwas/title/season/covers/filename
    return os.path.join('Manhwa', slugify(manhwa_title), slugify("Season "+season), 'Covers', filename)


class Genre(models.Model):
    title = models.CharField(max_length=200)
    description = models.CharField(max_length=500)

    def __str__(self):
        return self.title


class Studio(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()

    def __str__(self):
        return self.title


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
    genres = models.ManyToManyField(Genre, related_name='manhwas')
    studio = models.ForeignKey(Studio, on_delete=models.PROTECT, related_name='manhwas')
    views = models.PositiveIntegerField(default=0)

    datetime_created = models.DateTimeField(auto_now_add=True)
    datetime_modified = models.DateTimeField(auto_now=True)

    # status
    # rating
    # IMDB rating

    # add views
    # age_limit

    def __str__(self):
        return self.en_title


class View(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    manhwa = models.ForeignKey(Manhwa, on_delete=models.CASCADE, related_name='views')
    datetime_viewed = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('manhwa', 'user')


class Rate(models.Model):
    RATING_CHOICES = (
        (1, '1'),
        (2, '2'),
        (3, '3'),
        (4, '4'),
        (5, '5'),
    )
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    manhwa = models.ForeignKey(Manhwa, on_delete=models.CASCADE, related_name='rates')
    rating = models.PositiveSmallIntegerField(choices=RATING_CHOICES)

    class Meta:
        unique_together = ('user', 'manhwa')


class Episode(models.Model):
    number = models.PositiveIntegerField(default=1)
    manhwa = models.ForeignKey(Manhwa, on_delete=models.PROTECT, related_name='episodes')
    file = models.FileField(upload_to=manhwa_file_upload_to)
    downloads_count = models.PositiveIntegerField(default=0)

    datetime_created = models.DateTimeField(auto_now_add=True)
    datetime_modified = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('number', 'manhwa')

    def __str__(self):
        return str(self.number)



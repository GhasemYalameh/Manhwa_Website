import os.path

from django.db import models
from django.utils.text import slugify
from django.contrib.auth import get_user_model
from django.utils.translation import gettext as _


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
    title = models.CharField(max_length=200, verbose_name=_('title'))
    description = models.CharField(max_length=500, verbose_name='description')

    def __str__(self):
        return self.title


class Studio(models.Model):
    title = models.CharField(max_length=200, verbose_name=_('title'))
    description = models.TextField(verbose_name=_('description'))

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
    fa_title = models.CharField(max_length=500, blank=True, verbose_name=_('persian title'))
    en_title = models.CharField(max_length=500, verbose_name=_('english title'))
    summary = models.TextField(verbose_name=_('summary'))
    season = models.PositiveIntegerField(default=1, verbose_name=_('season'))
    day_of_week = models.CharField(max_length=30, choices=DAY_OF_THE_WEEK, verbose_name=_('day of the week'))
    cover = models.ImageField(upload_to=manhwa_cover_upload_to, verbose_name=_('manhwa cover'))
    publication_datetime = models.DateTimeField(verbose_name=_('publication datetime'))
    genres = models.ManyToManyField(Genre, related_name='manhwas', verbose_name=_('genre'))
    studio = models.ForeignKey(Studio, on_delete=models.PROTECT, related_name='manhwas', verbose_name=_('studio'))
    views_count = models.PositiveIntegerField(default=0, verbose_name=_('views count'))

    datetime_created = models.DateTimeField(auto_now_add=True, verbose_name=_('datetime created'))
    datetime_modified = models.DateTimeField(auto_now=True, verbose_name=_('datetime modified'))

    # status
    # rating
    # IMDB rating

    # add views
    # age_limit

    def __str__(self):
        return self.en_title


class View(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, verbose_name=_('user'))
    manhwa = models.ForeignKey(Manhwa, on_delete=models.CASCADE, related_name='views', verbose_name=_('manhwa'))
    datetime_viewed = models.DateTimeField(auto_now_add=True, verbose_name=_('datetime viewed'))

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
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, verbose_name=_('user'))
    manhwa = models.ForeignKey(Manhwa, on_delete=models.CASCADE, related_name='rates', verbose_name=_('manhwa'))
    rating = models.PositiveSmallIntegerField(choices=RATING_CHOICES, verbose_name=_('rating'))

    class Meta:
        unique_together = ('user', 'manhwa')


class Episode(models.Model):
    number = models.PositiveIntegerField(default=1, verbose_name=_('number of episode'))
    manhwa = models.ForeignKey(Manhwa, on_delete=models.PROTECT, related_name='episodes', verbose_name=_('manhwa'))
    file = models.FileField(upload_to=manhwa_file_upload_to, verbose_name=_('episode file'))
    downloads_count = models.PositiveIntegerField(default=0, verbose_name=_('download count'))

    datetime_created = models.DateTimeField(auto_now_add=True, verbose_name=_('datetime created'))
    datetime_modified = models.DateTimeField(auto_now=True, verbose_name=_('datetime modified'))

    class Meta:
        unique_together = ('number', 'manhwa')

    def __str__(self):
        return str(self.number)



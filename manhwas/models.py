from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.db.models import F, Avg, Count, Case, When
from django.utils.text import slugify
from django.utils.translation import gettext as _
from django_ckeditor_5.fields import CKEditor5Field

from config import settings

import os.path


def manhwa_file_upload_to(instance, filename):
    # استفاده از slugify برای تمیز کردن عنوان و جلوگیری از مشکلات مسیر
    manhwa_title = instance.manhwa.en_title
    manhwa_season = instance.manhwa.season
    season = str(manhwa_season)

    # manhwas/title/season/episodes/filename
    return os.path.join('Manhwa', slugify(manhwa_title), slugify('Season ' + season), 'Episodes', filename)


def manhwa_cover_upload_to(instance, filename):
    manhwa_title = instance.en_title
    manhwa_season = instance.season
    season = str(manhwa_season)

    # manhwas/title/season/covers/filename
    return os.path.join('Manhwa', slugify(manhwa_title), slugify("Season " + season), 'Covers', filename)


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
    SATURDAY, SUNDAY, MONDAY, TUESDAY = 'sat', 'sun', 'mon', 'tue'
    WEDNESDAY, THURSDAY, FRIDAY = 'wed', 'thu', 'fri'

    DAY_OF_THE_WEEK = (
        (SATURDAY, 'Saturday'), (SUNDAY, 'Sunday'), (MONDAY, 'Monday'), (TUESDAY, 'Tuesday'),
        (WEDNESDAY, 'Wednesday'), (THURSDAY, 'thursday'), (FRIDAY, 'Friday'),
    )
    AGE_RANGE = (
        ('all', 'All people'), ('adult', 'older than 18'),
        ('child', 'less than 13'), ('teen', 'older than 13'),
    )

    fa_title = models.CharField(max_length=500, blank=True, verbose_name=_('persian title'))
    en_title = models.CharField(max_length=500, verbose_name=_('english title'))
    summary = CKEditor5Field('Text', config_name='extends')
    season = models.PositiveIntegerField(default=1, verbose_name=_('season'))
    day_of_week = models.CharField(max_length=30, choices=DAY_OF_THE_WEEK, verbose_name=_('day of the week'))
    cover = models.ImageField(upload_to=manhwa_cover_upload_to, verbose_name=_('manhwa cover'))
    publication_datetime = models.DateTimeField(verbose_name=_('publication datetime'))
    genres = models.ManyToManyField(Genre, related_name='manhwas', verbose_name=_('genre'))
    studio = models.ForeignKey(Studio, on_delete=models.PROTECT, related_name='manhwas', verbose_name=_('studio'))
    views_count = models.PositiveIntegerField(default=0, verbose_name=_('views count'))

    datetime_created = models.DateTimeField(auto_now_add=True, verbose_name=_('datetime created'))
    datetime_modified = models.DateTimeField(auto_now=True, verbose_name=_('datetime modified'))

    # IMDB rating
    # age_limit

    def __str__(self):
        return self.en_title


class View(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='views',
        verbose_name=_('user')
    )
    manhwa = models.ForeignKey(Manhwa, on_delete=models.CASCADE, related_name='views', verbose_name=_('manhwa'))
    datetime_viewed = models.DateTimeField(auto_now_add=True, verbose_name=_('datetime viewed'))

    class Meta:
        unique_together = ('manhwa', 'user')

    def __str__(self):
        return f'user: {self.user.phone_number} manhwa: {self.manhwa.en_title}'


class Rate(models.Model):
    RATING_CHOICES = (
        (1, '1'), (2, '2'), (3, '3'),
        (4, '4'), (5, '5'),
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='rates',
        verbose_name=_('user')
    )
    manhwa = models.ForeignKey(Manhwa, on_delete=models.CASCADE, related_name='rates', verbose_name=_('manhwa'))
    rating = models.PositiveSmallIntegerField(choices=RATING_CHOICES, verbose_name=_('rating'))

    class Meta:
        unique_together = ('user', 'manhwa')

    @property
    def rating_data(self):
        query_set = self.__class__.objects.filter(manhwa_id=self.manhwa.id).aggregate(
            avg_rating=Avg('rating'),
            total_rates=Count('id'),
            fives_count=Count(Case(When(rating=5, then=1))),
            fours_count=Count(Case(When(rating=4, then=1))),
            threes_count=Count(Case(When(rating=3, then=1))),
            twos_count=Count(Case(When(rating=2, then=1))),
            ones_count=Count(Case(When(rating=1, then=1)))
        )
        return query_set


class Episode(models.Model):
    manhwa = models.ForeignKey(Manhwa, on_delete=models.PROTECT, related_name='episodes', verbose_name=_('episodes'))
    number = models.PositiveIntegerField(default=1, verbose_name=_('number of episode'))
    file = models.FileField(upload_to=manhwa_file_upload_to, verbose_name=_('episode file'))
    downloads_count = models.PositiveIntegerField(default=0, verbose_name=_('download count'))

    datetime_created = models.DateTimeField(auto_now_add=True, verbose_name=_('datetime created'))
    datetime_modified = models.DateTimeField(auto_now=True, verbose_name=_('datetime modified'))

    class Meta:
        unique_together = ('number', 'manhwa')
        ordering = ('number',)

    def __str__(self):
        return f'{self.manhwa.en_title}: {self.number}'


class NewComment(models.Model):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='new_comments'
        )
    manhwa = models.ForeignKey(Manhwa, on_delete=models.CASCADE, related_name='new_comments')
    text = models.TextField()

    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, default=None, related_name='childes')
    level = models.PositiveSmallIntegerField(default=0, editable=False)  # level of comment depth

    likes_count = models.PositiveIntegerField(default=0, editable=False)
    dis_likes_count = models.PositiveIntegerField(default=0, editable=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if self.parent:

            if self.manhwa_id != self.manhwa_id:
                raise ValidationError('parent & child must sign to same manhwa.')

            self.level = self.parent.level + 1  # set comment level
            if self.level >= 3:
                raise ValidationError('depth of comment cant more than 3.')

        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.id}'


class Comment(models.Model):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name=_('author')
    )
    manhwa = models.ForeignKey(Manhwa, on_delete=models.CASCADE, related_name='comments', verbose_name=_('manhwa'))
    text = models.TextField()
    likes_count = models.PositiveIntegerField(default=0, editable=False, verbose_name=_('Likes count'))
    dis_likes_count = models.PositiveIntegerField(default=0, editable=False, verbose_name=_('disLikes count'))

    datetime_created = models.DateTimeField(auto_now_add=True, verbose_name=_('datetime created'))
    datetime_modified = models.DateTimeField(auto_now=True, verbose_name=_('datetime modified'))

    class Meta:
        unique_together = ('manhwa', 'author', 'text')  # try except for same text and spam robot
        ordering = ('-datetime_created',)

    @property
    def comment_replies(self):
        replies = self.replies.all()
        return [reply.replied_comment for reply in replies]

    def __str__(self):
        return f'comment: {self.id} || {self.author.phone_number} || {self.manhwa.en_title}'


class CommentReply(models.Model):
    main_comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='replies')
    replied_comment = models.ForeignKey(Comment, on_delete=models.CASCADE)

    def __str__(self):
        return f'the {self.replied_comment.author.phone_number} replied to {self.main_comment.author.phone_number}'


class CommentReactionManager(models.Manager):
    def toggle_reaction(self, user, comment_id, reaction):
        """
        if reaction exist and reaction was different, will update it.
        if reaction was same, will delete it.
        if reaction not exist, will create it.

        returns: (reaction_obj, action)
        action may be: 'updated', 'deleted', 'created'
        """
        with transaction.atomic():
            try:
                reaction_obj = self.select_for_update().get(  # lock update row
                    user=user,
                    comment_id=comment_id
                )
                old_reaction = reaction_obj.reaction

                if reaction_obj.reaction == reaction:  # unlike or undislike
                    reaction_obj.delete()
                    self._update_comment_reaction_counters(comment_id, old_reaction=old_reaction)
                    reaction_obj = None
                    action = 'deleted'

                else:
                    reaction_obj.reaction = reaction  # change reaction
                    reaction_obj.save(update_fields=['reaction'])
                    self._update_comment_reaction_counters(comment_id, old_reaction=old_reaction, new_reaction=reaction)
                    action = 'updated'

            except self.model.DoesNotExist:
                reaction_obj = self.create(
                    user=user,
                    comment_id=comment_id,
                    reaction=reaction
                )
                self._update_comment_reaction_counters(comment_id, new_reaction=reaction)
                action = 'created'

            return reaction_obj, action

    def _update_comment_reaction_counters(self, comment_id, old_reaction=None, new_reaction=None):
        """
        update likes_count, dis_likes_count, when need to update
        if reaction is deleted, new_reaction must be None!
        if reaction created, old_reaction must be None!
        and if reaction changed, you must set both old_reaction & new_reaction
        """
        updates = {}

        if old_reaction == self.model.LIKE:
            updates['likes_count'] = F('likes_count') - 1
        elif old_reaction == self.model.DISLIKE:
            updates['dis_likes_count'] = F('dis_likes_count') - 1

        if new_reaction == self.model.LIKE:
            updates['likes_count'] = F('likes_count') + 1
        elif new_reaction == self.model.DISLIKE:
            updates['dis_likes_count'] = F('dis_likes_count') + 1

        if updates:
            Comment.objects.filter(pk=comment_id).update(**updates)

    def sync_comment_reaction_counters(self, comment_id):
        """update likes & dis_likes count fields from db and real count of reactions"""

        reactions = self.filter(comment_id=comment_id).aggregate(
            likes=Count(When(reaction='lk', then=1)),
            dis_likes=Count(When(reaction='dlk', then=1))
        )
        Comment.objects.filter(pk=comment_id).update(likes_count=reactions.likes, dis_likes_count=reactions.dis_likes)


class CommentReAction(models.Model):
    LIKE = 'lk'
    DISLIKE = 'dlk'

    COMMENT_REACTIONS = (
        (LIKE, 'like'),
        (DISLIKE, 'dislike'),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='comment_reactions',
        verbose_name=_('user')
    )
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='reactions', verbose_name=_('comment'))
    reaction = models.CharField(max_length=10, choices=COMMENT_REACTIONS, verbose_name=_('reaction'))

    objects = CommentReactionManager()

    class Meta:
        unique_together = ('user', 'comment')

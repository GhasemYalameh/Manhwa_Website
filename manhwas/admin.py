from django.contrib import admin
from django.db.models import Count, OuterRef, Subquery
from django.utils.html import format_html, urlencode
from django.urls import reverse

from .models import Manhwa, Episode, Studio, Genre, Rate, View, Comment, CommentReAction, CommentReply


class CommentInline(admin.TabularInline):
    model = Comment
    fields = ['author', 'text']
    extra = 0


class EpisodeInline(admin.TabularInline):
    model = Episode
    fields = ['number', 'file']
    extra = 0


class ManhwaAdmin(admin.ModelAdmin):
    list_display = ('en_title', 'season', 'views_count', 'get_genres', 'episodes_count', 'comments_count')
    autocomplete_fields = ['genres']
    list_filter = ['genres', 'day_of_week', 'studio']
    search_fields = ['en_title']
    inlines = [EpisodeInline, CommentInline]

    def get_queryset(self, request):
        return super(ManhwaAdmin, self)\
            .get_queryset(request)\
            .prefetch_related('genres')\
            .select_related('studio')\
            .annotate(
                episodes_count=Subquery(
                    Episode.objects
                    .filter(manhwa=OuterRef('pk'))
                    .values('manhwa')
                    .annotate(count=Count('id'))
                    .values('count')
                ),
                comments_count=Subquery(
                    Comment.objects
                    .filter(manhwa=OuterRef('pk'))
                    .values('manhwa')
                    .annotate(count=Count('id'))
                    .values('count')
                )
            )

    def get_genres(self, obj):
        return ', '.join([genre.title for genre in obj.genres.all()])
    get_genres.short_description = 'Genre'

    @admin.display(description='Episodes', ordering='episodes_count')
    def episodes_count(self, manhwa):
        url = reverse('admin:manhwas_episode_changelist') + "?" + urlencode({'manhwa__id': manhwa.id})
        return format_html('<a href="{}">{}</a>', url, manhwa.episodes_count or 0)

    @admin.display(description='Comments', ordering='comments_count')
    def comments_count(self, manhwa):
        url = reverse('admin:manhwas_comment_changelist') + '?' + urlencode({'manhwa__id': manhwa.id})

        return format_html('<a href="{}">{}</a>', url, manhwa.comments_count or 0)


class ViewAdmin(admin.ModelAdmin):
    list_display = ('user', 'manhwa', 'datetime_viewed')


class RateAdmin(admin.ModelAdmin):
    list_display = ('user', 'manhwa', 'rating')


class GenreAdmin(admin.ModelAdmin):
    list_display = ('title',)
    search_fields = ['title']


class StudioAdmin(admin.ModelAdmin):
    list_display = ('title',)


class EpisodeAdmin(admin.ModelAdmin):
    list_display = ('number', 'downloads_count', 'manhwa')


class CommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'manhwa', 'datetime_modified',)


class CommentReplyAdmin(admin.ModelAdmin):
    pass


class CommentReActionAdmin(admin.ModelAdmin):
    list_display = ('user', 'comment', 'reaction')


admin.site.register(Manhwa, ManhwaAdmin)
admin.site.register(Genre, GenreAdmin)
admin.site.register(Studio, StudioAdmin)
admin.site.register(Episode, EpisodeAdmin)
admin.site.register(Rate, RateAdmin)
admin.site.register(View, ViewAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(CommentReAction, CommentReActionAdmin)
admin.site.register(CommentReply, CommentReplyAdmin)


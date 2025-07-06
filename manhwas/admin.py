from django.contrib import admin
from django.db.models import Count
from django.utils.html import format_html, urlencode
from django.urls import reverse

from .models import Manhwa, Episode, Studio, Genre, Rate, View, Comment, CommentReAction


class CommentInline(admin.TabularInline):
    model = Comment
    fields = ['author', 'text']
    extra = 0


class EpisodeInline(admin.TabularInline):
    model = Episode
    fields = ['number', 'file']
    extra = 0


class ManhwaAdmin(admin.ModelAdmin):
    list_display = ('en_title', 'season', 'views_count', 'get_genres', 'comments_count')
    autocomplete_fields = ['genres']
    list_filter = ['genres', 'day_of_week', 'studio']
    search_fields = ['en_title']
    inlines = [EpisodeInline, CommentInline]

    def get_queryset(self, request):
        return super(ManhwaAdmin, self)\
            .get_queryset(request)\
            .prefetch_related('genres', 'comments')\
            .select_related('studio')\
            .annotate(comments_count=Count('comments'))

    def get_genres(self, obj):
        return ', '.join([genre.title for genre in obj.genres.all()])
    get_genres.short_description = 'Genre'

    @admin.display(description='Comments')
    def comments_count(self, manhwa):
        url = reverse('admin:manhwas_comment_changelist') + '?' + urlencode({'manhwa_id': manhwa.id})

        return format_html('<a href="{}">{}</a>', url, manhwa.comments_count)


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


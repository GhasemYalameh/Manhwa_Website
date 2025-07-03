from django.contrib import admin
from django import forms

from .models import Manhwa, Episode, Studio, Genre, Rate


class ManhwaAdmin(admin.ModelAdmin):
    list_display = ('en_title', 'season', 'views', 'get_genres')
    # filter_horizontal = ('genres',)
    autocomplete_fields = ['genres']
    list_filter = ['genres']
    search_fields = ['en_title']

    def get_genres(self, obj):
        return ', '.join([genre.title for genre in obj.genres.all()])
    get_genres.short_description = 'Genre'


class RateAdmin(admin.ModelAdmin):
    list_display = ('user', 'manhwa', 'rating')


class GenreAdmin(admin.ModelAdmin):
    list_display = ('title',)
    search_fields = ['title']


class StudioAdmin(admin.ModelAdmin):
    list_display = ('title',)


class EpisodeAdmin(admin.ModelAdmin):
    list_display = ('number', 'downloads_count', 'manhwa')


admin.site.register(Manhwa, ManhwaAdmin)
admin.site.register(Genre, GenreAdmin)
admin.site.register(Studio, StudioAdmin)
admin.site.register(Episode, EpisodeAdmin)
admin.site.register(Rate, RateAdmin)


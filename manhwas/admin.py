from django.contrib import admin

from .models import Manhwa, ManhwaGenre, Episode, Studio, Genre


class ManhwaAdmin(admin.ModelAdmin):
    list_display = ('en_title', 'season', 'views')


class GenreAdmin(admin.ModelAdmin):
    list_display = ('title',)


class StudioAdmin(admin.ModelAdmin):
    list_display = ('title',)


class ManhwaGenreAdmin(admin.ModelAdmin):
    list_display = ('genre', 'manhwa')


class EpisodeAdmin(admin.ModelAdmin):
    list_display = ('number', 'downloads_count', 'manhwa')


admin.site.register(Manhwa, ManhwaAdmin)
admin.site.register(Genre, GenreAdmin)
admin.site.register(ManhwaGenre, ManhwaGenreAdmin)
admin.site.register(Studio, StudioAdmin)
admin.site.register(Episode, EpisodeAdmin)


from django.contrib import admin

from .models import Manhwa, Episode, Studio, Genre, Rate


class ManhwaAdmin(admin.ModelAdmin):
    list_display = ('en_title', 'season', 'views')
    filter_horizontal = ('genres',)


class RateAdmin(admin.ModelAdmin):
    list_display = ('user', 'manhwa', 'rating')


class GenreAdmin(admin.ModelAdmin):
    list_display = ('title',)


class StudioAdmin(admin.ModelAdmin):
    list_display = ('title',)


class EpisodeAdmin(admin.ModelAdmin):
    list_display = ('number', 'downloads_count', 'manhwa')


admin.site.register(Manhwa, ManhwaAdmin)
admin.site.register(Genre, GenreAdmin)
admin.site.register(Studio, StudioAdmin)
admin.site.register(Episode, EpisodeAdmin)
admin.site.register(Rate, RateAdmin)


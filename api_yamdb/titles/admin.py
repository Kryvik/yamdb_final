from django.contrib import admin
from titles.models import Category, Genre, Title


@admin.register(Title)
class TitlesAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'name',
        'category',
        'description',
        'year'
    )
    search_fields = ('name',)
    list_filter = ('year',)
    empty_value_display = '-пусто-'


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'name',
        'slug'
    )
    search_fields = ('name',)


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'name',
        'slug'
    )
    search_fields = ('name',)

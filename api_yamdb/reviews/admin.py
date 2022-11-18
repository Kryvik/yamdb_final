from django.contrib import admin
from reviews.models import Comment, Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'text',
        'score',
        'title',
        'author',
        'pub_date'
    )
    search_fields = ('text',)
    list_filter = ('pub_date',)
    empty_value_display = '-пусто-'


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'text',
        'review',
        'author',
        'pub_date'
    )
    search_fields = ('text',)
    list_filter = ('pub_date',)
    empty_value_display = '-пусто-'

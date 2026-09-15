from django.contrib import admin
from .models import ReviewPost, Article, CustomerReview

@admin.register(ReviewPost)
class ReviewPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'property', 'created_at', 'updated_at')
    list_filter = ('created_at',)
    search_fields = ('title', 'content')
    prepopulated_fields = {'slug': ('title',)}


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'is_published', 'views_count', 'created_at')
    list_filter = ('category', 'is_published', 'created_at')
    search_fields = ('title', 'excerpt', 'content')
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ('is_published',)


@admin.register(CustomerReview)
class CustomerReviewAdmin(admin.ModelAdmin):
    list_display = ('reviewer_name', 'rating', 'property', 'is_approved', 'created_at')
    list_filter = ('rating', 'is_approved', 'created_at')
    search_fields = ('reviewer_name', 'comment')
    list_editable = ('is_approved',)

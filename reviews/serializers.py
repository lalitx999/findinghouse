from rest_framework import serializers
from .models import ReviewPost, Article, CustomerReview
from properties.serializers import PropertySerializer

class ReviewPostSerializer(serializers.ModelSerializer):
    property = PropertySerializer(read_only=True)

    class Meta:
        model = ReviewPost
        fields = ['id', 'title', 'slug', 'cover_image', 'content', 'property', 'created_at', 'updated_at']


class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = ['id', 'title', 'slug', 'category', 'cover_image', 'excerpt', 'content', 'views_count', 'is_published', 'created_at', 'updated_at']


class CustomerReviewSerializer(serializers.ModelSerializer):
    property_title = serializers.ReadOnlyField(source='property.title', default=None)

    class Meta:
        model = CustomerReview
        fields = ['id', 'reviewer_name', 'reviewer_role', 'rating', 'comment', 'property', 'property_title', 'avatar', 'is_approved', 'created_at']
        read_only_fields = ['is_approved', 'created_at']

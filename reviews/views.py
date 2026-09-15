from rest_framework import viewsets, permissions
from rest_framework.response import Response
from .models import ReviewPost, Article, CustomerReview
from .serializers import ReviewPostSerializer, ArticleSerializer, CustomerReviewSerializer

class ReviewPostViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ReviewPost.objects.all()
    serializer_class = ReviewPostSerializer
    lookup_field = 'slug'


class ArticleViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Article.objects.filter(is_published=True)
    serializer_class = ArticleSerializer
    lookup_field = 'slug'

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.views_count += 1
        instance.save(update_fields=['views_count'])
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class CustomerReviewViewSet(viewsets.ModelViewSet):
    serializer_class = CustomerReviewSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        # Public gets only approved reviews
        if self.request.user and self.request.user.is_staff:
            return CustomerReview.objects.all()
        return CustomerReview.objects.filter(is_approved=True)

    def perform_create(self, serializer):
        # New reviews submitted by guests/users wait for admin approval
        serializer.save(is_approved=False)

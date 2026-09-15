"""
URL configuration for config project.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from properties.views import CategoryViewSet, LocationViewSet, PropertyViewSet, BookmarkViewSet, ConsignmentViewSet
from reviews.views import ReviewPostViewSet, ArticleViewSet, CustomerReviewViewSet
from inquiries.views import InquiryCreateView
from config.views import RegisterView, UserProfileView

# Configure Default REST API Router
router = DefaultRouter()
router.register(r'properties', PropertyViewSet, basename='property')
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'locations', LocationViewSet, basename='location')
router.register(r'reviews', ReviewPostViewSet, basename='review')
router.register(r'articles', ArticleViewSet, basename='article')
router.register(r'customer-reviews', CustomerReviewViewSet, basename='customer-review')
router.register(r'bookmarks', BookmarkViewSet, basename='bookmark')
router.register(r'consignments', ConsignmentViewSet, basename='consignment')

from audit.views_health import SystemHealthView

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # System Health Check
    path('api/health/', SystemHealthView.as_view(), name='system_health'),

    # Auth endpoints
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/register/', RegisterView.as_view(), name='register'),
    path('api/profile/', UserProfileView.as_view(), name='profile'),
    
    # Inquiries submission
    path('api/inquiries/', InquiryCreateView.as_view(), name='inquiry_create'),
    
    # CRM app endpoints
    path('api/crm/', include('crm.urls')),

    # Audit & Security app endpoints
    path('api/audit/', include('audit.urls')),
    path('api/security/', include('audit.urls')),

    # Chat app endpoints
    path('api/chat/', include('chat.urls')),

    # Decoupled apps endpoints routed automatically
    path('api/', include(router.urls)),
]

# Serve static and media files
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AuditLogViewSet, UserSessionViewSet, RequestOTPView, VerifyOTPView, FCMDeviceTokenView

router = DefaultRouter()
router.register(r'logs', AuditLogViewSet, basename='auditlog')
router.register(r'sessions', UserSessionViewSet, basename='usersession')

from .views_otp import SendListingOTPView, VerifyListingOTPView

urlpatterns = [
    path('', include(router.urls)),
    path('2fa/request-otp/', RequestOTPView.as_view(), name='request-otp'),
    path('2fa/verify-otp/', VerifyOTPView.as_view(), name='verify-otp'),
    path('send-otp/', SendListingOTPView.as_view(), name='send-listing-otp'),
    path('verify-otp/', VerifyListingOTPView.as_view(), name='verify-listing-otp'),
    path('fcm-token/', FCMDeviceTokenView.as_view(), name='fcm-token'),
]

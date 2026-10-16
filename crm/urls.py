from django.urls import path, include
from rest_framework.routers import DefaultRouter
from crm.views import LeadViewSet, DealViewSet, ViewingAppointmentViewSet, LeaseAgreementViewSet, AgentViewSet
from crm.views_analytics import AnalyticsDashboardView

router = DefaultRouter()
router.register('leads', LeadViewSet, basename='lead')
router.register('deals', DealViewSet, basename='deal')
router.register('appointments', ViewingAppointmentViewSet, basename='appointment')
router.register('leases', LeaseAgreementViewSet, basename='lease')
router.register('agents', AgentViewSet, basename='agent')

urlpatterns = [
    path('analytics/', AnalyticsDashboardView.as_view(), name='crm-analytics'),
    path('', include(router.urls)),
]


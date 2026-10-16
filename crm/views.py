from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from crm.models import Lead, LeadMatch, Deal, ViewingAppointment, LeaseAgreement
from crm.serializers import (
    LeadSerializer, LeadCreateSerializer, LeadMatchSerializer, DealSerializer,
    ViewingAppointmentSerializer, LeaseAgreementSerializer
)
from crm.services import run_lead_auto_matching
from config.permissions import ScopedQuerySetMixin

class LeadViewSet(ScopedQuerySetMixin, viewsets.ModelViewSet):
    agent_field_name = 'assigned_agent'
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if not self.request.user or not self.request.user.is_authenticated:
            return Lead.objects.none()
        qs = Lead.objects.all().prefetch_related('categories', 'locations', 'matches', 'matches__property')
        return self.filter_queryset_by_role(qs)

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return LeadCreateSerializer
        return LeadSerializer

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def match(self, request, pk=None):
        """
        Triggers Auto-Matching Engine for a specific Lead via REST API.
        """
        lead = self.get_object()
        match_count = run_lead_auto_matching(lead)

        updated_lead = self.get_object()
        return Response({
            'message': f'Auto-Matching complete. Found {match_count} matching properties.',
            'lead': LeadSerializer(updated_lead).data
        }, status=status.HTTP_200_OK)


class DealViewSet(ScopedQuerySetMixin, viewsets.ModelViewSet):
    agent_field_name = 'agent'
    permission_classes = [IsAuthenticated]
    serializer_class = DealSerializer

    def get_queryset(self):
        if not self.request.user or not self.request.user.is_authenticated:
            return Deal.objects.none()
        qs = Deal.objects.all().select_related('lead', 'property', 'agent')
        return self.filter_queryset_by_role(qs)


class ViewingAppointmentViewSet(ScopedQuerySetMixin, viewsets.ModelViewSet):
    agent_field_name = 'agent'
    permission_classes = [IsAuthenticated]
    serializer_class = ViewingAppointmentSerializer

    def get_queryset(self):
        if not self.request.user or not self.request.user.is_authenticated:
            return ViewingAppointment.objects.none()
        qs = ViewingAppointment.objects.all().select_related('lead', 'property', 'agent')
        return self.filter_queryset_by_role(qs)


class LeaseAgreementViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = LeaseAgreementSerializer

    def get_queryset(self):
        if not self.request.user or not self.request.user.is_authenticated:
            return LeaseAgreement.objects.none()
        qs = LeaseAgreement.objects.all().select_related('property', 'property__agent')
        user = self.request.user
        if user.is_superuser:
            return qs
        profile = getattr(user, 'profile', None)
        if profile and profile.role in ['SUPER_ADMIN', 'BRANCH_MANAGER']:
            return qs
        return qs.filter(property__agent=user)


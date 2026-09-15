from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from crm.models import Lead, LeadMatch, Deal, ViewingAppointment, LeaseAgreement
from crm.serializers import (
    LeadSerializer, LeadCreateSerializer, LeadMatchSerializer, DealSerializer,
    ViewingAppointmentSerializer, LeaseAgreementSerializer
)
from crm.services import run_lead_auto_matching
from config.permissions import ScopedQuerySetMixin

class LeadViewSet(ScopedQuerySetMixin, viewsets.ModelViewSet):
    agent_field_name = 'assigned_agent'

    def get_queryset(self):
        qs = Lead.objects.all().prefetch_related('categories', 'locations', 'matches', 'matches__property')
        if self.request.user and self.request.user.is_authenticated:
            return self.filter_queryset_by_role(qs)
        return qs

    def get_permissions(self):
        if self.action == 'create':
            return [AllowAny()]
        return [AllowAny()]  # Can be tightened to IsAuthenticated in production

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return LeadCreateSerializer
        return LeadSerializer

    @action(detail=True, methods=['post'], permission_classes=[AllowAny])
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
    permission_classes = [AllowAny]
    serializer_class = DealSerializer

    def get_queryset(self):
        qs = Deal.objects.all().select_related('lead', 'property', 'agent')
        if self.request.user and self.request.user.is_authenticated:
            return self.filter_queryset_by_role(qs)
        return qs


class ViewingAppointmentViewSet(ScopedQuerySetMixin, viewsets.ModelViewSet):
    agent_field_name = 'agent'
    permission_classes = [AllowAny]
    serializer_class = ViewingAppointmentSerializer

    def get_queryset(self):
        qs = ViewingAppointment.objects.all().select_related('lead', 'property', 'agent')
        if self.request.user and self.request.user.is_authenticated:
            return self.filter_queryset_by_role(qs)
        return qs


class LeaseAgreementViewSet(viewsets.ModelViewSet):
    queryset = LeaseAgreement.objects.all().select_related('property')
    permission_classes = [AllowAny]
    serializer_class = LeaseAgreementSerializer

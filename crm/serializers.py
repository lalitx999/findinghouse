from rest_framework import serializers
from crm.models import Lead, LeadMatch, Deal, ViewingAppointment, LeaseAgreement
from properties.serializers import PropertySerializer, CategorySerializer, LocationSerializer

class LeadMatchSerializer(serializers.ModelSerializer):
    property = PropertySerializer(read_only=True)

    class Meta:
        model = LeadMatch
        fields = ['id', 'property', 'match_score', 'match_reasons', 'status', 'created_at']


class LeadSerializer(serializers.ModelSerializer):
    categories = CategorySerializer(many=True, read_only=True)
    locations = LocationSerializer(many=True, read_only=True)
    matches = LeadMatchSerializer(many=True, read_only=True)

    class Meta:
        model = Lead
        fields = [
            'id', 'name', 'phone', 'email', 'line_id',
            'lead_type', 'status', 'categories', 'locations',
            'budget_min', 'budget_max', 'min_bedrooms', 'min_usable_size',
            'notes', 'matches', 'created_at', 'updated_at'
        ]


class LeadCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lead
        fields = '__all__'
        read_only_fields = ['status', 'created_at', 'updated_at']


class DealSerializer(serializers.ModelSerializer):
    lead = LeadSerializer(read_only=True)
    property = PropertySerializer(read_only=True)

    class Meta:
        model = Deal
        fields = '__all__'


class ViewingAppointmentSerializer(serializers.ModelSerializer):
    lead = LeadSerializer(read_only=True)
    property = PropertySerializer(read_only=True)

    class Meta:
        model = ViewingAppointment
        fields = '__all__'


class LeaseAgreementSerializer(serializers.ModelSerializer):
    property = PropertySerializer(read_only=True)
    days_until_expiration = serializers.ReadOnlyField()

    class Meta:
        model = LeaseAgreement
        fields = '__all__'

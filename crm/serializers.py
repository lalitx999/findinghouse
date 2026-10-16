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


from crm.models import UserProfile

class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)
    email = serializers.CharField(source='user.email', read_only=True)
    is_active = serializers.BooleanField(source='user.is_active', read_only=True)
    is_staff = serializers.BooleanField(source='user.is_staff', read_only=True)

    class Meta:
        model = UserProfile
        fields = [
            'id', 'user_id', 'username', 'first_name', 'last_name', 'email',
            'is_active', 'is_staff', 'role', 'branch', 'phone_number',
            'created_at', 'updated_at'
        ]


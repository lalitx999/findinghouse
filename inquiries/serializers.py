from rest_framework import serializers
from .models import Inquiry
from properties.models import Property

class InquirySerializer(serializers.ModelSerializer):
    property_id = serializers.PrimaryKeyRelatedField(
        queryset=Property.objects.all(),
        source='property',
        required=False,
        allow_null=True
    )

    class Meta:
        model = Inquiry
        fields = ['id', 'property_id', 'name', 'email', 'phone', 'message', 'created_at']
        read_only_fields = ['id', 'created_at']

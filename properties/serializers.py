from rest_framework import serializers
from .models import Category, Location, Property, PropertyImage, Bookmark, Consignment, ConsignmentImage, ConsignmentDeed
from django.contrib.auth import get_user_model

User = get_user_model()

class AgentSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email']


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug']


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ['id', 'name', 'slug']


class PropertyImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyImage
        fields = ['id', 'image', 'is_cover', 'order']


class PropertySerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    location = LocationSerializer(read_only=True)
    images = PropertyImageSerializer(many=True, read_only=True)
    agent = AgentSerializer(read_only=True)
    completeness_score = serializers.SerializerMethodField()
    price_per_sqm = serializers.ReadOnlyField()
    price_per_sqwah = serializers.ReadOnlyField()
    price_per_rai = serializers.ReadOnlyField()
    seo_search_phrases = serializers.SerializerMethodField()

    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), source='category', write_only=True, required=False
    )
    location_id = serializers.PrimaryKeyRelatedField(
        queryset=Location.objects.all(), source='location', write_only=True, required=False
    )
    agent_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='agent', write_only=True, required=False, allow_null=True
    )

    class Meta:
        model = Property
        fields = [
            'id', 'title', 'slug', 'property_code', 'description', 'price',
            'property_type', 'category', 'location', 'category_id', 'location_id',
            'bedrooms', 'bathrooms',
            'size_land', 'size_usable', 'features', 'status', 'agent', 'agent_id', 'images',
            'source', 'sale_condition',
            'google_maps_link', 'latitude', 'longitude', 'floors', 'parking_spaces', 'direction', 'furniture',
            'pet_friendly', 'common_fee', 'availability', 'minimum_lease',
            'deposit', 'advance_payment', 'move_in_date',
            'seller_name', 'seller_phone', 'seller_line_id', 'is_direct_seller',
            'landmarks', 'price_per_sqm', 'price_per_sqwah', 'price_per_rai',
            'seo_search_phrases', 'completeness_score', 'last_confirmed_at',
            'created_at', 'updated_at'
        ]

    def get_completeness_score(self, obj):
        return obj.calculate_completeness_score()

    def get_seo_search_phrases(self, obj):
        return obj.get_seo_search_phrases()


class BookmarkSerializer(serializers.ModelSerializer):
    property = PropertySerializer(read_only=True)

    class Meta:
        model = Bookmark
        fields = ['id', 'property', 'created_at']


class BookmarkCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bookmark
        fields = ['id', 'property']

    def validate(self, attrs):
        user = self.context['request'].user
        property_obj = attrs['property']
        if Bookmark.objects.filter(user=user, property=property_obj).exists():
            raise serializers.ValidationError("คุณเคยบันทึกรายการนี้ไว้แล้ว")
        return attrs


class ConsignmentImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConsignmentImage
        fields = ['id', 'image', 'uploaded_at']


class ConsignmentDeedSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConsignmentDeed
        fields = ['id', 'deed_image', 'uploaded_at']


class ConsignmentSerializer(serializers.ModelSerializer):
    images = ConsignmentImageSerializer(many=True, read_only=True)
    deeds = ConsignmentDeedSerializer(many=True, read_only=True)

    class Meta:
        model = Consignment
        fields = '__all__'


class ConsignmentCreateSerializer(serializers.ModelSerializer):
    specs = serializers.JSONField(required=False, default=dict)

    class Meta:
        model = Consignment
        fields = '__all__'
        read_only_fields = ['status', 'created_at']

    def to_internal_value(self, data):
        if 'specs' in data and isinstance(data['specs'], str):
            import json
            try:
                mutable_data = data.copy()
                mutable_data['specs'] = json.loads(data['specs'])
                data = mutable_data
            except Exception:
                pass
        return super().to_internal_value(data)

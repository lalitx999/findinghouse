from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()
    is_agent = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'is_staff', 'is_superuser', 'role', 'is_agent']
        read_only_fields = ['id', 'username']

    def get_role(self, obj):
        if hasattr(obj, 'profile') and obj.profile:
            return obj.profile.role
        if obj.is_superuser:
            return 'SUPER_ADMIN'
        if obj.is_staff:
            return 'SENIOR_AGENT'
        return 'CUSTOMER'

    def get_is_agent(self, obj):
        if obj.is_staff or obj.is_superuser:
            return True
        if hasattr(obj, 'profile') and obj.profile:
            return obj.profile.role in ['SUPER_ADMIN', 'BRANCH_MANAGER', 'SENIOR_AGENT', 'JUNIOR_AGENT']
        return False


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password', 'password_confirm']
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
            'email': {'required': True},
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password": "Passwords do not match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            password=validated_data['password']
        )
        return user

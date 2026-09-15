from rest_framework import serializers
from .models import AuditLog, UserSession, UserTwoFactorOTP

class AuditLogSerializer(serializers.ModelSerializer):
    user_username = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = AuditLog
        fields = [
            'id', 'user', 'user_username', 'action', 'model_name',
            'object_id', 'object_repr', 'details', 'ip_address',
            'user_agent', 'timestamp'
        ]


class UserSessionSerializer(serializers.ModelSerializer):
    user_username = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = UserSession
        fields = [
            'id', 'user_username', 'session_key', 'ip_address',
            'user_agent', 'device_name', 'created_at', 'last_activity',
            'is_active'
        ]


class RequestOTPSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)


class VerifyOTPSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    otp_code = serializers.CharField(max_length=6, min_length=6, required=True)


from .models import FCMDeviceToken

class FCMDeviceTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = FCMDeviceToken
        fields = ['id', 'token', 'device_type', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


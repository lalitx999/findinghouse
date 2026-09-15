from rest_framework import viewsets, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import AuditLog, UserSession, UserTwoFactorOTP, LoginAttempt
from .serializers import (
    AuditLogSerializer, UserSessionSerializer,
    RequestOTPSerializer, VerifyOTPSerializer
)

User = get_user_model()

class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for viewing Audit Logs (Admins only)
    """
    queryset = AuditLog.objects.all()
    serializer_class = AuditLogSerializer
    permission_classes = [permissions.IsAdminUser]
    filterset_fields = ['action', 'model_name', 'user']
    search_fields = ['object_id', 'object_repr', 'ip_address', 'details']


class UserSessionViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing Active User Sessions
    """
    serializer_class = UserSessionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UserSession.objects.filter(user=self.request.user, is_active=True)

    @action(detail=True, methods=['post'], url_path='revoke')
    def revoke_session(self, request, pk=None):
        session = self.get_object()
        session.is_active = False
        session.save()
        return Response({'status': 'Session revoked successfully'}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], url_path='revoke-others')
    def revoke_other_sessions(self, request):
        current_session_key = request.headers.get('X-Session-Key', '')
        sessions = UserSession.objects.filter(user=request.user, is_active=True)
        if current_session_key:
            sessions = sessions.exclude(session_key=current_session_key)
        count = sessions.update(is_active=False)
        return Response({'status': f'Revoked {count} other sessions successfully'}, status=status.HTTP_200_OK)


class RequestOTPView(APIView):
    """
    Generate a 6-digit OTP code for 2FA verification (5 min expiration)
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RequestOTPSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        username = serializer.validated_data['username']
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response({'error': 'ไม่พบผู้ใช้งานตามชื่อที่ระบุ'}, status=status.HTTP_404_NOT_FOUND)

        # Check account lockout status
        attempt, _ = LoginAttempt.objects.get_or_create(username=username)
        if attempt.check_is_locked():
            remaining_mins = int((attempt.locked_until - timezone.now()).total_seconds() // 60) + 1
            return Response({
                'error': f'บัญชีของคุณถูกล็อกเนื่องจากใส่รหัสผิดเกินกำหนด กรุณาลองใหม่ในอีก {remaining_mins} นาที'
            }, status=status.HTTP_403_FORBIDDEN)

        # Generate 6-digit OTP
        otp_obj = UserTwoFactorOTP.generate_otp(user=user, validity_minutes=5)

        return Response({
            'message': 'สร้างรหัส OTP 6 หลักสำเร็จแล้ว',
            'otp_code': otp_obj.otp_code,  # Included for preview/testing
            'expires_at': otp_obj.expires_at.strftime('%Y-%m-%d %H:%M:%S'),
            'validity_minutes': 5
        }, status=status.HTTP_200_OK)


class VerifyOTPView(APIView):
    """
    Verify 6-digit OTP code for 2FA
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        username = serializer.validated_data['username']
        otp_code = serializer.validated_data['otp_code']

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response({'error': 'ไม่พบผู้ใช้งาน'}, status=status.HTTP_404_NOT_FOUND)

        # Fetch latest unused OTP for user
        otp_obj = UserTwoFactorOTP.objects.filter(user=user, is_used=False).first()
        if not otp_obj:
            return Response({'error': 'ไม่พบรหัส OTP ที่รอดำเนินการ กรุณากดขอ OTP ใหม่'}, status=status.HTTP_400_BAD_REQUEST)

        is_valid, msg = otp_obj.is_valid()
        if not is_valid:
            return Response({'error': msg}, status=status.HTTP_400_BAD_REQUEST)

        # Check if code matches
        if otp_obj.otp_code != otp_code:
            otp_obj.attempts += 1
            otp_obj.save()
            return Response({'error': f'รหัส OTP ไม่ถูกต้อง (เหลือโอกาสลองอีก {3 - otp_obj.attempts} ครั้ง)'}, status=status.HTTP_400_BAD_REQUEST)

        # Mark OTP as used
        otp_obj.is_used = True
        otp_obj.save()

        # Reset failed login attempt count on successful 2FA
        LoginAttempt.objects.filter(username=username).update(failed_count=0, is_locked=False, locked_until=None)

        return Response({
            'message': 'ยืนยันตัวตน 2FA ด้วยรหัส OTP สำเร็จแล้ว',
            'verified': True
        }, status=status.HTTP_200_OK)


from .models import FCMDeviceToken
from .serializers import FCMDeviceTokenSerializer

class FCMDeviceTokenView(APIView):
    """
    API endpoint for registering/updating FCM Device Token for Push Notifications
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        token_str = request.data.get('token')
        device_type = request.data.get('device_type', 'WEB')

        if not token_str:
            return Response({'error': 'กรุณาระบุ FCM Device Token'}, status=status.HTTP_400_BAD_REQUEST)

        fcm_obj, created = FCMDeviceToken.objects.update_or_create(
            token=token_str,
            defaults={
                'user': request.user,
                'device_type': device_type,
            }
        )

        serializer = FCMDeviceTokenSerializer(fcm_obj)
        return Response({
            'message': 'บันทึก FCM Device Token สำเร็จแล้ว',
            'created': created,
            'data': serializer.data
        }, status=status.HTTP_200_OK)


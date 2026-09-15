from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .models import UserListingOTP
from .utils_sms import send_sms_otp

class SendListingOTPView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        phone = request.data.get('phone')
        if not phone or len(phone.strip()) < 9:
            return Response({'error': 'กรุณาระบุเบอร์โทรศัพท์ที่ถูกต้อง (อย่างน้อย 9 หลัก)'}, status=status.HTTP_400_BAD_REQUEST)

        phone_clean = phone.strip()
        otp_obj = UserListingOTP.generate_otp(phone=phone_clean)

        # Trigger SMSMKT SMS Dispatch
        sms_success, sms_msg = send_sms_otp(phone=phone_clean, otp_code=otp_obj.otp_code)

        if not sms_success and 'Sandbox' not in sms_msg:
            return Response({'error': f'ไม่สามารถส่ง SMS OTP ได้: {sms_msg}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({
            'message': f'ส่งรหัส OTP ไปยังเบอร์ {phone_clean} เรียบร้อยแล้ว (มีอายุ 5 นาที)',
            'phone': phone_clean,
            'dev_otp': otp_obj.otp_code # Included for sandbox/testing convenience
        }, status=status.HTTP_200_OK)


class VerifyListingOTPView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        phone = request.data.get('phone')
        otp_code = request.data.get('otp_code')

        if not phone or not otp_code:
            return Response({'error': 'กรุณาระบุเบอร์โทรศัพท์และรหัส OTP 6 หลัก'}, status=status.HTTP_400_BAD_REQUEST)

        otp_qs = UserListingOTP.objects.filter(phone=phone.strip(), otp_code=otp_code.strip()).order_by('-created_at')
        if not otp_qs.exists():
            return Response({'error': 'รหัส OTP ไม่ถูกต้อง'}, status=status.HTTP_400_BAD_REQUEST)

        otp_obj = otp_qs.first()
        valid, msg = otp_obj.is_valid()
        if not valid:
            return Response({'error': msg}, status=status.HTTP_400_BAD_REQUEST)

        otp_obj.is_verified = True
        otp_obj.save()

        return Response({
            'verified': True,
            'message': 'ยืนยันเบอร์โทรศัพท์ด้วย SMS OTP เรียบร้อยแล้ว'
        }, status=status.HTTP_200_OK)

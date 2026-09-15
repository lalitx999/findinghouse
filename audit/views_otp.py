from datetime import timedelta
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .models import UserListingOTP
from .utils_sms import send_sms_otp, verify_sms_otp_gateway

class SendListingOTPView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        phone = request.data.get('phone')
        if not phone or len(phone.strip()) < 9:
            return Response({'error': 'กรุณาระบุเบอร์โทรศัพท์ที่ถูกต้อง'}, status=status.HTTP_400_BAD_REQUEST)

        phone_clean = phone.strip()

        # ส่งผ่าน SMSMKT Gateway จริง
        sms_success, sms_msg, token = send_sms_otp(phone=phone_clean)

        if not sms_success or not token:
            return Response({'error': f'ส่ง SMS ไม่สำเร็จ: {sms_msg}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # บันทึก token พร้อมคำนวณ expires_at 5 นาที
        UserListingOTP.objects.create(
            phone=phone_clean,
            otp_code=token,
            expires_at=timezone.now() + timedelta(minutes=5),
            is_verified=False
        )

        return Response({
            'message': f'ส่งรหัส OTP ไปยังเบอร์ {phone_clean} เรียบร้อยแล้ว (มีอายุ 5 นาที)',
            'phone': phone_clean
        }, status=status.HTTP_200_OK)


class VerifyListingOTPView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        phone = request.data.get('phone')
        otp_code = request.data.get('otp_code')

        if not phone or not otp_code:
            return Response({'error': 'กรุณาระบุเบอร์โทรศัพท์และรหัส OTP'}, status=status.HTTP_400_BAD_REQUEST)

        phone_clean = phone.strip()
        otp_obj = UserListingOTP.objects.filter(phone=phone_clean).order_by('-created_at').first()
        if not otp_obj or not otp_obj.otp_code:
            return Response({'error': 'ไม่พบประวัติการขอ OTP หรือรหัสหมดอายุ กรุณากดขอใหม่'}, status=status.HTTP_400_BAD_REQUEST)

        token = otp_obj.otp_code

        # ตรวจสอบกับ Gateway ของ SMSMKT ด้วย Token ที่ได้มา
        is_ok, verify_msg = verify_sms_otp_gateway(token=token, otp_code=otp_code.strip())

        if is_ok:
            otp_obj.is_verified = True
            otp_obj.save()
            return Response({
                'verified': True,
                'message': 'ยืนยันเบอร์โทรศัพท์ด้วย SMS OTP เรียบร้อยแล้ว'
            }, status=status.HTTP_200_OK)
        else:
            return Response({'error': verify_msg}, status=status.HTTP_400_BAD_REQUEST)

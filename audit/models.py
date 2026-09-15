from django.db import models
from django.conf import settings

class AuditLog(models.Model):
    ACTION_CHOICES = [
        ('CREATE', 'สร้างข้อมูล'),
        ('UPDATE', 'แก้ไขข้อมูล'),
        ('DELETE', 'ลบข้อมูล'),
        ('VIEW', 'เข้าดูข้อมูล'),
        ('LOGIN', 'เข้าสู่ระบบ'),
        ('LOGOUT', 'ออกจากระบบ'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs',
        verbose_name='ผู้ใช้งาน'
    )
    action = models.CharField(max_length=20, choices=ACTION_CHOICES, verbose_name='ประเภทกิจกรรม')
    model_name = models.CharField(max_length=100, verbose_name='โมเดล/ระบบ')
    object_id = models.CharField(max_length=100, blank=True, null=True, verbose_name='รหัสวัตถุ (ID/Code)')
    object_repr = models.CharField(max_length=255, blank=True, null=True, verbose_name='ชื่อวัตถุ/คำอธิบาย')
    details = models.JSONField(default=dict, blank=True, verbose_name='รายละเอียดการเปลี่ยนแปลง')
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name='IP Address')
    user_agent = models.TextField(blank=True, null=True, verbose_name='User Agent / Browser')
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name='วันเวลาที่ทำรายการ')

    class Meta:
        verbose_name = 'ประวัติกิจกรรม (Audit Log)'
        verbose_name_plural = 'บันทึกประวัติกิจกรรมระบบ (Audit Logs)'
        ordering = ['-timestamp']

    def __str__(self):
        user_str = self.user.username if self.user else 'System/Anonymous'
        return f"[{self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}] {user_str} - {self.get_action_display()} {self.model_name} ({self.object_id})"


import secrets
from django.utils import timezone
from datetime import timedelta

class UserSession(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='active_sessions',
        verbose_name='ผู้ใช้งาน'
    )
    session_key = models.CharField(max_length=100, unique=True, verbose_name='Session Key')
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name='IP Address')
    user_agent = models.TextField(blank=True, null=True, verbose_name='User Agent')
    device_name = models.CharField(max_length=100, default='Unknown Device', verbose_name='ชื่ออุปกรณ์')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='เวลาที่เริ่มเข้าสู่ระบบ')
    last_activity = models.DateTimeField(auto_now=True, verbose_name='เวลาใช้งานล่าสุด')
    is_active = models.BooleanField(default=True, verbose_name='สถานะ Active')

    class Meta:
        verbose_name = 'Session อุปกรณ์การใช้งาน (Active Session)'
        verbose_name_plural = 'รายการ Session การใช้งาน (Active Sessions)'
        ordering = ['-last_activity']

    def __str__(self):
        return f"{self.user.username} - {self.device_name} ({self.ip_address})"


class LoginAttempt(models.Model):
    username = models.CharField(max_length=150, db_index=True, verbose_name='ชื่อผู้ใช้')
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name='IP Address')
    failed_count = models.IntegerField(default=0, verbose_name='จำนวนครั้งที่ใส่รหัสผิด')
    is_locked = models.BooleanField(default=False, verbose_name='สถานะถูกล็อกบัญชี')
    locked_until = models.DateTimeField(null=True, blank=True, verbose_name='ถูกล็อกถึงเวลา')
    last_attempt = models.DateTimeField(auto_now=True, verbose_name='พยายามเข้าสู่ระบบล่าสุด')

    class Meta:
        verbose_name = 'ประวัติความพยายามเข้าสู่ระบบ (Login Attempt)'
        verbose_name_plural = 'ประวัติความพยายามเข้าสู่ระบบ (Login Attempts)'
        ordering = ['-last_attempt']

    def __str__(self):
        status = f"LOCKED until {self.locked_until}" if self.is_locked else f"Failed {self.failed_count} times"
        return f"{self.username} ({self.ip_address}) - {status}"

    def check_is_locked(self):
        if self.is_locked and self.locked_until:
            if timezone.now() > self.locked_until:
                self.is_locked = False
                self.failed_count = 0
                self.locked_until = None
                self.save()
                return False
            return True
        return self.is_locked


class UserTwoFactorOTP(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='otp_codes',
        verbose_name='ผู้ใช้งาน'
    )
    otp_code = models.CharField(max_length=6, verbose_name='รหัส OTP 6 หลัก')
    is_used = models.BooleanField(default=False, verbose_name='ใช้งานแล้ว')
    attempts = models.IntegerField(default=0, verbose_name='จำนวนครั้งที่ลองกรอก')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='เวลาที่สร้าง')
    expires_at = models.DateTimeField(verbose_name='เวลาหมดอายุ')

    class Meta:
        verbose_name = 'รหัส OTP 2FA (Two-Factor OTP)'
        verbose_name_plural = 'รายการรหัส OTP 2FA (Two-Factor OTPs)'
        ordering = ['-created_at']

    def is_valid(self):
        if self.is_used:
            return False, 'รหัส OTP นี้ถูกใช้งานไปแล้ว'
        if self.attempts >= 3:
            return False, 'กรอกรหัส OTP ผิดเกินจำนวนครั้งที่กำหนด (สะสม 3 ครั้ง)'
        if timezone.now() > self.expires_at:
            return False, 'รหัส OTP หมดอายุแล้ว (เกิน 5 นาที)'
        return True, 'รหัส OTP ถูกต้อง'

    @classmethod
    def generate_otp(cls, user, validity_minutes=5):
        code = str(secrets.randbelow(900000) + 100000)
        expires_at = timezone.now() + timedelta(minutes=validity_minutes)
        return cls.objects.create(
            user=user,
            otp_code=code,
            expires_at=expires_at
        )

    def __str__(self):
        return f"{self.user.username} - OTP: {self.otp_code} (Valid until: {self.expires_at.strftime('%H:%M:%S')})"


class Notification(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name='ผู้ใช้งาน'
    )
    title = models.CharField(max_length=200, verbose_name='หัวข้อการแจ้งเตือน')
    message = models.TextField(verbose_name='เนื้อหาแจ้งเตือน')
    link = models.CharField(max_length=500, blank=True, null=True, verbose_name='ลิงก์ที่เกี่ยวข้อง')
    is_read = models.BooleanField(default=False, verbose_name='อ่านแล้ว')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='เวลาที่แจ้งเตือน')

    class Meta:
        verbose_name = 'ระบบแจ้งเตือนภายในเว็บ (In-App Notification)'
        verbose_name_plural = 'รายการแจ้งเตือนภายในเว็บ (In-App Notifications)'
        ordering = ['-created_at']

    def __str__(self):
        status = "READ" if self.is_read else "UNREAD"
        return f"[{status}] {self.user.username} - {self.title}"


class WebhookConfig(models.Model):
    EVENT_TYPES = [
        ('ALL', 'ทุกเหตุการณ์ (All Events)'),
        ('LEAD_CREATED', 'เมื่อมีลีดลูกค้าใหม่ (New Lead Created)'),
        ('DEAL_CLOSED', 'เมื่อปิดการขาย/เช่าสำเร็จ (Deal Closed Won)'),
        ('SECURITY_ALERT', 'เมื่อมีคำเตือนความปลอดภัย (Security Alert)'),
    ]

    name = models.CharField(max_length=150, verbose_name='ชื่อระบบปลายทาง')
    url = models.URLField(max_length=500, verbose_name='Webhook Target URL')
    secret_token = models.CharField(max_length=255, blank=True, null=True, verbose_name='Secret Token (HMAC SHA256 Signature)')
    event_type = models.CharField(max_length=30, choices=EVENT_TYPES, default='ALL', verbose_name='ประเภทเหตุการณ์ที่ดักจับ')
    is_active = models.BooleanField(default=True, verbose_name='สถานะเปิดใช้งาน')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='สร้างเมื่อ')

    class Meta:
        verbose_name = 'การตั้งค่า Webhook (Webhook Config)'
        verbose_name_plural = 'การตั้งค่า Webhook (Webhook Configs)'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.get_event_type_display()}) - {self.url}"


class FCMDeviceToken(models.Model):
    DEVICE_TYPES = [
        ('WEB', 'เว็บเบราว์เซอร์ (Web Browser)'),
        ('IOS', 'ไอโฟน/ไอแพด (iOS Device)'),
        ('ANDROID', 'แอนดรอยด์ (Android Device)'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='fcm_tokens',
        verbose_name='ผู้ใช้งาน'
    )
    token = models.CharField(max_length=500, unique=True, verbose_name='FCM Device Token')
    device_type = models.CharField(max_length=10, choices=DEVICE_TYPES, default='WEB', verbose_name='ประเภทอุปกรณ์')
    is_active = models.BooleanField(default=True, verbose_name='สถานะใช้งาน')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='ลงทะเบียนเมื่อ')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='อัปเดตล่าสุด')

    class Meta:
        verbose_name = 'FCM Device Token (Push Notification)'
        verbose_name_plural = 'รายการ FCM Device Tokens (Push Notifications)'
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.user.username} - [{self.get_device_type_display()}] {self.token[:20]}..."


class UserListingOTP(models.Model):
    phone = models.CharField(max_length=50, verbose_name='เบอร์โทรศัพท์')
    otp_code = models.CharField(max_length=6, verbose_name='รหัส OTP 6 หลัก')
    is_verified = models.BooleanField(default=False, verbose_name='ยืนยันแล้ว')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='สร้างเมื่อ')
    expires_at = models.DateTimeField(verbose_name='หมดอายุเมื่อ')

    class Meta:
        verbose_name = 'รหัส OTP การลงขายทรัพย์'
        verbose_name_plural = 'รายการ OTP การลงขายทรัพย์'
        ordering = ['-created_at']

    def is_valid(self):
        if self.is_verified:
            return False, 'รหัส OTP นี้ถูกใช้งานแล้ว'
        if timezone.now() > self.expires_at:
            return False, 'รหัส OTP หมดอายุแล้ว (เกิน 5 นาที)'
        return True, 'รหัส OTP ถูกต้อง'

    @classmethod
    def generate_otp(cls, phone, validity_minutes=5):
        code = str(secrets.randbelow(900000) + 100000)
        expires_at = timezone.now() + timedelta(minutes=validity_minutes)
        return cls.objects.create(
            phone=phone,
            otp_code=code,
            expires_at=expires_at
        )

    def __str__(self):
        return f"{self.phone} - OTP: {self.otp_code} ({'Verified' if self.is_verified else 'Pending'})"





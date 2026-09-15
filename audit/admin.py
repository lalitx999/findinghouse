from django.contrib import admin
from django.utils.html import format_html
from .models import AuditLog, UserSession, LoginAttempt, UserTwoFactorOTP

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'user', 'action_badge', 'model_name', 'object_id', 'object_repr', 'ip_address')
    list_filter = ('action', 'model_name', 'timestamp')
    search_fields = ('user__username', 'object_id', 'object_repr', 'model_name', 'ip_address', 'details')
    readonly_fields = ('timestamp', 'user', 'action', 'model_name', 'object_id', 'object_repr', 'details', 'ip_address', 'user_agent')
    ordering = ('-timestamp',)

    def action_badge(self, obj):
        colors = {
            'CREATE': '#28a745',  # Green
            'UPDATE': '#fd7e14',  # Orange
            'DELETE': '#dc3545',  # Red
            'VIEW': '#007bff',    # Blue
            'LOGIN': '#6f42c1',   # Purple
            'LOGOUT': '#6c757d',  # Gray
        }
        color = colors.get(obj.action, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 4px; font-weight: bold; font-size: 11px;">{}</span>',
            color,
            obj.get_action_display()
        )
    action_badge.short_description = 'ประเภทกิจกรรม'

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    list_display = ('user', 'device_name', 'ip_address', 'is_active', 'created_at', 'last_activity')
    list_filter = ('is_active', 'created_at')
    search_fields = ('user__username', 'ip_address', 'device_name', 'user_agent')
    readonly_fields = ('created_at', 'last_activity', 'session_key')
    actions = ['force_revoke_sessions']

    @admin.action(description='เตะออกจากระบบ (Revoke Active Sessions)')
    def force_revoke_sessions(self, request, queryset):
        count = queryset.update(is_active=False)
        self.message_user(request, f"เตะอุปกรณ์ออกจากระบบสำเร็จ {count} รายการ")


@admin.register(LoginAttempt)
class LoginAttemptAdmin(admin.ModelAdmin):
    list_display = ('username', 'ip_address', 'failed_count', 'lock_status_badge', 'locked_until', 'last_attempt')
    list_filter = ('is_locked', 'last_attempt')
    search_fields = ('username', 'ip_address')
    actions = ['unlock_accounts']

    def lock_status_badge(self, obj):
        if obj.check_is_locked():
            return format_html('<span style="background-color: #dc3545; color: white; padding: 3px 8px; border-radius: 4px; font-weight: bold; font-size: 11px;">LOCKED</span>')
        return format_html('<span style="background-color: #28a745; color: white; padding: 3px 8px; border-radius: 4px; font-weight: bold; font-size: 11px;">NORMAL</span>')
    lock_status_badge.short_description = 'สถานะบัญชี'

    @admin.action(description='ปลดล็อกบัญชี (Unlock Selected Accounts)')
    def unlock_accounts(self, request, queryset):
        count = queryset.update(is_locked=False, failed_count=0, locked_until=None)
        self.message_user(request, f"ปลดล็อกบัญชีสำเร็จ {count} บัญชี")


from .models import AuditLog, UserSession, LoginAttempt, UserTwoFactorOTP, Notification, WebhookConfig, FCMDeviceToken
from .utils_notify import dispatch_webhook_event, send_line_notification
from django.contrib import messages

@admin.register(UserTwoFactorOTP)
class UserTwoFactorOTPAdmin(admin.ModelAdmin):
    list_display = ('user', 'otp_code', 'is_used', 'attempts', 'created_at', 'expires_at')
    list_filter = ('is_used', 'created_at')
    search_fields = ('user__username', 'otp_code')
    readonly_fields = ('created_at', 'expires_at', 'otp_code')


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('user__username', 'title', 'message')


@admin.register(WebhookConfig)
class WebhookConfigAdmin(admin.ModelAdmin):
    list_display = ('name', 'url', 'event_type', 'is_active', 'created_at')
    list_filter = ('event_type', 'is_active', 'created_at')
    search_fields = ('name', 'url')
    actions = ['test_dispatch_webhook', 'test_send_line']

    @admin.action(description="🚀 ทดสอบส่งข้อมูล Webhook (Test Dispatch Webhook)")
    def test_dispatch_webhook(self, request, queryset):
        test_payload = {
            'event': 'TEST_DISPATCH',
            'message': 'ทดสอบการส่ง Webhook จากระบบ Finding House Control Center',
            'sender': request.user.username
        }
        for hook in queryset:
            count = dispatch_webhook_event(hook.event_type, test_payload)
            self.message_user(request, f"ส่งข้อมูลทดสอบไปยัง Webhook '{hook.name}' สำเร็จแล้ว", messages.SUCCESS)

    @admin.action(description="📲 ทดสอบส่งแจ้งเตือนเข้า LINE (Test LINE Notify)")
    def test_send_line(self, request, queryset):
        msg = f"\n📌 [Finding House Test]\nทดสอบการส่งแจ้งเตือนโดย {request.user.username}\nระบบทำงานปกติ 100%"
        success = send_line_notification(msg)
        if success:
            self.message_user(request, "ส่งข้อความทดสอบ LINE Notify สำเร็จแล้ว", messages.SUCCESS)
        else:
            self.message_user(request, "ไม่สามารถส่ง LINE Notify ได้ (กรุณาเช็ค LINE_NOTIFY_TOKEN ใน .env)", messages.WARNING)


@admin.register(FCMDeviceToken)
class FCMDeviceTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'device_type', 'short_token', 'created_at', 'updated_at')
    list_filter = ('device_type', 'created_at')
    search_fields = ('user__username', 'token')
    readonly_fields = ('created_at', 'updated_at')

    def short_token(self, obj):
        return obj.token[:40] + ('...' if len(obj.token) > 40 else '')
    short_token.short_description = 'Device Token'




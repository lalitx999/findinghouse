import logging
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags

logger = logging.getLogger(__name__)

def send_inquiry_notification_to_admin(inquiry):
    """
    ส่งอีเมลแจ้งเตือนทีมงาน/แอดมิน เมื่อมีผู้สนใจกรอกฟอร์มติดต่อกลับเข้ามา
    """
    if not settings.EMAIL_HOST_USER or not settings.EMAIL_HOST_PASSWORD:
        logger.warning("Email credentials (EMAIL_HOST_USER / EMAIL_HOST_PASSWORD) not set in .env yet.")
        return False

    admin_email = getattr(settings, 'ADMIN_NOTIFICATION_EMAIL', settings.EMAIL_HOST_USER)
    if not admin_email:
        admin_email = settings.EMAIL_HOST_USER

    property_info = f"รหัสทรัพย์: {inquiry.property.property_code} - {inquiry.property.title}" if inquiry.property else "สอบถามข้อมูลทั่วไป"

    subject = f"[Finding House] มีผู้สนใจติดต่อกลับใหม่: คุณ {inquiry.name}"
    
    html_message = f"""
    <div style="font-family: 'Tahoma', sans-serif; max-width: 600px; margin: 0 auto; border: 1px solid #e2e8f0; border-radius: 12px; padding: 24px; background-color: #ffffff;">
        <h2 style="color: #0f172a; border-bottom: 2px solid #f1f5f9; padding-bottom: 12px;">แจ้งเตือนข้อความติดต่อกลับใหม่ (New Inquiry)</h2>
        <p style="color: #475569; font-size: 14px;">มีผู้สนใจกรอกฟอร์มติดต่อกลับผ่านหน้าเว็บไซต์ รายละเอียดดังนี้:</p>
        
        <table style="width: 100%; border-collapse: collapse; margin: 20px 0; font-size: 14px;">
            <tr>
                <td style="padding: 8px 0; font-weight: bold; color: #64748b; width: 140px;">ผู้ติดต่อ:</td>
                <td style="padding: 8px 0; color: #0f172a; font-weight: bold;">คุณ {inquiry.name}</td>
            </tr>
            <tr>
                <td style="padding: 8px 0; font-weight: bold; color: #64748b;">เบอร์โทรศัพท์:</td>
                <td style="padding: 8px 0; color: #0f172a;">{inquiry.phone}</td>
            </tr>
            <tr>
                <td style="padding: 8px 0; font-weight: bold; color: #64748b;">อีเมล:</td>
                <td style="padding: 8px 0; color: #0f172a;">{inquiry.email}</td>
            </tr>
            <tr>
                <td style="padding: 8px 0; font-weight: bold; color: #64748b;">ทรัพย์สินที่สนใจ:</td>
                <td style="padding: 8px 0; color: #0f172a;">{property_info}</td>
            </tr>
            <tr>
                <td style="padding: 8px 0; font-weight: bold; color: #64748b; vertical-align: top;">ข้อความเพิ่มเติม:</td>
                <td style="padding: 8px 0; color: #334155; background: #f8fafc; padding: 10px; border-radius: 6px;">{inquiry.message}</td>
            </tr>
        </table>
        
        <div style="margin-top: 24px; padding-top: 16px; border-top: 1px solid #f1f5f9; text-align: center;">
            <a href="http://127.0.0.1:8000/admin/inquiries/inquiry/{inquiry.id}/change/" style="background-color: #0f172a; color: #ffffff; padding: 10px 20px; border-radius: 8px; text-decoration: none; font-size: 13px; font-weight: bold; display: inline-block;">เปิดดูในระบบ Admin</a>
        </div>
    </div>
    """
    
    plain_message = strip_tags(html_message)

    try:
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[admin_email],
            html_message=html_message,
            fail_silently=True
        )
        return True
    except Exception as e:
        logger.error(f"Failed to send admin inquiry email: {e}")
        return False


def send_auto_reply_to_customer(inquiry):
    """
    ส่งอีเมลตอบรับอัตโนมัติ (Auto-reply) ไปยังอีเมลของผู้ติดต่อ
    """
    if not settings.EMAIL_HOST_USER or not settings.EMAIL_HOST_PASSWORD or not inquiry.email:
        return False

    property_info = f"ทรัพย์สินรหัส: {inquiry.property.property_code} - {inquiry.property.title}" if inquiry.property else "บริการอสังหาริมทรัพย์ Finding House"

    subject = "[Finding House] ขอบคุณที่สนใจสอบถามข้อมูลอสังหาริมทรัพย์"
    
    html_message = f"""
    <div style="font-family: 'Tahoma', sans-serif; max-width: 600px; margin: 0 auto; border: 1px solid #e2e8f0; border-radius: 12px; padding: 24px; background-color: #ffffff;">
        <h2 style="color: #0f172a; border-bottom: 2px solid #f1f5f9; padding-bottom: 12px;">ขอบคุณที่ติดต่อ Finding House</h2>
        <p style="color: #334155; font-size: 14px; line-height: 1.6;">
            เรียน คุณ <strong>{inquiry.name}</strong>,<br><br>
            ทางทีมงาน Finding House ได้รับข้อความสอบถามข้อมูลของท่านเกี่ยวกับ <strong>{property_info}</strong> เรียบร้อยแล้ว<br>
            เจ้าหน้าที่ฝ่ายดูแลลูกค้าจะทำการตรวจสอบรายละเอียดและติดต่อกลับท่านโดยเร็วที่สุด
        </p>

        <div style="background-color: #f8fafc; border-left: 4px solid #0f172a; padding: 14px; margin: 20px 0; border-radius: 4px;">
            <p style="margin: 0; font-size: 13px; color: #475569; font-weight: bold;">สรุปข้อความสอบถามของท่าน:</p>
            <p style="margin: 6px 0 0 0; font-size: 13px; color: #334155;">&ldquo;{inquiry.message}&rdquo;</p>
        </div>

        <p style="color: #64748b; font-size: 13px; line-height: 1.5;">
            หากท่านมีเรื่องด่วนประการใด สามารถติดต่อทีมงานโดยตรงได้ที่เบอร์โทรศัพท์ 02-123-4567 หรือแชตผ่านหน้าเว็บไซต์ได้ตลอดเวลาครับ
        </p>

        <div style="margin-top: 24px; padding-top: 16px; border-top: 1px solid #f1f5f9; font-size: 12px; color: #94a3b8; text-align: center;">
            Finding House - Real Estate Platform & CRM Operations<br>
            อีเมลนี้เป็นการตอบรับอัตโนมัติจากระบบ
        </div>
    </div>
    """
    
    plain_message = strip_tags(html_message)

    try:
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[inquiry.email],
            html_message=html_message,
            fail_silently=True
        )
        return True
    except Exception as e:
        logger.error(f"Failed to send customer auto-reply email: {e}")
        return False

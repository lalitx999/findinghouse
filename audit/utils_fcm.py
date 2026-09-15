import os
import logging
from django.conf import settings
from .models import FCMDeviceToken

logger = logging.getLogger(__name__)

def send_fcm_admin_notification(title: str, body: str, data: dict = None) -> bool:
    """
    FCM (Firebase Cloud Messaging) Admin Push Notification Engine.
    ยิงการแจ้งเตือน Push Notification หาอุปกรณ์ทีมงานนายหน้าและแอดมินทุกคนในระบบ
    ทำงานแบบ Fallback / Dry-Run Logging Mode หากยังไม่ได้ใส่ไฟล์คีย์ Firebase จริง
    """
    data = data or {}
    cred_path = getattr(settings, 'FIREBASE_CREDENTIALS_PATH', os.getenv('FIREBASE_CREDENTIALS_PATH', ''))

    if not cred_path or not os.path.exists(cred_path):
        logger.info(f"[FCM Push Notification - Dry Run] Title: '{title}' | Body: '{body}' | Data: {data}")
        print(f"[FCM Admin Alert - Dry Run] {title}: {body} (Data: {data})")
        return True

    try:
        import firebase_admin
        from firebase_admin import credentials, messaging

        if not firebase_admin._apps:
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)

        # Retrieve all active admin & agent device tokens
        tokens = list(FCMDeviceToken.objects.values_list('token', flat=True))
        if not tokens:
            logger.info("No registered FCM tokens found.")
            return True

        message = messaging.MulticastMessage(
            notification=messaging.Notification(title=title, body=body),
            data={k: str(v) for k, v in data.items()},
            tokens=tokens
        )
        response = messaging.send_multicast(message)
        logger.info(f"FCM Multicast sent successfully: {response.success_count} success, {response.failure_count} failure")
        return True
    except Exception as e:
        logger.error(f"[FCM Notification Error] Failed to send push notification: {e}")
        return False


def send_fcm_user_notification(user, title: str, body: str, data: dict = None) -> bool:
    """
    ส่งการแจ้งเตือน FCM หาอุปกรณ์ของผู้ใช้งานที่ระบุโดยเฉพาะ
    """
    data = data or {}
    cred_path = getattr(settings, 'FIREBASE_CREDENTIALS_PATH', os.getenv('FIREBASE_CREDENTIALS_PATH', ''))

    if not cred_path or not os.path.exists(cred_path):
        logger.info(f"[FCM User Notification - Dry Run] Target User: {user.username} | Title: '{title}' | Body: '{body}'")
        return True

    try:
        import firebase_admin
        from firebase_admin import credentials, messaging

        if not firebase_admin._apps:
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)

        tokens = list(FCMDeviceToken.objects.filter(user=user).values_list('token', flat=True))
        if not tokens:
            return True

        message = messaging.MulticastMessage(
            notification=messaging.Notification(title=title, body=body),
            data={k: str(v) for k, v in data.items()},
            tokens=tokens
        )
        messaging.send_multicast(message)
        return True
    except Exception as e:
        logger.error(f"[FCM User Notification Error] Failed: {e}")
        return False

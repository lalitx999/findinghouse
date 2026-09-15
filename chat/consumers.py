import json
from audit.utils_fcm import send_fcm_admin_notification

class ChatConsumer:
    """
    Real-Time WebSocket Chat Consumer Handler (ASGI Compatible)
    """
    def __init__(self, *args, **kwargs):
        pass

    async def connect(self):
        # Stub for ASGI WebSocket Handshake
        pass

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data=None, bytes_data=None):
        if text_data:
            data = json.loads(text_data)
            message = data.get('message', '')
            sender_name = data.get('sender_name', 'Guest')
            
            # Send FCM Admin Notification on incoming WebSocket chat message
            send_fcm_admin_notification(
                title=f"💬 [WebSocket Live] ข้อความใหม่จาก {sender_name}",
                body=message,
                data={'type': 'websocket_chat'}
            )

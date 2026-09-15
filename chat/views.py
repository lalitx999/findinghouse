from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from chat.models import ChatRoom, ChatMessage
from chat.serializers import ChatRoomSerializer, ChatMessageSerializer
from audit.utils_fcm import send_fcm_admin_notification

class ChatRoomViewSet(viewsets.ModelViewSet):
    queryset = ChatRoom.objects.all()
    serializer_class = ChatRoomSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'room_name'

    @action(detail=True, methods=['get'])
    def messages(self, request, room_name=None):
        room = self.get_object()
        messages = room.messages.all()
        serializer = ChatMessageSerializer(messages, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def send_message(self, request, room_name=None):
        room = self.get_object()
        sender_name = request.data.get('sender_name', 'Guest Buyer')
        message_text = request.data.get('message', '')
        is_agent = request.data.get('is_agent', False)

        if not message_text.strip():
            return Response({'detail': 'Message content cannot be empty.'}, status=status.HTTP_400_BAD_REQUEST)

        msg = ChatMessage.objects.create(
            room=room,
            sender=request.user if request.user.is_authenticated else None,
            sender_name=sender_name,
            message=message_text,
            is_agent=is_agent
        )

        room.save() # Update updated_at timestamp

        # Dispatch FCM Admin Notification Push Alert
        if not is_agent:
            send_fcm_admin_notification(
                title=f"💬 ข้อความแชทใหม่จาก {sender_name}",
                body=message_text[:100],
                data={'room_name': room.room_name}
            )

        return Response(ChatMessageSerializer(msg).data, status=status.HTTP_201_CREATED)

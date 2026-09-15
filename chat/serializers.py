from rest_framework import serializers
from chat.models import ChatRoom, ChatMessage

class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = ['id', 'room', 'sender', 'sender_name', 'message', 'is_agent', 'is_read', 'created_at']

class ChatRoomSerializer(serializers.ModelSerializer):
    last_message = serializers.SerializerMethodField()
    property_title = serializers.CharField(source='property.title', read_only=True, default=None)

    class Meta:
        model = ChatRoom
        fields = ['id', 'room_name', 'property', 'property_title', 'lead', 'agent', 'is_active', 'last_message', 'created_at', 'updated_at']

    def get_last_message(self, obj):
        last_msg = obj.messages.last()
        if last_msg:
            return ChatMessageSerializer(last_msg).data
        return None

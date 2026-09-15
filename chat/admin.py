from django.contrib import admin
from .models import ChatRoom, ChatMessage

class ChatMessageInline(admin.TabularInline):
    model = ChatMessage
    extra = 0
    readonly_fields = ('created_at',)
    fields = ('sender_name', 'message', 'is_agent', 'is_read', 'created_at')

@admin.register(ChatRoom)
class ChatRoomAdmin(admin.ModelAdmin):
    list_display = ('room_name', 'property', 'lead', 'agent', 'is_active', 'updated_at', 'created_at')
    list_filter = ('is_active', 'created_at', 'updated_at')
    search_fields = ('room_name', 'property__title', 'property__property_code', 'lead__name', 'agent__username')
    inlines = [ChatMessageInline]

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'room', 'sender_name', 'short_message', 'is_agent', 'is_read', 'created_at')
    list_filter = ('is_agent', 'is_read', 'created_at')
    search_fields = ('sender_name', 'message', 'room__room_name')
    readonly_fields = ('created_at',)

    def short_message(self, obj):
        return obj.message[:50] + ('...' if len(obj.message) > 50 else '')
    short_message.short_description = 'ข้อความ'

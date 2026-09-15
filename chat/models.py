from django.db import models
from django.conf import settings
from properties.models import Property
from crm.models import Lead

class ChatRoom(models.Model):
    room_name = models.CharField(max_length=100, unique=True, verbose_name="รหัสห้องแชต (Room Code)")
    property = models.ForeignKey(Property, on_delete=models.CASCADE, null=True, blank=True, related_name='chat_rooms', verbose_name="ทรัพย์สินที่สอบถาม")
    lead = models.ForeignKey(Lead, on_delete=models.SET_NULL, null=True, blank=True, related_name='chat_rooms', verbose_name="ลีด/ลูกค้า")
    agent = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='agent_chat_rooms', verbose_name="นายหน้าผู้ดูแล")
    
    is_active = models.BooleanField(default=True, verbose_name="สถานะห้องสนทนา")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="สร้างห้องเมื่อ")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="ข้อความล่าสุดเมื่อ")

    class Meta:
        verbose_name = "ห้องสนทนาเรียลไทม์ (Chat Room)"
        verbose_name_plural = "รายการห้องสนทนาเรียลไทม์ (Chat Rooms)"
        ordering = ['-updated_at']

    def __str__(self):
        prop_str = f" [{self.property.property_code}]" if self.property else ""
        return f"ChatRoom #{self.room_name}{prop_str}"


class ChatMessage(models.Model):
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages', verbose_name="ห้องสนทนา")
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='sent_messages', verbose_name="ผู้ส่ง")
    sender_name = models.CharField(max_length=150, verbose_name="ชื่อผู้ส่ง")
    message = models.TextField(verbose_name="ข้อความ")
    is_agent = models.BooleanField(default=False, verbose_name="ข้อความจากนายหน้า")
    is_read = models.BooleanField(default=False, verbose_name="อ่านแล้ว")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="เวลาที่ส่ง")

    class Meta:
        verbose_name = "ข้อความสนทนา (Chat Message)"
        verbose_name_plural = "รายการข้อความสนทนา (Chat Messages)"
        ordering = ['created_at']

    def __str__(self):
        return f"[{self.sender_name}] {self.message[:30]}"

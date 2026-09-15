from django.db import models
from properties.models import Property

class Inquiry(models.Model):
    property = models.ForeignKey(Property, on_delete=models.SET_NULL, null=True, blank=True, related_name='inquiries', verbose_name="อสังหาริมทรัพย์ที่สนใจ")
    name = models.CharField(max_length=150, verbose_name="ชื่อผู้ติดต่อ")
    email = models.EmailField(verbose_name="อีเมล")
    phone = models.CharField(max_length=30, verbose_name="เบอร์โทรศัพท์")
    message = models.TextField(verbose_name="ข้อความติดต่อ")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="ติดต่อเข้ามาเมื่อ")

    class Meta:
        verbose_name = "ข้อความติดต่อกลับ"
        verbose_name_plural = "ข้อความติดต่อกลับ"
        ordering = ['-created_at']

    def __str__(self):
        property_lbl = self.property.property_code if self.property else "ทั่วไป"
        return f"คุณ {self.name} สนใจ: {property_lbl}"

from django.db import models
from django.utils.text import slugify
from properties.models import Property

class ReviewPost(models.Model):
    title = models.CharField(max_length=200, verbose_name="หัวข้อรีวิว")
    slug = models.SlugField(max_length=220, unique=True, blank=True, verbose_name="สลัก (URL Slug)")
    cover_image = models.ImageField(upload_to='reviews/', null=True, blank=True, verbose_name="รูปหน้าปกบทความ")
    content = models.TextField(verbose_name="เนื้อหาบทความรีวิว")
    property = models.ForeignKey(Property, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviews', verbose_name="อสังหาฯ ที่รีวิว")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="สร้างเมื่อ")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="แก้ไขล่าสุด")

    class Meta:
        verbose_name = "บทความรีวิวอสังหาฯ"
        verbose_name_plural = "บทความรีวิวอสังหาฯ"
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title, allow_unicode=True)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class Article(models.Model):
    title = models.CharField(max_length=250, verbose_name="หัวข้อบทความ")
    slug = models.SlugField(max_length=260, unique=True, blank=True, verbose_name="สลัก (URL Slug)")
    category = models.CharField(max_length=100, default='ความรู้เรื่องบ้าน', verbose_name="หมวดหมู่บทความ")
    cover_image = models.ImageField(upload_to='articles/', null=True, blank=True, verbose_name="รูปภาพหน้าปก")
    excerpt = models.TextField(blank=True, verbose_name="เกริ่นนำ/สรุปย่อ")
    content = models.TextField(verbose_name="เนื้อหาบทความ")
    views_count = models.PositiveIntegerField(default=0, verbose_name="จำนวนผู้เข้าชม")
    is_published = models.BooleanField(default=True, verbose_name="เผยแพร่แล้ว")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="สร้างเมื่อ")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="แก้ไขล่าสุด")

    class Meta:
        verbose_name = "บทความความรู้เรื่องบ้าน"
        verbose_name_plural = "บทความความรู้เรื่องบ้าน"
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title, allow_unicode=True)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class CustomerReview(models.Model):
    reviewer_name = models.CharField(max_length=120, verbose_name="ชื่อผู้รีวิว")
    reviewer_role = models.CharField(max_length=100, default="ลูกค้าผู้ใช้บริการ", verbose_name="บทบาท/สถานะ")
    rating = models.PositiveIntegerField(default=5, verbose_name="คะแนนดาว (1-5)")
    comment = models.TextField(verbose_name="ความคิดเห็น/ข้อความรีวิว")
    property = models.ForeignKey(Property, on_delete=models.SET_NULL, null=True, blank=True, related_name='customer_reviews', verbose_name="อสังหาฯ ที่เกี่ยวข้อง (ถ้ามี)")
    avatar = models.ImageField(upload_to='reviews/avatars/', null=True, blank=True, verbose_name="รูปโปรไฟล์/อวตาร")
    is_approved = models.BooleanField(default=False, verbose_name="ผ่านการอนุมัติให้แสดงผล")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="สร้างเมื่อ")

    class Meta:
        verbose_name = "รีวิวจากลูกค้าจริง"
        verbose_name_plural = "รีวิวจากลูกค้าจริง"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.reviewer_name} ({self.rating}★) - {'อนุมัติแล้ว' if self.is_approved else 'รออนุมัติ'}"

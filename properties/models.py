from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from django.contrib.auth import get_user_model

User = get_user_model()

class Category(models.Model):
    name = models.Model
    name = models.CharField(max_length=100, verbose_name="ชื่อหมวดหมู่")
    slug = models.SlugField(max_length=120, unique=True, verbose_name="สลัก (URL Slug)")

    class Meta:
        verbose_name = "หมวดหมู่อสังหาฯ"
        verbose_name_plural = "หมวดหมู่อสังหาฯ"

    def __str__(self):
        return self.name


class Location(models.Model):
    name = models.CharField(max_length=100, verbose_name="ทำเล/ย่าน")
    slug = models.SlugField(max_length=120, unique=True, blank=True, verbose_name="สลัก (URL Slug)")

    class Meta:
        verbose_name = "ทำเลที่ตั้ง"
        verbose_name_plural = "ทำเลที่ตั้ง"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Property(models.Model):
    PROPERTY_TYPES = [
        ('SALE', 'ขาย'),
        ('RENT', 'เช่า'),
    ]
    STATUS_CHOICES = [
        ('DRAFT', 'ร่าง'),
        ('REVIEW', 'รอการตรวจสอบ'),
        ('PUBLISHED', 'เผยแพร่'),
        ('NEGOTIATING', 'อยู่ระหว่างเจรจา'),
        ('BOOKED', 'จองแล้ว'),
        ('SOLD', 'ขายแล้ว'),
        ('PAUSED', 'พักประกาศ'),
        ('EXPIRED', 'หมดอายุ'),
        ('CANCELLED', 'ยกเลิก'),
    ]
    SOURCE_CHOICES = [
        ('FINDING_HOUSE', 'Finding House'),
        ('CO_BROKER', 'Agent / Co-Broker ภายนอก'),
    ]
    SALE_CONDITION_CHOICES = [
        ('SALE_ONLY', 'ขายอย่างเดียว'),
        ('SALE_AND_RENT', 'ขายและมีราคาเช่า'),
        ('SALE_WITH_TENANT', 'ขายพร้อมผู้เช่า'),
    ]

    title = models.CharField(max_length=200, verbose_name="หัวข้อประกาศ")
    slug = models.SlugField(max_length=220, unique=True, blank=True, verbose_name="สลัก (URL Slug)")
    property_code = models.CharField(max_length=50, unique=True, blank=True, verbose_name="รหัสทรัพย์ (สร้างให้อัตโนมัติ)")
    description = models.TextField(verbose_name="รายละเอียดทรัพย์")
    price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="ราคา (บาท)")
    property_type = models.CharField(max_length=10, choices=PROPERTY_TYPES, default='SALE', verbose_name="ประเภทประกาศ")
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='properties', verbose_name="หมวดหมู่")
    location = models.ForeignKey(Location, on_delete=models.PROTECT, related_name='properties', verbose_name="ทำเลที่ตั้ง")
    
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES, default='FINDING_HOUSE', verbose_name="แหล่งทรัพย์")
    sale_condition = models.CharField(max_length=20, choices=SALE_CONDITION_CHOICES, default='SALE_ONLY', verbose_name="เงื่อนไขงาน")

    bedrooms = models.PositiveIntegerField(null=True, blank=True, verbose_name="จำนวนห้องนอน")
    bathrooms = models.PositiveIntegerField(null=True, blank=True, verbose_name="จำนวนห้องน้ำ")
    size_land = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True, verbose_name="ขนาดที่ดิน (ตารางวา)")
    size_usable = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True, verbose_name="พื้นที่ใช้สอย (ตารางเมตร)")
    
    # New Fields for Rich Detail view & Interactive Map
    google_maps_link = models.URLField(max_length=500, null=True, blank=True, verbose_name="ลิงก์ Google Maps")
    latitude = models.FloatField(null=True, blank=True, verbose_name="ละติจูด (Lat)")
    longitude = models.FloatField(null=True, blank=True, verbose_name="ลองจิจูด (Lng)")
    floors = models.PositiveIntegerField(null=True, blank=True, verbose_name="จำนวนชั้น")
    parking_spaces = models.PositiveIntegerField(null=True, blank=True, verbose_name="ที่จอดรถ (คัน)")
    direction = models.CharField(max_length=50, null=True, blank=True, verbose_name="ทิศหน้าทรัพย์")
    furniture = models.CharField(max_length=100, null=True, blank=True, verbose_name="เฟอร์นิเจอร์")
    pet_friendly = models.BooleanField(default=False, verbose_name="รับสัตว์เลี้ยง")
    common_fee = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="ค่าส่วนกลาง (บาท/เดือน)")
    availability = models.BooleanField(default=True, verbose_name="สถานะว่าง")
    minimum_lease = models.CharField(max_length=100, null=True, blank=True, verbose_name="สัญญาขั้นต่ำ")
    deposit = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, verbose_name="เงินประกัน (บาท)")
    advance_payment = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, verbose_name="เงินล่วงหน้า (บาท)")
    move_in_date = models.CharField(max_length=100, null=True, blank=True, verbose_name="พร้อมเข้าอยู่เมื่อ")

    # Direct Seller Info (สำหรับผู้ใช้ทั่วไปลงประกาศเอง)
    seller_name = models.CharField(max_length=150, null=True, blank=True, verbose_name="ชื่อผู้ขายตรง")
    seller_phone = models.CharField(max_length=50, null=True, blank=True, verbose_name="เบอร์โทรผู้ขายตรง")
    seller_line_id = models.CharField(max_length=100, null=True, blank=True, verbose_name="LINE ID ผู้ขายตรง")
    is_direct_seller = models.BooleanField(default=False, verbose_name="ประกาศจากผู้ขายตรง")

    landmarks = models.JSONField(default=list, blank=True, verbose_name="สถานที่ใกล้เคียง (Structured JSON)")
    features = models.JSONField(default=dict, blank=True, verbose_name="คุณสมบัติจำเพาะ (JSON)")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT', verbose_name="สถานะประกาศ")
    agent = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='managed_properties', verbose_name="ตัวแทนผู้ดูแล")
    
    last_confirmed_at = models.DateTimeField(default=timezone.now, verbose_name="วันที่ยืนยันสถานะล่าสุด")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="สร้างเมื่อ")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="แก้ไขล่าสุด")

    @property
    def price_per_sqm(self):
        if self.price and self.size_usable and float(self.size_usable) > 0:
            return round(float(self.price) / float(self.size_usable), 2)
        return None

    @property
    def price_per_sqwah(self):
        if self.price and self.size_land and float(self.size_land) > 0:
            return round(float(self.price) / float(self.size_land), 2)
        return None

    @property
    def price_per_rai(self):
        if self.price and self.size_land and float(self.size_land) > 0:
            rai = float(self.size_land) / 400.0
            return round(float(self.price) / rai, 2)
        return None

    def get_seo_search_phrases(self):
        """
        Generates SEO phrases combining action, location, and structured landmarks.
        Example: ["ขายบ้าน บางนา-ตราด ใกล้เมกาบางนา 2 กม.", "ขายบ้านใกล้ ABAC"]
        """
        phrases = []
        action = "ขาย" if self.property_type == 'SALE' else "เช่า"
        cat_name = self.category.name if self.category else "อสังหาฯ"
        loc_name = self.location.name if self.location else ""
        
        base_phrase = f"{action}{cat_name} {loc_name}".strip()
        phrases.append(base_phrase)
        
        if isinstance(self.landmarks, list):
            for item in self.landmarks:
                if isinstance(item, dict) and item.get('name'):
                    name = item['name']
                    dist = f" {item['distance']}" if item.get('distance') else ""
                    phrases.append(f"{base_phrase} ใกล้{name}{dist}")
                    
        return phrases

    class Meta:
        verbose_name = "ประกาศอสังหาฯ"
        verbose_name_plural = "ประกาศอสังหาฯ"
        ordering = ['-created_at']

    def generate_code(self):
        cat_slug = self.category.slug.lower() if self.category else ""
        cat_name = self.category.name if self.category else ""
        
        prefix = 'H'
        if 'condo' in cat_slug or 'คอนโด' in cat_name:
            prefix = 'C'
        elif 'land' in cat_slug or 'ที่ดิน' in cat_name:
            prefix = 'L'
        elif 'warehouse' in cat_slug or 'โกดัง' in cat_name:
            prefix = 'W'
        elif 'factory' in cat_slug or 'โรงงาน' in cat_name:
            prefix = 'F'
        elif 'commercial' in cat_slug or 'พาณิชย์' in cat_name:
            prefix = 'B'
        elif 'office' in cat_slug or 'สำนักงาน' in cat_name:
            prefix = 'O'
        elif 'apartment' in cat_slug or 'อพาร์ตเมนต์' in cat_name or 'หอพัก' in cat_name:
            prefix = 'A'
        elif 'hotel' in cat_slug or 'โรงแรม' in cat_name or 'รีสอร์ต' in cat_name:
            prefix = 'T'
        elif 'house' in cat_slug or 'บ้าน' in cat_name:
            prefix = 'H'
        
        import re
        existing_codes = Property.objects.filter(property_code__startswith=prefix).values_list('property_code', flat=True)
        max_num = 0
        for code in existing_codes:
            match = re.search(rf'^{prefix}(\d+)$', code)
            if match:
                num = int(match.group(1))
                if num > max_num:
                    max_num = num
        
        next_num = max_num + 1
        return f"{prefix}{next_num:04d}"

    def calculate_completeness_score(self):
        """
        Calculates the completeness score (0-100%) and returns missing fields.
        """
        score = 0
        missing = []

        # 1. Title (10 pts)
        if self.title and len(self.title.strip()) >= 10:
            score += 10
        else:
            missing.append("ชื่อหัวข้อประกาศ (อย่างน้อย 10 ตัวอักษร)")

        # 2. Description (10 pts)
        if self.description and len(self.description.strip()) >= 30:
            score += 10
        else:
            missing.append("รายละเอียดทรัพย์ (อย่างน้อย 30 ตัวอักษร)")

        # 3. Price (10 pts)
        if self.price and float(self.price) > 0:
            score += 10
        else:
            missing.append("ราคาขาย/เช่า")

        # 4. Images count (20 pts max: 20+ images = 20, 10-19 images = 13, 1-9 images = 7)
        img_count = self.images.count() if self.pk else 0
        if img_count >= 20:
            score += 20
        elif img_count >= 10:
            score += 13
            missing.append(f"รูปภาพทรัพย์ (แนะนำอย่างน้อย 20 รูป, ปัจจุบันมี {img_count} รูป)")
        elif img_count >= 1:
            score += 7
            missing.append(f"รูปภาพทรัพย์ (แนะนำอย่างน้อย 20 รูป, ปัจจุบันมี {img_count} รูป)")
        else:
            missing.append("รูปภาพทรัพย์ (แนะนำอย่างน้อย 20 รูป)")

        # 5. Google Maps Link (10 pts)
        if self.google_maps_link and 'http' in self.google_maps_link:
            score += 10
        else:
            missing.append("ลิงก์พิกัด Google Maps")

        # 6. Land or Usable Size (10 pts)
        if (self.size_land and float(self.size_land) > 0) or (self.size_usable and float(self.size_usable) > 0):
            score += 10
        else:
            missing.append("ขนาดที่ดิน หรือ พื้นที่ใช้สอย")

        # 7. Bedrooms / Bathrooms (10 pts)
        if self.bedrooms is not None or self.bathrooms is not None:
            score += 10
        else:
            missing.append("จำนวนห้องนอน/ห้องน้ำ")

        # 8. Facing Direction (5 pts)
        if self.direction:
            score += 5
        else:
            missing.append("ทิศหน้าทรัพย์")

        # 9. Rental / Fee Details (5 pts)
        if self.common_fee or self.deposit or self.minimum_lease:
            score += 5
        else:
            missing.append("ข้อมูลค่าส่วนกลาง หรือ เงื่อนไขสัญญา/ประกัน")

        # 10. Specifications / Features (10 pts)
        if self.features and len(self.features) > 0:
            score += 10
        else:
            missing.append("คุณสมบัติและสเปกจำเพาะ (Features)")

        return {
            'score': min(score, 100),
            'missing': missing,
            'is_ready_for_publish': score >= 90
        }

    def check_duplicate(self):
        """
        Returns potential duplicate properties.
        """
        duplicates = Property.objects.exclude(pk=self.pk) if self.pk else Property.objects.all()
        
        matches = []
        if self.google_maps_link:
            map_matches = duplicates.filter(google_maps_link__iexact=self.google_maps_link)
            matches.extend(list(map_matches))
            
        if self.title:
            title_matches = duplicates.filter(title__icontains=self.title.strip(), category=self.category)
            for m in title_matches:
                if m not in matches:
                    matches.append(m)
                    
        return matches

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title, allow_unicode=True)
        if not self.property_code:
            self.property_code = self.generate_code()
        if self.features is None or self.features == "":
            self.features = {}
        super().save(*args, **kwargs)

    def __str__(self):
        return f"[{self.property_code}] {self.title}"


class PropertyImage(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='images', verbose_name="อสังหาฯ")
    image = models.ImageField(upload_to='properties/', verbose_name="รูปภาพ")
    is_cover = models.BooleanField(default=False, verbose_name="ภาพหน้าปก")
    order = models.PositiveIntegerField(default=0, verbose_name="ลำดับการแสดงผล")
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name="อัปโหลดเมื่อ")

    class Meta:
        verbose_name = "รูปภาพอสังหาฯ"
        verbose_name_plural = "รูปภาพอสังหาฯ"
        ordering = ['order', 'id']

    def save(self, *args, **kwargs):
        # Auto SEO renaming and watermarking if new image is uploaded
        if self.image and not getattr(self, '_watermarked', False):
            from properties.utils_image import process_and_watermark_image
            index = self.property.images.count() + 1 if self.property_id else 1
            prefix = f"{self.property.category.name}-{self.property.title}" if self.property_id and self.property.category else "property"
            
            processed = process_and_watermark_image(
                image_file=self.image,
                prefix=prefix,
                index=index,
                watermark_text="Finding House"
            )
            self.image = processed
            self._watermarked = True
            
        super().save(*args, **kwargs)


class Bookmark(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookmarks', verbose_name="ผู้ใช้งาน")
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='bookmarked_by', verbose_name="อสังหาฯ")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="บันทึกเมื่อ")

    class Meta:
        verbose_name = "รายการบันทึกอสังหาฯ"
        verbose_name_plural = "รายการบันทึกอสังหาฯ"
        unique_together = ('user', 'property')

    def __str__(self):
        return f"{self.user.username} - {self.property.property_code}"


class Consignment(models.Model):
    PROPERTY_TYPES = [
        ('HOUSE', 'บ้าน / ทาวน์เฮาส์ / ทาวน์โฮม'),
        ('CONDO', 'คอนโด'),
        ('LAND', 'ที่ดิน'),
        ('WAREHOUSE', 'โรงงาน / โกดัง'),
        ('HOTEL', 'โรงแรม / รีสอร์ต / อพาร์ตเมนต์'),
    ]
    STATUS_CHOICES = [
        ('PENDING', 'รอการตรวจสอบ'),
        ('REVIEWED', 'ตรวจสอบแล้ว'),
        ('APPROVED', 'อนุมัติ / สร้างประกาศแล้ว'),
        ('REJECTED', 'ปฏิเสธ'),
    ]

    # Owner details
    owner_name = models.CharField(max_length=150, verbose_name="ชื่อผู้ฝากขาย")
    owner_phone = models.CharField(max_length=50, verbose_name="เบอร์โทรศัพท์")
    owner_line_id = models.CharField(max_length=100, null=True, blank=True, verbose_name="LINE ID")
    owner_email = models.EmailField(null=True, blank=True, verbose_name="อีเมล")

    # Basic Property Info
    property_type = models.CharField(max_length=20, choices=PROPERTY_TYPES, verbose_name="ประเภททรัพย์")
    target_price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="ราคาที่ต้องการขาย/เช่า (บาท)")
    province = models.CharField(max_length=100, verbose_name="จังหวัด")
    district = models.CharField(max_length=100, verbose_name="อำเภอ / เขต")
    subdistrict = models.CharField(max_length=100, verbose_name="ตำบล / แขวง")
    google_maps_link = models.URLField(max_length=500, verbose_name="พิกัดทรัพย์ / ลิงก์ Google Maps")
    is_in_project = models.BooleanField(default=False, verbose_name="อยู่ในโครงการ")
    project_name = models.CharField(max_length=200, null=True, blank=True, verbose_name="ชื่อโครงการ / หมู่บ้าน")

    # Specifications according to property type (JSON storage)
    specs = models.JSONField(default=dict, blank=True, verbose_name="ข้อมูลรายละเอียดจำเพาะ (JSON)")

    # Additional optional details
    street_soi = models.CharField(max_length=200, null=True, blank=True, verbose_name="ถนน / ซอย")
    highlights = models.TextField(null=True, blank=True, verbose_name="จุดเด่นทรัพย์")
    nearby_places = models.TextField(null=True, blank=True, verbose_name="สถานที่ใกล้เคียง")
    direction = models.CharField(max_length=50, null=True, blank=True, verbose_name="ทิศ")
    condition = models.CharField(max_length=100, null=True, blank=True, verbose_name="สภาพทรัพย์")
    furniture = models.CharField(max_length=100, null=True, blank=True, verbose_name="เฟอร์นิเจอร์")
    amenities = models.TextField(null=True, blank=True, verbose_name="สิ่งอำนวยความสะดวก")
    notes = models.TextField(null=True, blank=True, verbose_name="หมายเหตุเพิ่มเติม")

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING', verbose_name="สถานะการตรวจสอบ")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="ส่งเรื่องเมื่อ")

    class Meta:
        verbose_name = "รายการฝากขายทรัพย์"
        verbose_name_plural = "รายการฝากขายทรัพย์"
        ordering = ['-created_at']

    def __str__(self):
        return f"ฝากขาย: คุณ {self.owner_name} ({self.get_property_type_display()}) - {self.target_price:,.0f} บาท"


class ConsignmentImage(models.Model):
    consignment = models.ForeignKey(Consignment, on_delete=models.CASCADE, related_name='images', verbose_name="คำขอฝากขาย")
    image = models.ImageField(upload_to='consignments/images/', verbose_name="รูปภาพทรัพย์")
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name="อัปโหลดเมื่อ")

    class Meta:
        verbose_name = "รูปภาพทรัพย์ฝากขาย"
        verbose_name_plural = "รูปภาพทรัพย์ฝากขาย"


class ConsignmentDeed(models.Model):
    consignment = models.ForeignKey(Consignment, on_delete=models.CASCADE, related_name='deeds', verbose_name="คำขอฝากขาย")
    deed_image = models.ImageField(upload_to='consignments/deeds/', verbose_name="เอกสารโฉนด (ลับ/ตรวจภายใน)")
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name="อัปโหลดเมื่อ")

    class Meta:
        verbose_name = "เอกสารโฉนด (ซ่อนลับ)"
        verbose_name_plural = "เอกสารโฉนด (ซ่อนลับ)"


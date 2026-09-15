import builtins
from django.db import models
from django.contrib.auth import get_user_model
from properties.models import Category, Location, Property
from config.models_soft_delete import SoftDeleteMixin

User = get_user_model()

class Lead(SoftDeleteMixin, models.Model):
    LEAD_TYPE_CHOICES = [
        ('BUYER', 'ผู้ซื้อ'),
        ('RENTER', 'ผู้เช่า'),
    ]
    STATUS_CHOICES = [
        ('NEW', 'ลีดใหม่'),
        ('CONTACTED', 'ติดต่อแล้ว'),
        ('MATCHED', 'เสนอทรัพย์แล้ว'),
        ('VIEWING', 'นัดเข้าชมทรัพย์'),
        ('CLOSED_WON', 'ปิดการขาย/เช่าสำเร็จ'),
        ('CLOSED_LOST', 'ยกเลิก/ไม่สนใจ'),
    ]

    name = models.CharField(max_length=150, verbose_name="ชื่อลูกค้า/ลีด")
    phone = models.CharField(max_length=50, verbose_name="เบอร์โทรศัพท์")
    email = models.EmailField(null=True, blank=True, verbose_name="อีเมล")
    line_id = models.CharField(max_length=100, null=True, blank=True, verbose_name="LINE ID")
    
    lead_type = models.CharField(max_length=10, choices=LEAD_TYPE_CHOICES, default='BUYER', verbose_name="ประเภทลีด")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='NEW', verbose_name="สถานะลีด")

    # Criteria for Auto-Matching Engine
    categories = models.ManyToManyField(Category, blank=True, related_name='interested_leads', verbose_name="หมวดหมู่อสังหาฯ ที่สนใจ")
    locations = models.ManyToManyField(Location, blank=True, related_name='interested_leads', verbose_name="ทำเลที่สนใจ")
    budget_min = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, verbose_name="งบขั้นต่ำ (บาท)")
    budget_max = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, verbose_name="งบสูงสุด (บาท)")
    min_bedrooms = models.PositiveIntegerField(null=True, blank=True, verbose_name="จำนวนห้องนอนขั้นต่ำ")
    min_usable_size = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True, verbose_name="พื้นที่ใช้สอยขั้นต่ำ (ตร.ม.)")
    
    notes = models.TextField(null=True, blank=True, verbose_name="หมายเหตุเพิ่มเติม")
    assigned_agent = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='crm_leads', verbose_name="นายหน้าผู้รับผิดชอบ")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="สร้างเมื่อ")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="แก้ไขล่าสุด")

    class Meta:
        verbose_name = "ลีดความต้องการลูกค้า (Lead)"
        verbose_name_plural = "ลีดความต้องการลูกค้า (Leads)"
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.get_lead_type_display()}] คุณ {self.name} - {self.phone}"


class LeadMatch(models.Model):
    STATUS_CHOICES = [
        ('SUGGESTED', 'ระบบแนะนำ'),
        ('SENT', 'เสนอทรัพย์ให้ลูกค้าแล้ว'),
        ('INTERESTED', 'ลูกค้าสนใจ'),
        ('REJECTED', 'ลูกค้าปฏิเสธ'),
    ]

    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name='matches', verbose_name="ลีด")
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='lead_matches', verbose_name="ทรัพย์สินที่จับคู่")
    match_score = models.PositiveIntegerField(default=0, verbose_name="คะแนนความแมตช์ (%)")
    match_reasons = models.JSONField(default=list, blank=True, verbose_name="เหตุผลความแมตช์ (JSON)")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='SUGGESTED', verbose_name="สถานะการเสนอทรัพย์")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="จับคู่เมื่อ")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="อัปเดตล่าสุด")

    class Meta:
        verbose_name = "ผลการจับคู่ทรัพย์สิน (Lead Match)"
        verbose_name_plural = "ผลการจับคู่ทรัพย์สิน (Lead Matches)"
        unique_together = ('lead', 'property')
        ordering = ['-match_score', '-created_at']

    def __str__(self):
        return f"{self.lead.name} <-> [{self.property.property_code}] {self.property.title} ({self.match_score}%)"


class Deal(SoftDeleteMixin, models.Model):
    DEAL_TYPE_CHOICES = [
        ('SALE', 'ซื้อขาย'),
        ('RENT', 'เช่า'),
    ]
    STAGE_CHOICES = [
        ('NEW_LEAD', '1. ลีดใหม่ (New Lead)'),
        ('QUALIFIED', '2. คัดกรองความต้องการ (Qualified)'),
        ('PROPOSED', '3. เสนอทรัพย์สิน (Proposed)'),
        ('VIEWING', '4. นัดเข้าชมทรัพย์สิน (Viewing Scheduled)'),
        ('NEGOTIATION', '5. อยู่ระหว่างเจรจาต่อรอง (Negotiation)'),
        ('CONTRACT', '6. ทำสัญญาซื้อขาย/เช่า (Contract Draft)'),
        ('CLOSED_WON', '7. ปิดการขายสำเร็จ (Closed Won)'),
        ('CLOSED_LOST', '8. ปิดดีลไม่สำเร็จ (Closed Lost)'),
    ]

    title = models.CharField(max_length=200, verbose_name="ชื่อดีล")
    lead = models.ForeignKey(Lead, on_delete=models.SET_NULL, null=True, blank=True, related_name='deals', verbose_name="ลูกค้า/ลีด")
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='deals', verbose_name="ทรัพย์สิน")
    agent = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='managed_deals', verbose_name="นายหน้าผู้ดูแลดีล")
    
    deal_type = models.CharField(max_length=10, choices=DEAL_TYPE_CHOICES, default='SALE', verbose_name="ประเภทดีล")
    stage = models.CharField(max_length=20, choices=STAGE_CHOICES, default='NEW_LEAD', verbose_name="ขั้นตอนใน Pipeline")

    # Financial & Commission Calculations
    agreed_price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="ราคาตกลงซื้อขาย/เช่า (บาท)")
    commission_rate = models.DecimalField(max_digits=5, decimal_places=2, default=3.00, verbose_name="อัตราค่าคอมมิชชัน (%)")
    commission_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="ยอดค่าคอมมิชชันรวม (บาท)")
    company_share = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="ส่วนแบ่งบริษัท (บาท)")
    agent_share = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="ส่วนแบ่งนายหน้า (บาท)")

    expected_close_date = models.DateField(null=True, blank=True, verbose_name="คาดว่าจะปิดดีลเมื่อ")
    actual_close_date = models.DateField(null=True, blank=True, verbose_name="ปิดดีลจริงเมื่อ")
    notes = models.TextField(null=True, blank=True, verbose_name="หมายเหตุดีล")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="สร้างดีลเมื่อ")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="อัปเดตล่าสุด")

    class Meta:
        verbose_name = "ดีลการขาย/เช่า (Deal)"
        verbose_name_plural = "บอร์ดดีลการขาย/เช่า (Deals Pipeline)"
        ordering = ['-updated_at']

    def save(self, *args, **kwargs):
        # Auto calculate commission
        if self.agreed_price and float(self.agreed_price) > 0:
            agreed = float(self.agreed_price)
            rate = float(self.commission_rate or 3.0)
            
            # 1. Total Commission Amount
            self.commission_amount = round((agreed * rate) / 100.0, 2)

            # 2. Default Split (50% Company, 50% Agent)
            if not self.company_share and not self.agent_share:
                half = round(self.commission_amount / 2.0, 2)
                self.company_share = half
                self.agent_share = half

        # Auto set actual_close_date if stage changed to CLOSED_WON
        if self.stage == 'CLOSED_WON' and not self.actual_close_date:
            from django.utils import timezone
            self.actual_close_date = timezone.now().date()

        super().save(*args, **kwargs)

    def __str__(self):
        return f"[{self.get_stage_display()}] {self.title} - ฿{self.agreed_price:,.0f}"


class ViewingAppointment(SoftDeleteMixin, models.Model):
    STATUS_CHOICES = [
        ('SCHEDULED', 'นัดหมายแล้ว'),
        ('COMPLETED', 'เข้าชมเรียบร้อย'),
        ('CANCELLED', 'ยกเลิกนัด'),
        ('NO_SHOW', 'ไม่มาตามนัด'),
    ]

    lead = models.ForeignKey(Lead, on_delete=models.SET_NULL, null=True, blank=True, related_name='appointments', verbose_name="ลูกค้า/ลีด")
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='appointments', verbose_name="ทรัพย์สินที่นัดชม")
    agent = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='managed_appointments', verbose_name="นายหน้าผู้ดูแล")
    
    appointment_datetime = models.DateTimeField(verbose_name="วัน-เวลานัดหมายเข้าชม")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='SCHEDULED', verbose_name="สถานะการนัดหมาย")
    
    client_rating = models.PositiveIntegerField(null=True, blank=True, verbose_name="คะแนนความพอใจลูกค้า (1-5 ดาว)")
    client_feedback = models.TextField(null=True, blank=True, verbose_name="คำวิจารณ์/Feedback จากลูกค้าหลังชม")
    notes = models.TextField(null=True, blank=True, verbose_name="หมายเหตุบันทึกนายหน้า")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="นัดเมื่อ")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="แก้ไขล่าสุด")

    class Meta:
        verbose_name = "ใบนัดเข้าชมทรัพย์สิน (Viewing Appointment)"
        verbose_name_plural = "ใบนัดเข้าชมทรัพย์สิน (Viewing Appointments)"
        ordering = ['-appointment_datetime']

    def __str__(self):
        return f"นัดชม [{self.property.property_code}] - {self.appointment_datetime.strftime('%d/%m/%Y %H:%M')}"


class LeaseAgreement(SoftDeleteMixin, models.Model):
    STATUS_CHOICES = [
        ('ACTIVE', 'สัญญาใช้งานอยู่'),
        ('EXPIRING_SOON', 'ใกล้หมดอายุ (ใน 30-60 วัน)'),
        ('EXPIRED', 'หมดอายุแล้ว'),
        ('TERMINATED', 'ยกเลิกสัญญาก่อนกำหนด'),
    ]

    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='lease_agreements', verbose_name="ทรัพย์สินให้เช่า")
    tenant_name = models.CharField(max_length=150, verbose_name="ชื่อผู้เช่า")
    tenant_phone = models.CharField(max_length=50, verbose_name="เบอร์โทรศัพท์ผู้เช่า")
    tenant_email = models.EmailField(null=True, blank=True, verbose_name="อีเมลผู้เช่า")
    
    start_date = models.DateField(verbose_name="วันเริ่มสัญญาเช่า")
    end_date = models.DateField(verbose_name="วันสิ้นสุดสัญญาเช่า")
    monthly_rent = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="ค่าเช่ารายเดือน (บาท)")
    deposit_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, verbose_name="เงินประกัน (บาท)")
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACTIVE', verbose_name="สถานะสัญญา")
    notes = models.TextField(null=True, blank=True, verbose_name="หมายเหตุสัญญา")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="บันทึกเมื่อ")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="อัปเดตล่าสุด")

    class Meta:
        verbose_name = "สัญญาเช่าและผู้เช่า (Lease Agreement)"
        verbose_name_plural = "สัญญาเช่าและผู้เช่า (Lease Agreements)"
        ordering = ['end_date']

    @builtins.property
    def days_until_expiration(self):
        from django.utils import timezone
        if self.end_date:
            today = timezone.now().date()
            delta = (self.end_date - today).days
            return delta
        return None

    def save(self, *args, **kwargs):
        # Auto calculate status based on remaining days
        if self.end_date and self.status != 'TERMINATED':
            days = self.days_until_expiration
            if days is not None:
                if days <= 0:
                    self.status = 'EXPIRED'
                elif days <= 60:
                    self.status = 'EXPIRING_SOON'
                else:
                    self.status = 'ACTIVE'

        super().save(*args, **kwargs)

    def __str__(self):
        return f"สัญญาเช่า: คุณ {self.tenant_name} - [{self.property.property_code}] (หมด {self.end_date})"


class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('SUPER_ADMIN', 'ผู้ดูแลระบบสูงสุด (Super Admin)'),
        ('BRANCH_MANAGER', 'ผู้จัดการสาขา (Branch Manager)'),
        ('SENIOR_AGENT', 'นายหน้าอาวุโส (Senior Agent)'),
        ('JUNIOR_AGENT', 'นายหน้าทั่วไป (Junior Agent)'),
        ('LANDLORD', 'เจ้าของทรัพย์สิน/ผู้ฝากขาย (Landlord)'),
    ]

    BRANCH_CHOICES = [
        ('BANGKOK_HQ', 'สำนักงานใหญ่ กรุงเทพฯ'),
        ('PHUKET_BRANCH', 'สาขาภูเก็ต'),
        ('CHIANGMAI_BRANCH', 'สาขาเชียงใหม่'),
        ('PATTAYA_BRANCH', 'สาขาพัทยา'),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name='ผู้ใช้งาน'
    )
    role = models.CharField(
        max_length=30,
        choices=ROLE_CHOICES,
        default='JUNIOR_AGENT',
        verbose_name='บทบาท/ระดับสิทธิ์'
    )
    branch = models.CharField(
        max_length=50,
        choices=BRANCH_CHOICES,
        default='BANGKOK_HQ',
        verbose_name='สาขาประจำการ'
    )
    phone_number = models.CharField(max_length=50, blank=True, null=True, verbose_name='เบอร์โทรศัพท์ติดต่อ')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='สร้างเมื่อ')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='แก้ไขล่าสุด')

    class Meta:
        verbose_name = 'โปรไฟล์สิทธิ์ผู้ใช้งาน (User Profile & Role)'
        verbose_name_plural = 'โปรไฟล์สิทธิ์ผู้ใช้งาน (User Profiles & Roles)'

    def __str__(self):
        return f"{self.user.username} - [{self.get_role_display()}] ({self.get_branch_display()})"


from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.get_or_create(user=instance)
    else:
        if hasattr(instance, 'profile') and instance.profile:
            instance.profile.save()


class Document(models.Model):
    DOCUMENT_TYPES = [
        ('DEED', 'เอกสารโฉนดที่ดิน'),
        ('CONTRACT', 'สัญญาเช่า / สัญญาซื้อขาย'),
        ('ID_CARD', 'สำเนาบัตรประชาชน / พาสปอร์ต'),
        ('POWER_OF_ATTORNEY', 'หนังสือมอบอำนาจ'),
        ('OTHER', 'เอกสารประกอบอื่น ๆ'),
    ]

    title = models.CharField(max_length=200, verbose_name="ชื่อเอกสาร")
    document_type = models.CharField(max_length=30, choices=DOCUMENT_TYPES, default='CONTRACT', verbose_name="ประเภทเอกสาร")
    file = models.FileField(upload_to='documents/%Y/%m/', verbose_name="ไฟล์เอกสาร")
    
    deal = models.ForeignKey(Deal, on_delete=models.SET_NULL, null=True, blank=True, related_name='documents', verbose_name="ดีลการขาย/เช่า")
    property = models.ForeignKey(Property, on_delete=models.SET_NULL, null=True, blank=True, related_name='documents', verbose_name="ทรัพย์สิน")
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='uploaded_documents', verbose_name="อัปโหลดโดย")
    
    notes = models.TextField(null=True, blank=True, verbose_name="หมายเหตุเอกสาร")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="อัปโหลดเมื่อ")

    class Meta:
        verbose_name = "คลังเอกสารและไฟล์แนบ (Document)"
        verbose_name_plural = "คลังเอกสารและไฟล์แนบ (Documents)"
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.get_document_type_display()}] {self.title}"



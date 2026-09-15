from django.contrib import admin, messages
from django.utils.text import slugify
from .models import Category, Location, Property, PropertyImage, Bookmark, Consignment, ConsignmentImage, ConsignmentDeed

class PropertyImageInline(admin.TabularInline):
    model = PropertyImage
    extra = 1

class ConsignmentImageInline(admin.TabularInline):
    model = ConsignmentImage
    extra = 0

class ConsignmentDeedInline(admin.TabularInline):
    model = ConsignmentDeed
    extra = 0
    verbose_name = "เอกสารโฉนด (ลับ)"
    verbose_name_plural = "เอกสารโฉนด (ลับ)"

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ('property_code', 'title', 'price', 'property_type', 'category', 'location', 'completeness_score_badge', 'status', 'agent')
    list_filter = ('property_type', 'category', 'location', 'status', 'agent')
    search_fields = ('title', 'property_code', 'description')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [PropertyImageInline]
    actions = ['export_as_excel', 'generate_banner_action', 'generate_ai_seo_action']

    @admin.action(description='📊 ส่งออกรายงาน Excel (.xlsx) สรุปอสังหาริมทรัพย์')
    def export_as_excel(self, request, queryset):
        from crm.utils_reports import export_properties_excel
        return export_properties_excel(queryset)

    @admin.action(description='สร้างรูปปกโปรโมต Banner อัตโนมัติ (Generate Cover Banner)')
    def generate_banner_action(self, request, queryset):
        from .utils_banner import generate_cover_banner
        count = 0
        for prop in queryset:
            cover_img = prop.images.filter(is_cover=True).first() or prop.images.first()
            if cover_img and cover_img.image:
                banner_file = generate_cover_banner(
                    image_file=cover_img.image,
                    title=prop.title,
                    price=prop.price,
                    property_code=prop.property_code,
                    property_type_display=prop.get_property_type_display()
                )
                # Unset previous cover images
                prop.images.filter(is_cover=True).update(is_cover=False)
                # Create new cover banner image
                banner_img = PropertyImage(
                    property=prop,
                    image=banner_file,
                    is_cover=True
                )
                banner_img._watermarked = True # Avoid double watermarking
                banner_img.save()
                count += 1
        self.message_user(request, f"สร้าง Banner รูปปกโปรโมตสำเร็จ {count} รายการ", messages.SUCCESS)

    @admin.action(description='ให้ AI ร่างข้อความประกาศ + SEO อัตโนมัติ (Generate AI Description & SEO)')
    def generate_ai_seo_action(self, request, queryset):
        from .utils_ai import generate_ai_seo_and_description
        count = 0
        for prop in queryset:
            ai_package = generate_ai_seo_and_description(prop)
            prop.description = ai_package['ai_description']
            if not isinstance(prop.features, dict):
                prop.features = {}
            prop.features['seo_package'] = ai_package
            prop.save()
            count += 1
        self.message_user(request, f"ให้ AI สร้างรายละเอียดและแพ็กเกจ SEO สำเร็จ {count} รายการ", messages.SUCCESS)

    @admin.display(description="คะแนนความสมบูรณ์")
    def completeness_score_badge(self, obj):
        from django.utils.html import format_html
        result = obj.calculate_completeness_score()
        score = result['score']
        
        if score >= 90:
            color = "#16a34a" # green
            label = "สมบูรณ์สูง"
        elif score >= 70:
            color = "#d97706" # amber
            label = "ปานกลาง"
        else:
            color = "#dc2626" # red
            label = "ต้องเพิ่มข้อมูล"
            
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 12px; font-weight: bold; font-size: 11px;">{}% ({})</span>',
            color, score, label
        )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(agent=request.user)

    def get_fields(self, request, obj=None):
        fields = super().get_fields(request, obj)
        if not request.user.is_superuser and 'agent' in fields:
            fields.remove('agent')
        return fields

    def save_model(self, request, obj, form, change):
        if not request.user.is_superuser:
            obj.agent = request.user
        elif not obj.agent:
            obj.agent = request.user

        # 1. Quality Control: Completeness Check before Publishing
        res = obj.calculate_completeness_score()
        if obj.status == 'PUBLISHED' and res['score'] < 90:
            missing_str = ", ".join(res['missing'])
            messages.warning(
                request,
                f"เตือนคุณภาพประกาศ: คะแนนความสมบูรณ์ปัจจุบันคือ {res['score']}% (ขั้นต่ำ 90%) "
                f"ข้อมูลที่ยังขาด: [{missing_str}] ระบบได้ปรับสถานะเป็น 'ร่าง (DRAFT)' ไว้ชั่วคราว"
            )
            obj.status = 'DRAFT'

        # 2. Duplicate Detection Warning
        duplicates = obj.check_duplicate()
        if duplicates:
            dup_codes = ", ".join([d.property_code for d in duplicates])
            messages.info(
                request,
                f"ตรวจพบประกาศที่อาจซ้ำกันในระบบ: รหัส [{dup_codes}] กรุณาตรวจสอบตำแหน่งแผนที่หรือชื่อประกาศ"
            )

        super().save_model(request, obj, form, change)


@admin.register(Bookmark)
class BookmarkAdmin(admin.ModelAdmin):
    list_display = ('user', 'property', 'created_at')
    list_filter = ('user', 'created_at')
    search_fields = ('user__username', 'property__title', 'property__property_code')


@admin.register(Consignment)
class ConsignmentAdmin(admin.ModelAdmin):
    list_display = ('owner_name', 'owner_phone', 'property_type', 'target_price', 'province', 'district', 'status', 'created_at')
    list_filter = ('property_type', 'status', 'province', 'created_at')
    search_fields = ('owner_name', 'owner_phone', 'owner_email', 'project_name', 'province', 'district')
    inlines = [ConsignmentImageInline, ConsignmentDeedInline]
    actions = ['convert_to_property']

    @admin.action(description='แปลงรายการฝากขายที่เลือกเป็นประกาศหลัก (Convert to Property)')
    def convert_to_property(self, request, queryset):
        converted_count = 0
        for consignment in queryset:
            # Match or create category
            cat_name = consignment.get_property_type_display()
            category, _ = Category.objects.get_or_create(
                name=cat_name,
                defaults={'slug': slugify(consignment.property_type, allow_unicode=True)}
            )
            
            # Match or create location
            loc_name = f"{consignment.district}, {consignment.province}"
            location, _ = Location.objects.get_or_create(
                name=loc_name,
                defaults={'slug': slugify(loc_name, allow_unicode=True)}
            )

            title = f"{consignment.get_property_type_display()} {consignment.project_name or consignment.district} {consignment.province}"
            
            # Build description
            desc_lines = [
                f"ประกาศฝากขายโดยคุณ {consignment.owner_name}",
                f"ทำเลที่ตั้ง: {consignment.subdistrict} {consignment.district} {consignment.province}",
            ]
            if consignment.highlights:
                desc_lines.append(f"จุดเด่น: {consignment.highlights}")
            if consignment.nearby_places:
                desc_lines.append(f"สถานที่ใกล้เคียง: {consignment.nearby_places}")

            description = "\n".join(desc_lines)

            # Create Property instance (property_code will auto-generate on save!)
            property_obj = Property.objects.create(
                title=title,
                description=description,
                price=consignment.target_price,
                property_type='SALE',
                category=category,
                location=location,
                google_maps_link=consignment.google_maps_link,
                direction=consignment.direction or '',
                furniture=consignment.furniture or '',
                status='PUBLISHED',
                agent=request.user,
                features=consignment.specs or {}
            )

            # Copy ConsignmentImage to PropertyImage
            for c_img in consignment.images.all():
                PropertyImage.objects.create(
                    property=property_obj,
                    image=c_img.image
                )

            # Update Consignment status
            consignment.status = 'APPROVED'
            consignment.save()
            converted_count += 1

        self.message_user(request, f"แปลงคำขอฝากขายเป็นประกาศหลักสำเร็จ {converted_count} รายการ", messages.SUCCESS)




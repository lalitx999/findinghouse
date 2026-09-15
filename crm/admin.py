from django.contrib import admin, messages
from django.utils.html import format_html
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth import get_user_model
from crm.models import Lead, LeadMatch, Deal, ViewingAppointment, LeaseAgreement, UserProfile, Document
from crm.services import run_lead_auto_matching

User = get_user_model()

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'โปรไฟล์สิทธิ์ผู้ใช้งาน (Role & Profile)'
    fields = ('role', 'branch', 'phone_number')

try:
    admin.site.unregister(User)
except admin.sites.NotRegistered:
    pass

@admin.register(User)
class CustomUserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'get_role_badge', 'get_branch', 'is_staff', 'is_active')

    def get_role_badge(self, obj):
        if hasattr(obj, 'profile') and obj.profile:
            role_display = obj.profile.get_role_display()
            role_key = obj.profile.role
            colors = {
                'SUPER_ADMIN': '#dc2626',
                'BRANCH_MANAGER': '#2563eb',
                'SENIOR_AGENT': '#059669',
                'JUNIOR_AGENT': '#d97706',
                'LANDLORD': '#7c3aed',
            }
            color = colors.get(role_key, '#64748b')
            return format_html(
                '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 12px; font-weight: bold; font-size: 11px;">{}</span>',
                color, role_display
            )
        return format_html('<span style="background-color: #64748b; color: white; padding: 3px 8px; border-radius: 12px; font-size: 11px;">ลูกค้าทั่วไป</span>')
    get_role_badge.short_description = "บทบาท/สิทธิ์"

    def get_branch(self, obj):
        if hasattr(obj, 'profile') and obj.profile:
            return obj.profile.get_branch_display()
        return "-"
    get_branch.short_description = "สาขา"

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'document_type', 'deal', 'property', 'uploaded_by', 'created_at')
    list_filter = ('document_type', 'created_at')
    search_fields = ('title', 'deal__title', 'property__title', 'property__property_code', 'notes')

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role_badge', 'branch', 'phone_number', 'updated_at')
    list_filter = ('role', 'branch')
    search_fields = ('user__username', 'user__email', 'phone_number')

    def role_badge(self, obj):
        colors = {
            'SUPER_ADMIN': '#dc2626',      # Red
            'BRANCH_MANAGER': '#2563eb',   # Blue
            'SENIOR_AGENT': '#059669',     # Emerald
            'JUNIOR_AGENT': '#d97706',     # Amber
            'LANDLORD': '#7c3aed',         # Purple
        }
        color = colors.get(obj.role, '#64748b')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 12px; font-weight: bold; font-size: 11px;">{}</span>',
            color, obj.get_role_display()
        )
    role_badge.short_description = "บทบาท/ระดับสิทธิ์"

class LeadMatchInline(admin.TabularInline):
    model = LeadMatch
    extra = 0
    readonly_fields = ('property', 'match_score_badge', 'status', 'created_at')
    fields = ('property', 'match_score_badge', 'status', 'created_at')
    can_delete = True

    @admin.display(description="คะแนน Match (%)")
    def match_score_badge(self, obj):
        score = obj.match_score
        color = "#16a34a" if score >= 80 else "#d97706" if score >= 60 else "#64748b"
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 12px; font-weight: bold; font-size: 11px;">{}%</span>',
            color, score
        )

class SoftDeleteAdminMixin:
    actions = ['restore_selected']

    def get_queryset(self, request):
        return self.model.all_objects.all()

    @admin.action(description="♻️ กู้คืนรายการที่ถูกลบ (Restore Soft-Deleted Items)")
    def restore_selected(self, request, queryset):
        count = 0
        for obj in queryset:
            if getattr(obj, 'is_deleted', False):
                obj.restore()
                count += 1
        self.message_user(request, f"กู้คืนข้อมูลสำเร็จทั้งหมด {count} รายการ", messages.SUCCESS)


@admin.register(Lead)
class LeadAdmin(SoftDeleteAdminMixin, admin.ModelAdmin):
    list_display = ('name', 'phone', 'lead_type', 'status', 'budget_display', 'assigned_agent', 'is_deleted', 'created_at')
    list_filter = ('is_deleted', 'lead_type', 'status', 'categories', 'locations', 'assigned_agent')
    search_fields = ('name', 'phone', 'email', 'line_id', 'notes')
    filter_horizontal = ('categories', 'locations')
    inlines = [LeadMatchInline]
    actions = ['run_auto_matching_action', 'restore_selected']

    @admin.display(description="งบประมาณ")
    def budget_display(self, obj):
        if obj.budget_min and obj.budget_max:
            return f"฿{obj.budget_min:,.0f} - ฿{obj.budget_max:,.0f}"
        elif obj.budget_max:
            return f"ไม่เกิน ฿{obj.budget_max:,.0f}"
        elif obj.budget_min:
            return f"ขั้นต่ำ ฿{obj.budget_min:,.0f}"
        return "ไม่ระบุ"

    @admin.action(description='ประมวลผลจับคู่ทรัพย์สินอัตโนมัติ (Run Auto-Matching Engine)')
    def run_auto_matching_action(self, request, queryset):
        total_matches = 0
        for lead in queryset:
            count = run_lead_auto_matching(lead)
            total_matches += count
        self.message_user(request, f"ประมวลผล Auto-Matching สำเร็จ พบทรัพย์สินตรงตามเงื่อนไขทั้งหมด {total_matches} รายการ", messages.SUCCESS)

@admin.register(LeadMatch)
class LeadMatchAdmin(admin.ModelAdmin):
    list_display = ('lead', 'property', 'match_score_badge', 'status', 'created_at')
    list_filter = ('status', 'match_score', 'created_at')
    search_fields = ('lead__name', 'lead__phone', 'property__title', 'property__property_code')

    @admin.display(description="คะแนน Match (%)")
    def match_score_badge(self, obj):
        score = obj.match_score
        color = "#16a34a" if score >= 80 else "#d97706" if score >= 60 else "#64748b"
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 12px; font-weight: bold; font-size: 11px;">{}%</span>',
            color, score
        )


from crm.utils_excel import export_deals_to_excel

@admin.register(Deal)
class DealAdmin(SoftDeleteAdminMixin, admin.ModelAdmin):
    list_display = ('title', 'deal_type', 'stage_badge', 'agreed_price_display', 'commission_display', 'agent', 'is_deleted', 'updated_at')
    list_filter = ('is_deleted', 'deal_type', 'stage', 'agent', 'created_at')
    search_fields = ('title', 'lead__name', 'property__title', 'property__property_code', 'notes')
    readonly_fields = ('commission_amount', 'company_share', 'agent_share', 'created_at', 'updated_at')
    actions = ['restore_selected', 'export_excel_action']

    @admin.action(description="📊 ส่งออกรายงานเป็นไฟล์ Excel (.xlsx)")
    def export_excel_action(self, request, queryset):
        return export_deals_to_excel(queryset)

    @admin.display(description="ขั้นตอน Pipeline")
    def stage_badge(self, obj):
        color = "#1e293b"
        if obj.stage == 'CLOSED_WON':
            color = "#16a34a" # green
        elif obj.stage == 'CLOSED_LOST':
            color = "#dc2626" # red
        elif obj.stage in ['NEGOTIATION', 'CONTRACT']:
            color = "#2563eb" # blue
        elif obj.stage in ['PROPOSED', 'VIEWING']:
            color = "#d97706" # amber

        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 10px; border-radius: 12px; font-weight: bold; font-size: 11px;">{}</span>',
            color, obj.get_stage_display()
        )

    @admin.display(description="ราคาตกลง (บาท)")
    def agreed_price_display(self, obj):
        return f"฿{obj.agreed_price:,.0f}" if obj.agreed_price else "-"

    @admin.display(description="ค่าคอมมิชชันรวม")
    def commission_display(self, obj):
        if obj.commission_amount:
            return format_html(
                '<strong style="color: #16a34a;">฿{:,.0f}</strong> <span style="font-size: 10px; color: #64748b;">({}%)</span>',
                obj.commission_amount, obj.commission_rate
            )
        return "-"


@admin.register(ViewingAppointment)
class ViewingAppointmentAdmin(SoftDeleteAdminMixin, admin.ModelAdmin):
    list_display = ('appointment_datetime', 'property', 'lead', 'agent', 'rating_display', 'status', 'is_deleted')
    list_filter = ('is_deleted', 'status', 'appointment_datetime', 'agent')
    search_fields = ('lead__name', 'lead__phone', 'property__title', 'property__property_code', 'client_feedback', 'notes')

    @admin.display(description="ดาว Rating")
    def rating_display(self, obj):
        if obj.client_rating:
            stars = "⭐" * min(obj.client_rating, 5)
            return format_html('<span style="color: #f59e0b; font-weight: bold;">{} ({} ดาว)</span>', stars, obj.client_rating)
        return "ยังไม่ประเมิน"


@admin.register(LeaseAgreement)
class LeaseAgreementAdmin(SoftDeleteAdminMixin, admin.ModelAdmin):
    list_display = ('tenant_name', 'tenant_phone', 'property', 'monthly_rent_display', 'start_date', 'end_date', 'status_badge', 'is_deleted')
    list_filter = ('is_deleted', 'status', 'start_date', 'end_date')
    search_fields = ('tenant_name', 'tenant_phone', 'tenant_email', 'property__title', 'property__property_code', 'notes')

    @admin.display(description="ค่าเช่า/เดือน")
    def monthly_rent_display(self, obj):
        return f"฿{obj.monthly_rent:,.0f}"

    @admin.display(description="สถานะสัญญาเช่า")
    def status_badge(self, obj):
        days = obj.days_until_expiration
        if obj.status == 'ACTIVE':
            color = "#16a34a" # green
            text = f"ใช้งานอยู่ ({days} วัน)" if days is not None else "ใช้งานอยู่"
        elif obj.status == 'EXPIRING_SOON':
            color = "#d97706" # amber warning
            text = f"ใกล้หมดอายุ (เหลือ {days} วัน)" if days is not None else "ใกล้หมดอายุ"
        elif obj.status == 'EXPIRED':
            color = "#dc2626" # red
            text = "หมดอายุแล้ว"
        else:
            color = "#64748b"
            text = obj.get_status_display()

        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 12px; font-weight: bold; font-size: 11px;">{}</span>',
            color, text
        )

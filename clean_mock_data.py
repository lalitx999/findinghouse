import os
import sys
import django

# Setup Django Environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from properties.models import Property, Consignment, Bookmark
from crm.models import Lead, Deal, ViewingAppointment, LeaseAgreement, Document
from inquiries.models import Inquiry
from reviews.models import CustomerReview
from chat.models import ChatRoom, ChatMessage
from audit.models import AuditLog, UserTwoFactorOTP, UserListingOTP

def safe_hard_delete(model_class):
    """
    Safely executes hard deletion for both standard models and SoftDelete models,
    handling both tuple return types (standard delete) and int return types (SoftDelete update).
    """
    try:
        if hasattr(model_class, 'all_objects'):
            manager = model_class.all_objects
        else:
            manager = model_class.objects

        qs = manager.all()
        if hasattr(qs, 'hard_delete'):
            result = qs.hard_delete()
        else:
            result = qs.delete()

        if isinstance(result, tuple):
            return result[0]
        elif isinstance(result, int):
            return result
        return 0
    except Exception as e:
        print(f"  ⚠️ Warning while cleaning {model_class.__name__}: {e}")
        return 0

def clean_data():
    print("=" * 60)
    print("🧹 [Finding House] สคริปต์ล้างข้อมูลทดสอบ (Clean Slate Tool)")
    print("=" * 60)
    print("ข้อมูลที่จะถูกลบ:")
    print(" - ประกาศอสังหาริมทรัพย์ทดสอบทั้งหมด (Properties & Images)")
    print(" - คำขอฝากขายทรัพย์ทดสอบ (Consignments & Deeds)")
    print(" - ลีดลูกค้าและดีลการขายทั้งหมด (Leads, Matches, Deals)")
    print(" - ใบนัดชมและสัญญาเช่า (Appointments & Lease Agreements)")
    print(" - ข้อความสอบถาม (Inquiries)")
    print(" - รีวิวลูกค้าทดสอบ (Customer Reviews)")
    print(" - ห้องแชทและข้อความทดสอบ (Chat Rooms & Messages)")
    print(" - ประวัติ OTP ทดสอบ")
    print("-" * 60)
    print("ข้อมูลที่จะถูกเก็บรักษาไว้ (ไม่ถูกลบ):")
    print(" ✅ บัญชีผู้ใช้งานระบบและ Super Admin (Users & Profiles)")
    print(" ✅ หมวดหมู่อสังหาฯ หลัก (Categories เช่น คอนโด, บ้าน, ที่ดิน)")
    print(" ✅ ทำเลที่ตั้งหลัก (Locations เช่น สุขุมวิท, พัทยา, ฯลฯ)")
    print(" ✅ บทความให้ความรู้ (Articles)")
    print("=" * 60)

    confirm = input("⚠️ คุณต้องการล้างข้อมูลทดสอบจริงหรือไม่? พิมพ์ 'CONFIRM' เพื่อดำเนินการ: ")
    if confirm.strip() != "CONFIRM":
        print("❌ ยกเลิกการทำงาน ข้อมูลทั้งหมดปลอดภัยเหมือนเดิมครับ")
        return

    print("\n⏳ กำลังล้างข้อมูลทดสอบ...")

    # 1. Chat
    c_msg = safe_hard_delete(ChatMessage)
    c_rooms = safe_hard_delete(ChatRoom)
    print(f" ✔️ ลบข้อความแชท {c_msg} รายการ, ห้องแชท {c_rooms} ห้อง")

    # 2. CRM
    c_deals = safe_hard_delete(Deal)
    c_appts = safe_hard_delete(ViewingAppointment)
    c_leases = safe_hard_delete(LeaseAgreement)
    c_docs = safe_hard_delete(Document)
    c_leads = safe_hard_delete(Lead)
    print(f" ✔️ ลบดีล {c_deals} รายการ, ใบนัดชม {c_appts} รายการ, สัญญาเช่า {c_leases} รายการ, ลีดลูกค้า {c_leads} รายการ")

    # 3. Consignments
    c_consign = safe_hard_delete(Consignment)
    print(f" ✔️ ลบคำขอฝากขายและโฉนดลับทดสอบ {c_consign} รายการ")

    # 4. Inquiries & Reviews
    c_inq = safe_hard_delete(Inquiry)
    c_rev = safe_hard_delete(CustomerReview)
    print(f" ✔️ ลบข้อความติดต่อสอบถาม {c_inq} รายการ, รีวิวทดสอบ {c_rev} รายการ")

    # 5. Properties & Bookmarks
    c_bm = safe_hard_delete(Bookmark)
    c_props = safe_hard_delete(Property)
    print(f" ✔️ ลบประกาศอสังหาริมทรัพย์และรูปภาพทดสอบ {c_props} รายการ")

    # 6. OTPs
    safe_hard_delete(UserTwoFactorOTP)
    safe_hard_delete(UserListingOTP)
    print(" ✔️ ล้างรหัส OTP ทดสอบเรียบร้อย")

    print("\n🎉 ล้างข้อมูลทดสอบเสร็จสมบูรณ์! ฐานข้อมูลสะอาด ปลอดภัย พร้อมนำเข้าข้อมูลจริง 100% แล้วครับ")

if __name__ == "__main__":
    clean_data()


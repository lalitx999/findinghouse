import os
import sys
import django

from dotenv import load_dotenv

# Setup Django Environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
if os.path.exists(env_path):
    load_dotenv(env_path)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from inquiries.models import Inquiry
from inquiries.utils_email import send_inquiry_notification_to_admin, send_auto_reply_to_customer

print("=== Testing Finding House Email System ===")

# Create a test inquiry object (in memory)
test_inquiry = Inquiry(
    id=999,
    name="ทดสอบ ระบบอีเมล",
    email="findinghousexxx123@gmail.com",
    phone="081-234-5678",
    message="ทดสอบการส่งอีเมลแจ้งเตือนสองทางจากระบบ Finding House"
)

print("1. Sending Admin Notification Email...")
admin_success = send_inquiry_notification_to_admin(test_inquiry)
print(f"   -> Result: {'SUCCESS' if admin_success else 'FAILED'}")

print("2. Sending Customer Auto-Reply Email...")
customer_success = send_auto_reply_to_customer(test_inquiry)
print(f"   -> Result: {'SUCCESS' if customer_success else 'FAILED'}")

print("=== Email Test Completed ===")

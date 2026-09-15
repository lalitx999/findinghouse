"""
Custom AdminSite — ลบ Django Admin default CSS/JS ออกทั้งหมด
และใช้ CoolAdmin theme แทน
"""

from django.contrib.admin import AdminSite
from django import forms


class CoolAdminSite(AdminSite):
    """
    Custom Admin Site ที่ override media เพื่อไม่ให้ Django inject
    adminlte, jazzmin, หรือ Django default admin CSS เข้ามา
    """
    site_header = "Finding House Admin"
    site_title = "Finding House Control Center"
    index_title = "แผงควบคุมระบบ"

    @property
    def media(self):
        """
        Override media property เพื่อ return empty media
        ไม่ต้องการ Django default admin CSS/JS เลย
        ทุกอย่างจัดการใน base.html ของเราแล้ว
        """
        return forms.Media()


# Singleton instance ที่ใช้แทน admin.site เดิม
cool_admin_site = CoolAdminSite(name='admin')

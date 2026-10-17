# Module: AdminLTE 3.1.0 Django Admin Integration (การผสาน AdminLTE เข้าสู่ Django Admin)

## ทำอะไร
- ทำการแทนที่ระบบแสดงผลของ Django Admin เดิม (`vault_admin`) ด้วยเทมเพลต **AdminLTE 3.1.0** เต็มรูปแบบ
- เชื่อมต่อเมนูนำทางใน Sidebar ครบทั้ง 7 กลุ่มงานของ Finding House พร้อมไอคอน FontAwesome
- สร้างหน้าแดชบอร์ดผู้บริหาร (`index.html`) ด้วยการ์ด Small-Box KPI (ยอดขาย, คอมมิชชัน 50/50, ลีด, ทรัพย์ในคลัง), Info-Boxes, Quick Action Hub และตารางรายการล่าสุด
- ปรับแต่งหน้าเข้าสู่ระบบ (`login.html`) ให้เป็นสไตล์ AdminLTE Modern Login Card
- เขียน CSS Bridge (`adminlte-django.css`) เพื่อเชื่อมต่อองค์ประกอบฟอร์มและตารางของ Django เข้ากับ Bootstrap 4 อย่างสวยงาม

## ทำไมถึงทำแบบนี้
- **เลือกวิธีนี้เพราะอะไร:**
  - ใช้ประโยชน์จากโฟลเดอร์แม่แบบ `AdminLTE-3.1.0/` ที่มีอยู่แล้วในโปรเจกต์ โดยคัดเลือกเฉพาะ Core Assets ที่จำเป็น (CSS, JS, FontAwesome, Bootstrap, jQuery) มาไว้ที่ static เพื่อลดขนาดโปรเจกต์ไม่ให้บวม
  - ควบคุมการแสดงผล HTML และการจัดกลุ่มเมนูของ Finding House ได้อย่างอิสระ 100%
  - สอดคล้องกับระบบ `admin_dashboard_stats` ใน `context_processors.py` ที่มีอยู่แล้ว สามารถนำค่าสถิติจริงมาเรนเดอร์ลงใน Small Boxes ได้ทันที
- **ทางเลือกอื่นที่คิดไว้คืออะไร:**
  - ติดตั้ง `django-jazzmin` (แพ็กเกจสำเร็จรูปของ AdminLTE 3) ซึ่งแม้จะสะดวกแต่อาจต้องลง library ภายนอกเพิ่ม และปรับแต่งวิดเจ็ตสถิติเชิงลึกได้จำกัดกว่าการเขียน Template Injection เอง

## โครงสร้างไฟล์
| ไฟล์ / โฟลเดอร์ | หน้าที่และการทำงาน |
|---|---|
| `backend/static/adminlte/` | เก็บ Core Assets ของ AdminLTE 3.1.0 (css, js, plugins/fontawesome, plugins/bootstrap, plugins/jquery, img) |
| `backend/static/adminlte/css/adminlte-django.css` | สไตล์ชีตเชื่อมประสานระหว่าง Django Admin Elements กับ Bootstrap 4 / AdminLTE |
| `backend/templates/admin/base.html` | Master Shell ของระบบ (Top Navbar, Sidebar 7 หมวดหมู่, User Panel, Breadcrumbs, Footer) |
| `backend/templates/admin/base_site.html` | ตัวเชื่อม Site Branding ของ Finding House |
| `backend/templates/admin/index.html` | หน้า Executive KPI Dashboard (Quick Hub, Small-box 4 กล่อง, Info-boxes, ตารางกิจกรรมล่าสุด) |
| `backend/templates/admin/login.html` | หน้าเข้าสู่ระบบสไตล์ AdminLTE 3 Login Box |
| `backend/config/settings.py` | ปรับปรุง `INSTALLED_APPS` โดยถอด `vault_admin` ออก เพื่อให้ระบบเรนเดอร์ AdminLTE เป็นหลัก |

## จุดที่ต้องระวัง
- **การทับซ้อนของ Block Content:** ใน `base.html` ป้ายแท็ก `{% block content %}` ต้องปรากฏเพียงครั้งเดียวเพื่อไม่ให้ติด `TemplateSyntaxError` แม้จะอยู่คนละเงื่อนไข `{% if is_popup %}` ก็ตาม
- **การทดสอบในสภาพแวดล้อมจริง:** ตรวจสอบให้แน่ใจว่าเว็บเบราว์เซอร์ล้างแคช (Hard Refresh: `Ctrl+F5` หรือ `Cmd+Shift+R`) เพื่อโหลด CSS/JS ของ AdminLTE ใหม่ทั้งหมด
- **การเพิ่มโมเดลในอนาคต:** หากมีการสร้างโมเดลใหม่ใน Django Apps สามารถเพิ่มลิงก์เมนูและไอคอนใน `backend/templates/admin/base.html` ในหมวดหมู่ที่เหมาะสมได้ทันที

## อ้างอิง
- แม่แบบต้นฉบับ: `AdminLTE-3.1.0` (Bootstrap 4 & AdminLTE Core)
- ฟอนต์: Google Font 'Prompt' สำหรับภาษาไทยและภาษาอังกฤษ
- รัฐธรรมนูญนักพัฒนา: `GEMINI.md` (The 19 Iron Rules)

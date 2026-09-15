import os
import sys
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.utils.text import slugify
from properties.models import Property, Location, Category

def seed_pattaya():
    print("Starting Pattaya Properties Seeding...")

    # 1. Ensure Categories exist
    cat_condo, _ = Category.objects.get_or_create(name="คอนโดมิเนียม", defaults={"slug": "condo"})
    cat_house, _ = Category.objects.get_or_create(name="บ้านเดี่ยว / พูลวิลล่า", defaults={"slug": "house"})
    cat_comm, _ = Category.objects.get_or_create(name="อาคารพาณิชย์", defaults={"slug": "commercial"})
    cat_land, _ = Category.objects.get_or_create(name="ที่ดิน", defaults={"slug": "land"})

    # 2. Ensure Pattaya Locations exist
    loc_north, _ = Location.objects.get_or_create(name="พัทยาเหนือ", defaults={"slug": "pattaya-north"})
    loc_central, _ = Location.objects.get_or_create(name="พัทยากลาง", defaults={"slug": "pattaya-central"})
    loc_south, _ = Location.objects.get_or_create(name="พัทยาใต้", defaults={"slug": "pattaya-south"})
    loc_wongamat, _ = Location.objects.get_or_create(name="วงศ์อมาตย์", defaults={"slug": "wongamat"})
    loc_jomtien, _ = Location.objects.get_or_create(name="นาจอมเทียน", defaults={"slug": "na-jomtien"})

    # 3. Data for 10 Pattaya Properties
    pattaya_data = [
        {
            "title": "คอนโดหรูติดหาดวงศ์อมาตย์ พัทยาเหนือ 2 ห้องนอน วิวทะเล 180 องศา",
            "price": 7500000.00,
            "property_type": "SALE",
            "category": cat_condo,
            "location": loc_north,
            "bedrooms": 2,
            "bathrooms": 2,
            "size_usable": 70.00,
            "floors": 28,
            "parking_spaces": 1,
            "direction": "ทิศตะวันตก",
            "furniture": "เฟอร์นิเจอร์ครบ (Fully Furnished)",
            "common_fee": 3500.00,
            "description": "ขายคอนโดหรูสไตล์รีสอร์ต พัทยาเหนือ-วงศ์อมาตย์ วิวทะเล 180 องศาเต็มตาจากระเบียง ห้องแต่งครบพร้อมเข้าอยู่ ส่วนกลางระดับพรีเมียม สระว่ายน้ำอินฟินิตี้เอจ ฟิตเนสลอยฟ้า และระบบรักษาความปลอดภัย 24 ชม.",
            "google_maps_link": "https://maps.google.com/?q=12.9550,100.8850",
            "landmarks": [
                {"name": "หาดวงศ์อมาตย์", "distance": "200 เมตร"},
                {"name": "ปราสาทสัจธรรม", "distance": "1.2 กม."},
                {"name": "เทอร์มินอล 21 พัทยา", "distance": "2.5 กม."}
            ],
            "features": {"wifi": True, "pool": True, "gym": True, "sea_view": True, "security_24h": True},
            "status": "PUBLISHED"
        },
        {
            "title": "พูลวิลล่าสไตล์โมเดิร์น พัทยาเหนือ 4 ห้องนอน สระว่ายน้ำส่วนตัวระบบเกลือ",
            "price": 18900000.00,
            "property_type": "SALE",
            "category": cat_house,
            "location": loc_north,
            "bedrooms": 4,
            "bathrooms": 5,
            "size_land": 120.00,
            "size_usable": 380.00,
            "floors": 2,
            "parking_spaces": 3,
            "direction": "ทิศเหนือ",
            "furniture": "บิวต์อินหรูทั้งหลัง",
            "common_fee": 4500.00,
            "description": "พูลวิลล่าหลังใหญ่พัทยาเหนือ ออกแบบสไตล์ Modern Luxury ดีไซน์โปร่งโถงสูง Double Volume สระว่ายน้ำส่วนตัวระบบเกลือขนาดใหญ่ เหมาะสำหรับอยู่อาศัยหรือปล่อยเช่าเป็นบ้านพักตากอากาศพรีเมียม",
            "google_maps_link": "https://maps.google.com/?q=12.9600,100.8900",
            "landmarks": [
                {"name": "หาดกระทิงลาย", "distance": "800 เมตร"},
                {"name": "โรงพยาบาลกรุงเทพพัทยา", "distance": "2.0 กม."},
                {"name": "มอเตอร์เวย์ สาย 7", "distance": "3.0 กม."}
            ],
            "features": {"private_pool": True, "smart_home": True, "garden": True, "cctv": True},
            "status": "PUBLISHED"
        },
        {
            "title": "คอนโดใจกลางเมืองพัทยากลาง ใกล้เซ็นทรัลเฟสติวัล 1 ห้องนอน ชั้นสูง",
            "price": 3450000.00,
            "property_type": "SALE",
            "category": cat_condo,
            "location": loc_central,
            "bedrooms": 1,
            "bathrooms": 1,
            "size_usable": 35.00,
            "floors": 18,
            "parking_spaces": 1,
            "direction": "ทิศใต้",
            "furniture": "ครบชุดพร้อมเครื่องใช้ไฟฟ้า",
            "common_fee": 1800.00,
            "description": "คอนโดทำเลฮอตพัทยากลาง เดินไปเซ็นทรัลพัทยาและชายหาดเพียง 5 นาที ห้องสวยสภาพใหม่ ไม่เคยปล่อยเช่า วิวเมืองและวิวทะเลระยิบระยับยามค่ำคืน การเดินทางสะดวกที่สุด",
            "google_maps_link": "https://maps.google.com/?q=12.9350,100.8880",
            "landmarks": [
                {"name": "เซ็นทรัลเฟสติวัล พัทยา บีช", "distance": "400 เมตร"},
                {"name": "ชายหาดพัทยากลาง", "distance": "500 เมตร"},
                {"name": "บิ๊กซี พัทยากลาง", "distance": "900 เมตร"}
            ],
            "features": {"rooftop_pool": True, "fitness": True, "keycard_access": True},
            "status": "PUBLISHED"
        },
        {
            "title": "อาคารพาณิชย์ 4 ชั้น พัทยากลาง ถนนสาย 3 ทำเลทองสำหรับค้าขายและออฟฟิศ",
            "price": 12000000.00,
            "property_type": "SALE",
            "category": cat_comm,
            "location": loc_central,
            "bedrooms": 3,
            "bathrooms": 4,
            "size_land": 24.00,
            "size_usable": 280.00,
            "floors": 4,
            "parking_spaces": 2,
            "direction": "ทิศตะวันออก",
            "furniture": "บางส่วน",
            "description": "ตึกแถวทำเลทองพัทยากลาง 3 สาย ติดถนนใหญ่ คนพลุกพล่านตลอดวัน เหมาะทำโชว์รูม คลินิก ร้านอาหาร คาเฟ่ หรือโฮสเทลเดินทางสะดวก จอดรถด้านหน้าและข้างตึกได้ง่าย",
            "google_maps_link": "https://maps.google.com/?q=12.9300,100.8950",
            "landmarks": [
                {"name": "ถนนพัทยาสาย 3", "distance": "0 เมตร"},
                {"name": "ตลาดบัวขาว", "distance": "600 เมตร"},
                {"name": "โรงพยาบาลพัทยาเมโมเรียล", "distance": "1.1 กม."}
            ],
            "features": {"commercial_zone": True, "road_frontage": True},
            "status": "PUBLISHED"
        },
        {
            "title": "ให้เช่าคอนโดหรู พัทยากลาง 1 ห้องนอน ชั้น 22 วิวพาโนรามา พร้อมเข้าอยู่",
            "price": 25000.00,
            "property_type": "RENT",
            "category": cat_condo,
            "location": loc_central,
            "bedrooms": 1,
            "bathrooms": 1,
            "size_usable": 38.00,
            "floors": 22,
            "parking_spaces": 1,
            "direction": "ทิศตะวันตก",
            "furniture": "บิวต์อินหรูครบชุด",
            "common_fee": 0.00,
            "deposit": 50000.00,
            "advance_payment": 25000.00,
            "minimum_lease": "สัญญา 1 ปีขึ้นไป",
            "description": "คอนโดให้เช่าพัทยากลาง ชั้น 22 วิวทะเลและตัวเมืองพัทยาสวยงาม ตกแต่งครบด้วยเครื่องใช้ไฟฟ้าคุณภาพสูง สมาร์ททีวี 55 นิ้ว ตู้เย็น เครื่องซักผ้า ไมโครเวฟ หิ้วกระเป๋าเข้าอยู่ได้เลย",
            "google_maps_link": "https://maps.google.com/?q=12.9380,100.8890",
            "landmarks": [
                {"name": "ห้างสรรพสินค้าฮาร์เบอร์ พัทยา", "distance": "700 เมตร"},
                {"name": "ฟู้ดแลนด์ พัทยากลาง", "distance": "800 เมตร"}
            ],
            "features": {"balcony": True, "washing_machine": True, "sea_view": True},
            "status": "PUBLISHED"
        },
        {
            "title": "พูลวิลล่าหรู พัทยาใต้ ใกล้เขาพระตระหนัก เหมาะลงทุนบ้านเช่ารายวัน/รายเดือน",
            "price": 15500000.00,
            "property_type": "SALE",
            "category": cat_house,
            "location": loc_south,
            "bedrooms": 5,
            "bathrooms": 6,
            "size_land": 100.00,
            "size_usable": 320.00,
            "floors": 2,
            "parking_spaces": 4,
            "direction": "ทิศใต้",
            "furniture": "จัดเต็มสไตล์วิลล่าปาร์ตี้",
            "description": "พูลวิลล่า 5 ห้องนอน พัทยาใต้-เขาพระตระหนัก พร้อมสระว่ายน้ำส่วนตัว สไลเดอร์ โต๊ะพูล ไฟเทค อุปกรณ์ปาร์ตี้ครบครัน มีสถิติปล่อยเช่ารายวันสร้างรายได้สม่ำเสมอ ยอดจองแน่นตลอดปี",
            "google_maps_link": "https://maps.google.com/?q=12.9150,100.8680",
            "landmarks": [
                {"name": "จุดชมวิวเขาพระตระหนัก", "distance": "1.0 กม."},
                {"name": "หาดยินยอม", "distance": "1.5 กม."},
                {"name": "ถนนคนเดิน Walking Street", "distance": "2.2 กม."}
            ],
            "features": {"pool_table": True, "bbq_area": True, "party_sound_system": True},
            "status": "PUBLISHED"
        },
        {
            "title": "คอนโดวิวทะเล พัทยาใต้ ใกล้ Walking Street และท่าเรือแหลมบาลีฮาย",
            "price": 4900000.00,
            "property_type": "SALE",
            "category": cat_condo,
            "location": loc_south,
            "bedrooms": 1,
            "bathrooms": 1,
            "size_usable": 48.00,
            "floors": 12,
            "parking_spaces": 1,
            "direction": "ทิศตะวันตกเฉียงใต้",
            "furniture": "ตกแต่งครบ",
            "common_fee": 2200.00,
            "description": "ขายคอนโดวิวทะเลพัทยาใต้ ขนาดใหญ่ 48 ตร.ม. มองเห็นวิวอ่าวพัทยาและเกาะล้าน ใกล้แหล่งท่องเที่ยวคึกคัก ใกล้ท่าเรือไปเกาะล้านเพียงนิดเดียว ซื้ออยู่อาศัยหรือปล่อยเช่าชาวต่างชาติได้ราคาดี",
            "google_maps_link": "https://maps.google.com/?q=12.9220,100.8720",
            "landmarks": [
                {"name": "ท่าเรือแหลมบาลีฮาย", "distance": "600 เมตร"},
                {"name": "ถนนคนเดิน Walking Street", "distance": "500 เมตร"},
                {"name": "เขาพระบาท พัทยา", "distance": "800 เมตร"}
            ],
            "features": {"sea_view": True, "gym": True, "swimming_pool": True},
            "status": "PUBLISHED"
        },
        {
            "title": "ที่ดินแปลงสวย พัทยาใต้ ใกล้แยกใต้ทำเลทอง เหมาะสร้างอพาร์ตเมนต์หรือโรงแรม",
            "price": 45000000.00,
            "property_type": "SALE",
            "category": cat_land,
            "location": loc_south,
            "size_land": 350.00,
            "description": "ขายที่ดินเปล่า พัทยาใต้ ขนาด 350 ตารางวา หน้ากว้างติดถนนสาธารณะ ทำเลสวยเป็นรูปสี่เหลี่ยมผืนผ้า บรรยากาศรอบข้างเดินทางสะดวก เข้าออกได้ทั้งถนนสาย 2 และสาย 3 เหมาะสร้างบูทีคโรงแรม อพาร์ตเมนต์ หรือพูลวิลล่า",
            "google_maps_link": "https://maps.google.com/?q=12.9180,100.8800",
            "landmarks": [
                {"name": "แยกพัทยาใต้", "distance": "400 เมตร"},
                {"name": "บิ๊กซี พัทยาใต้", "distance": "900 เมตร"},
                {"name": "ถนนสุขุมวิท", "distance": "1.2 กม."}
            ],
            "features": {"flat_land": True, "public_road": True},
            "status": "PUBLISHED"
        },
        {
            "title": "ให้เช่าคอนโด 2 ห้องนอน พัทยาเหนือ-นาเกลือ เฟอร์บิวต์อินครบ ลมดีมาก",
            "price": 35000.00,
            "property_type": "RENT",
            "category": cat_condo,
            "location": loc_north,
            "bedrooms": 2,
            "bathrooms": 2,
            "size_usable": 65.00,
            "floors": 15,
            "parking_spaces": 1,
            "direction": "ทิศเหนือ",
            "furniture": "บิวต์อินสไตล์นอร์ดิก",
            "deposit": 70000.00,
            "advance_payment": 35000.00,
            "minimum_lease": "สัญญา 1 ปี",
            "description": "คอนโดปล่อยเช่า 2 ห้องนอน พัทยาเหนือ-นาเกลือ บรรยากาศเงียบสงบเป็นส่วนตัว ลมโกรกดีตลอดวัน ตกแต่งโทนไม้อบอุ่นสบายตา เหมาะสำหรับครอบครัวหรือวัยทำงาน",
            "google_maps_link": "https://maps.google.com/?q=12.9650,100.8880",
            "landmarks": [
                {"name": "ตลาดอาหารทะเลนาเกลือ", "distance": "1.0 กม."},
                {"name": "มูลนิธิสว่างบริบูรณ์ฯ", "distance": "1.5 กม."}
            ],
            "features": {"bathtub": True, "quiet_area": True, "fitness": True},
            "status": "PUBLISHED"
        },
        {
            "title": "บ้านเดี่ยว 2 ชั้น พัทยาใต้-จอมเทียน สระส่วนตัว ใกล้หาดจอมเทียนเพียง 500 เมตร",
            "price": 9800000.00,
            "property_type": "SALE",
            "category": cat_house,
            "location": loc_jomtien,
            "bedrooms": 3,
            "bathrooms": 3,
            "size_land": 80.00,
            "size_usable": 220.00,
            "floors": 2,
            "parking_spaces": 2,
            "direction": "ทิศตะวันออกเฉียงเหนือ",
            "furniture": "แต่งครบพร้อมอยู่",
            "common_fee": 2500.00,
            "description": "บ้านเดี่ยว 2 ชั้น พัทยาใต้ ใกล้หาดจอมเทียนเดินไปทะเลได้ สภาพดีมาก พร้อมสระว่ายน้ำส่วนตัวและสวนร่มรื่น ตัวบ้านออกแบบเน้นรับแสงธรรมชาติ เงียบสงบ ปลอดภัย 24 ชั่วโมง",
            "google_maps_link": "https://maps.google.com/?q=12.8950,100.8750",
            "landmarks": [
                {"name": "หาดจอมเทียน", "distance": "500 เมตร"},
                {"name": "ตลาดไนท์มาร์เก็ตจอมเทียน", "distance": "1.1 กม."},
                {"name": "ร้านอาหารปูเพ็ญ", "distance": "2.0 กม."}
            ],
            "features": {"private_pool": True, "garden": True, "near_beach": True},
            "status": "PUBLISHED"
        }
    ]

    created_count = 0
    for data in pattaya_data:
        title = data["title"]
        prop, created = Property.objects.get_or_create(
            title=title,
            defaults=data
        )
        if created:
            created_count += 1
            print(f"Created Property: [{prop.property_code}] {prop.title}")

    print(f"Successfully seeded {created_count} Pattaya properties!")

if __name__ == "__main__":
    seed_pattaya()

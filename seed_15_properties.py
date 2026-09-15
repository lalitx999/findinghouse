import os
import sys
import django

# Setup Django Environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.utils.text import slugify
from properties.models import Property, Location, Category

def seed_properties():
    print("🚀 สตาร์ทสคริปต์เพิ่มข้อมูลทรัพย์ 15 รายการ (15 Unique Properties Seeding)...")

    # 1. สร้าง/ตรวจสอบ Categories
    cat_condo, _ = Category.objects.get_or_create(name="คอนโดมิเนียม", defaults={"slug": "condo"})
    cat_house, _ = Category.objects.get_or_create(name="บ้านเดี่ยว / พูลวิลล่า", defaults={"slug": "house"})
    cat_townhome, _ = Category.objects.get_or_create(name="ทาวน์โฮม / ทาวน์เฮาส์", defaults={"slug": "townhome"})
    cat_commercial, _ = Category.objects.get_or_create(name="อาคารพาณิชย์ / ตึกแถว", defaults={"slug": "commercial"})
    cat_land, _ = Category.objects.get_or_create(name="ที่ดิน", defaults={"slug": "land"})
    cat_warehouse, _ = Category.objects.get_or_create(name="โกดัง / โรงงาน", defaults={"slug": "warehouse"})

    # 2. สร้าง/ตรวจสอบ Locations
    locations = {}
    location_names = [
        ("สุขุมวิท - ทองหล่อ", "sukhumvit-thonglor"),
        ("สาทร - สีลม", "sathorn-silom"),
        ("อารีย์ - พญาไท", "aree-phayathai"),
        ("พระราม 9 - รัชดา", "rama9-ratchada"),
        ("บางนา - ศรีนครินทร์", "bangna-srinakarin"),
        ("เอกมัย - พระโขนง", "ekkamai-phra-khanong"),
        ("ราชพฤกษ์ - ปิ่นเกล้า", "ratchapruek-pinklao"),
        ("แจ้งวัฒนะ - ปากเกร็ด", "chaengwattana-pakkret"),
        ("รามอินทรา - ประดิษฐ์มนูธรรม", "ramintra-praditmanutham"),
        ("ปทุมวัน - สยาม", "pathumwan-siam"),
        ("ลาดพร้าว - โชคชัย 4", "ladprao-chokchai4"),
        ("บางซื่อ - เตาปูน", "bangsue-taopoon"),
        ("หัวหมาก - รามคำแหง", "huamark-ramkhamhaeng"),
        ("พระราม 2 - แสมดำ", "rama2-saemdam"),
        ("ตลิ่งชัน - พุทธมณฑล", "talingchan-phutthamonthon"),
    ]
    for name, slug in location_names:
        loc_obj, _ = Location.objects.get_or_create(name=name, defaults={"slug": slug})
        locations[slug] = loc_obj

    # 3. ข้อมูลอสังหาฯ 15 รายการไม่ซ้ำกัน
    properties_data = [
        {
            "title": "คอนโดหรู High-Rise สุขุมวิท 55 (ทองหล่อ) 2 ห้องนอน แต่งครบพร้อมสระว่ายน้ำลอยฟ้า",
            "price": 12500000.00,
            "property_type": "SALE",
            "category": cat_condo,
            "location": locations["sukhumvit-thonglor"],
            "bedrooms": 2,
            "bathrooms": 2,
            "size_usable": 68.50,
            "floors": 32,
            "parking_spaces": 1,
            "direction": "ทิศตะวันออก",
            "furniture": "เฟอร์นิเจอร์ครบ (Fully Furnished)",
            "pet_friendly": True,
            "common_fee": 4800.00,
            "description": "ขายคอนโดระดับ Luxury ใจกลางทองหล่อ ห้องตกแต่งครบสไตล์ Modern Luxury วิวเมืองพาโนรามา เดินทางสะดวกใกล้ BTS ทองหล่อ สิ่งอำนวยความสะดวกครบครัน สระว่ายน้ำ Rooftop infinity pool, ฟิตเนส และ EV Charger",
            "google_maps_link": "https://maps.google.com/?q=13.7324,100.5812",
            "landmarks": [
                {"name": "BTS ทองหล่อ", "distance": "450 เมตร"},
                {"name": "J Avenue Thonglor", "distance": "300 เมตร"},
                {"name": "โรงพยาบาลสมิติเวช สุขุมวิท", "distance": "800 เมตร"}
            ],
            "features": {"wifi": True, "pool": True, "gym": True, "ev_charger": True, "security_24h": True},
            "status": "PUBLISHED"
        },
        {
            "title": "คฤหาสน์หรู 3 ชั้น ปลูกสร้างเอง ย่านสาทร-สีลม สระว่ายน้ำส่วนตัว จอดรถได้ 6 คัน",
            "price": 68000000.00,
            "property_type": "SALE",
            "category": cat_house,
            "location": locations["sathorn-silom"],
            "bedrooms": 5,
            "bathrooms": 6,
            "size_land": 180.00,
            "size_usable": 650.00,
            "floors": 3,
            "parking_spaces": 6,
            "direction": "ทิศใต้",
            "furniture": "บิ้วท์อินพรีเมียม (Built-in)",
            "pet_friendly": True,
            "common_fee": 0.00,
            "description": "ขายบ้านเดี่ยวหรูย่านสาทร สไตล์ Modern Classic โครงสร้างแข็งแรง ใช้วัสดุนำเข้าเกรด A พร้อมลิฟต์โดยสารในบ้าน สระว่ายน้ำส่วนตัวระบบเกลือ ใกล้สถานทูตและย่านธุรกิจการเงินสาทร-สีลม",
            "google_maps_link": "https://maps.google.com/?q=13.7200,100.5300",
            "landmarks": [
                {"name": "BTS ช่องนนทรี", "distance": "700 เมตร"},
                {"name": "โรงพยาบาลกรุงเทพคริสเตียน", "distance": "1.2 กม."},
                {"name": "สวนลุมพินี", "distance": "1.5 กม."}
            ],
            "features": {"pool": True, "lift": True, "garden": True, "security_24h": True, "maid_room": True},
            "status": "PUBLISHED"
        },
        {
            "title": "ให้เช่า คอนโด อารีย์-พญาไท 1 ห้องนอน ห้องสวย ชั้นสูง วิวสระ พร้อมเข้าอยู่",
            "price": 22000.00,
            "property_type": "RENT",
            "category": cat_condo,
            "location": locations["aree-phayathai"],
            "bedrooms": 1,
            "bathrooms": 1,
            "size_usable": 38.00,
            "floors": 18,
            "parking_spaces": 1,
            "direction": "ทิศเหนือ",
            "furniture": "เฟอร์นิเจอร์ครบ (Fully Furnished)",
            "minimum_lease": "สัญญา 1 ปี",
            "deposit": 44000.00,
            "advance_payment": 22000.00,
            "move_in_date": "พร้อมเข้าอยู่ได้ทันที",
            "description": "ให้เช่าคอนโดอารีย์ 1 ห้องนอน ขนาด 38 ตร.ม. ตกแต่งครบ พร้อมเครื่องใช้ไฟฟ้าครบชุด (ทีวี ตู้เย็น ไมโครเวฟ เครื่องซักผ้า) ส่วนกลางมีสระว่ายน้ำ Co-Working Space ใกล้ BTS อารีย์",
            "google_maps_link": "https://maps.google.com/?q=13.7790,100.5440",
            "landmarks": [
                {"name": "BTS อารีย์", "distance": "350 เมตร"},
                {"name": "La Villa Ari", "distance": "300 เมตร"},
                {"name": "โรงพยาบาลพญาไท 2", "distance": "900 เมตร"}
            ],
            "features": {"wifi": True, "pool": True, "gym": True, "coworking": True},
            "status": "PUBLISHED"
        },
        {
            "title": "ทาวน์โฮม 3 ชั้น สไตล์โมเดิร์น ย่านพระราม 9 - รัชดา เหมาะทำโฮมออฟฟิศหรืออยู่อาศัย",
            "price": 8900000.00,
            "property_type": "SALE",
            "category": cat_townhome,
            "location": locations["rama9-ratchada"],
            "bedrooms": 3,
            "bathrooms": 4,
            "size_land": 28.50,
            "size_usable": 220.00,
            "floors": 3,
            "parking_spaces": 2,
            "direction": "ทิศตะวันตกเฉียงเหนือ",
            "furniture": "บางส่วน (Partly Furnished)",
            "common_fee": 1500.00,
            "description": "ขายทาวน์โฮม 3 ชั้น สภาพใหม่ ดีไซน์โปร่งโล่ง เพดานสูง Double Volume บริเวณห้องรับแขก ต่อเติมครัวหลังบ้านเรียบร้อย ทำเลดีเดินทางสะดวก เข้าออกได้ทั้งถนนพระราม 9 และรัชดาภิเษก",
            "google_maps_link": "https://maps.google.com/?q=13.7580,100.5690",
            "landmarks": [
                {"name": "MRT พระราม 9", "distance": "1.1 กม."},
                {"name": "Central Rama 9", "distance": "1.2 กม."},
                {"name": "Fortune Town", "distance": "1.0 กม."}
            ],
            "features": {"security_24h": True, "kitchen_extension": True, "aircon": True},
            "status": "PUBLISHED"
        },
        {
            "title": "บ้านเดี่ยว 2 ชั้น โครงการแบรนด์ดัง บางนา-ตราด กม. 7 ใกล้ เมกาบางนา และ สนามกอล์ฟ",
            "price": 15800000.00,
            "property_type": "SALE",
            "category": cat_house,
            "location": locations["bangna-srinakarin"],
            "bedrooms": 4,
            "bathrooms": 5,
            "size_land": 72.00,
            "size_usable": 280.00,
            "floors": 2,
            "parking_spaces": 3,
            "direction": "ทิศเหนือ",
            "furniture": "เฟอร์นิเจอร์บิ้วท์อิน",
            "common_fee": 2500.00,
            "description": "ขายบ้านเดี่ยวโครงการหรู บางนา กม. 7 สังคมคุณภาพ สงบร่มรื่น ฟังก์ชัน 4 ห้องนอน 5 ห้องน้ำ พร้อมห้องแม่บ้าน บ้านตำแหน่งดีหน้าสวนส่วนกลาง ระบบรักษาความปลอดภัยเข้มงวด 24 ชม.",
            "google_maps_link": "https://maps.google.com/?q=13.6550,100.6720",
            "landmarks": [
                {"name": "Mega Bangna", "distance": "1.5 กม."},
                {"name": "โรงเรียนนานาชาติคอนคอร์เดียน", "distance": "800 เมตร"},
                {"name": "สนามกอล์ฟเมืองแก้ว", "distance": "500 เมตร"}
            ],
            "features": {"clubhouse": True, "pool": True, "gym": True, "security_24h": True, "garden": True},
            "status": "PUBLISHED"
        },
        {
            "title": "ให้เช่า อาคารพาณิชย์ 4 ชั้น ติดถนนใหญ่ เอกมัย ทำเลทองเหมาะทำหน้าร้าน หรือ คาเฟ่",
            "price": 85000.00,
            "property_type": "RENT",
            "category": cat_commercial,
            "location": locations["ekkamai-phra-khanong"],
            "bedrooms": 2,
            "bathrooms": 4,
            "size_land": 22.00,
            "size_usable": 320.00,
            "floors": 4,
            "parking_spaces": 2,
            "direction": "ทิศตะวันตก",
            "minimum_lease": "สัญญา 3 ปี",
            "deposit": 255000.00,
            "advance_payment": 8500.00,
            "description": "ให้เช่าอาคารพาณิชย์ 4 ชั้น หน้ากว้าง 4.5 เมตร ติดถนนเอกมัย ปรับปรุงระบบไฟฟ้าและประปาใหม่หมด เหมาะทำโชว์รูม สถาบันความงาม คาเฟ่ ร้านอาหาร หรือออฟฟิศสำนักงาน ทำเลมีทราฟฟิกตลอดวัน",
            "google_maps_link": "https://maps.google.com/?q=13.7310,100.5880",
            "landmarks": [
                {"name": "BTS เอกมัย", "distance": "900 เมตร"},
                {"name": "Big C เอกมัย", "distance": "300 เมตร"},
                {"name": "Donki Mall Thonglor", "distance": "500 เมตร"}
            ],
            "features": {"street_front": True, "parking": True, "renovated": True},
            "status": "PUBLISHED"
        },
        {
            "title": "บ้านเดี่ยวหรู 2 ชั้น สไตล์นอร์ดิก ราชพฤกษ์-ปิ่นเกล้า แปลงมุม ที่ดินใหญ่ 95 ตร.วา",
            "price": 14900000.00,
            "property_type": "SALE",
            "category": cat_house,
            "location": locations["ratchapruek-pinklao"],
            "bedrooms": 4,
            "bathrooms": 4,
            "size_land": 95.00,
            "size_usable": 310.00,
            "floors": 2,
            "parking_spaces": 3,
            "direction": "ทิศใต้",
            "furniture": "แต่งครบสไตล์ Minimal Nordic",
            "common_fee": 3000.00,
            "description": "ขายบ้านเดี่ยวแปลงมุม โครงการติดถนนราชพฤกษ์ ดีไซน์ Nordic หลังคาทรงจั่วสูง เพดานห้องนอนใหญ่สูง 3.5 เมตร สวนกว้างขวางรอบบ้าน เดินทางเข้าเมืองสะดวกใกล้ทางด่วนศรีรัช",
            "google_maps_link": "https://maps.google.com/?q=13.7880,100.4450",
            "landmarks": [
                {"name": "The Crystal SB Ratchapruek", "distance": "1.2 กม."},
                {"name": "HomePro ราชพฤกษ์", "distance": "1.0 กม."},
                {"name": "ทางด่วนศรีรัช-วงแหวนรอบนอก", "distance": "2.0 กม."}
            ],
            "features": {"corner_plot": True, "garden": True, "clubhouse": True, "security_24h": True},
            "status": "PUBLISHED"
        },
        {
            "title": "ที่ดินผืนงาม 2 ไร่ ติดถนนแจ้งวัฒนะ เหมาะพัฒนาคอนโด หรือ อาคารสำนักงาน",
            "price": 160000000.00,
            "property_type": "SALE",
            "category": cat_land,
            "location": locations["chaengwattana-pakkret"],
            "bedrooms": None,
            "bathrooms": None,
            "size_land": 800.00,
            "size_usable": None,
            "floors": None,
            "parking_spaces": None,
            "direction": "ทิศตะวันออก",
            "description": "ขายที่ดินสวยผังสีแดง (พ.๕) ขนาด 2 ไร่ (800 ตร.วา) หน้ากว้างติดถนนแจ้งวัฒนะ 40 เมตร ลึก 80 เมตร ทำเลใกล้สถานีรถไฟฟ้าสายสีชมพู และศูนย์ราชการแจ้งวัฒนะ เหมาะสำหรับพัฒนารายโครงการหรือสร้างตึกสูง",
            "google_maps_link": "https://maps.google.com/?q=13.8900,100.5280",
            "landmarks": [
                {"name": "รถไฟฟ้าสายสีชมพู สถานีแจ้งวัฒนะ 14", "distance": "150 เมตร"},
                {"name": "ศูนย์ราชการแจ้งวัฒนะ", "distance": "1.5 กม."},
                {"name": "Central Chaengwattana", "distance": "2.0 กม."}
            ],
            "features": {"red_zone": True, "main_road_front": True, "train_station_near": True},
            "status": "PUBLISHED"
        },
        {
            "title": "ให้เช่า โกดัง/โรงงาน พร้อมออฟฟิศ 2 ชั้น ย่านรามอินทรา รถใหญ่คอนเทนเนอร์เข้า-ออกสะดวก",
            "price": 120000.00,
            "property_type": "RENT",
            "category": cat_warehouse,
            "location": locations["ramintra-praditmanutham"],
            "bedrooms": None,
            "bathrooms": 4,
            "size_land": 350.00,
            "size_usable": 850.00,
            "floors": 2,
            "parking_spaces": 10,
            "direction": "ทิศเหนือ",
            "minimum_lease": "สัญญา 2 ปี",
            "deposit": 360000.00,
            "advance_payment": 120000.00,
            "description": "ให้เช่าโกดังคลังสินค้าพร้อมสำนักงานปรับอากาศ 2 ชั้น พื้นรับน้ำหนักได้ 3 ตัน/ตร.ม. หลังคาเมทัลชีทพร้อมบุฉนวนกันความร้อน ระบบไฟฟ้า 3 เฟส 100A รถเทรลเลอร์และคอนเทนเนอร์ 40 ฟุต เข้า-ออกได้สะดวก",
            "google_maps_link": "https://maps.google.com/?q=13.8400,100.6400",
            "landmarks": [
                {"name": "ทางด่วนฉลองรัช (รามอินทรา-อาจณรงค์)", "distance": "1.8 กม."},
                {"name": "Fashion Island", "distance": "3.5 กม."}
            ],
            "features": {"three_phase_electric": True, "container_accessible": True, "office_attached": True},
            "status": "PUBLISHED"
        },
        {
            "title": "คอนโดระดับ Super Luxury ปทุมวัน-สยาม 3 ห้องนอน เพ้นท์เฮาส์ชั้นสูงสุด วิวราชกรีฑาสโมสร",
            "price": 45000000.00,
            "property_type": "SALE",
            "category": cat_condo,
            "location": locations["pathumwan-siam"],
            "bedrooms": 3,
            "bathrooms": 4,
            "size_usable": 185.00,
            "floors": 45,
            "parking_spaces": 3,
            "direction": "ทิศใต้",
            "furniture": "เฟอร์นิเจอร์แบรนด์เนมนำเข้า",
            "common_fee": 15000.00,
            "description": "ขายห้อง Penthouse สุดหรู คอนโดระดับ Ultimate Luxury ย่านปทุมวัน เพดานสูง 3.2 เมตร วิวพื้นที่สีเขียวราชกรีฑาสโมสร และวิวเมืองสยามสแควร์ ลิฟต์ส่วนตัวส่งถึงหน้าห้อง จอดรถ Fixed 3 คัน",
            "google_maps_link": "https://maps.google.com/?q=13.7430,100.5340",
            "landmarks": [
                {"name": "BTS สยาม", "distance": "500 เมตร"},
                {"name": "Siam Paragon", "distance": "400 เมตร"},
                {"name": "จุฬาลงกรณ์มหาวิทยาลัย", "distance": "800 เมตร"}
            ],
            "features": {"private_lift": True, "penthouse": True, "golf_view": True, "concierge": True},
            "status": "PUBLISHED"
        },
        {
            "title": "ทาวน์โฮม 2 ชั้น รีโนเวทใหม่ทั้งหลัง ลาดพร้าว - โชคชัย 4 พร้อมอยู่ ทำเลดีใกล้รถไฟฟ้าสายสีโกลด์/เหลือง",
            "price": 3950000.00,
            "property_type": "SALE",
            "category": cat_townhome,
            "location": locations["ladprao-chokchai4"],
            "bedrooms": 3,
            "bathrooms": 2,
            "size_land": 20.00,
            "size_usable": 130.00,
            "floors": 2,
            "parking_spaces": 1,
            "direction": "ทิศตะวันออก",
            "furniture": "ตกแต่งใหม่พร้อมเคาน์เตอร์ครัว",
            "description": "ขายทาวน์โฮม 2 ชั้น รีโนเวทใหม่สไตล์มินิมอล ทำระบบน้ำ-ไฟฟ้าใหม่ทั้งหมด เปลี่ยนกระเบื้อง สุขภัณฑ์ใหม่หมด ต่อเติมโรงจอดรถและครัวหลังบ้าน ทำเลดีมาก อยู่ซอยโชคชัย 4 เดินทางสะดวก",
            "google_maps_link": "https://maps.google.com/?q=13.7950,100.5920",
            "landmarks": [
                {"name": "รถไฟฟ้าสายสีเหลือง สถานีโชคชัย 4", "distance": "800 เมตร"},
                {"name": "ตลาดโชคชัย 4", "distance": "900 เมตร"},
                {"name": "โรงพยาบาลเปาโล โชคชัย 4", "distance": "600 เมตร"}
            ],
            "features": {"renovated": True, "ready_to_move": True, "kitchen_extension": True},
            "status": "PUBLISHED"
        },
        {
            "title": "คอนโด High-Rise ติดสถานีรถไฟฟ้า บางซื่อ-เตาปูน 1 ห้องนอน 32 ตร.ม. ชั้น 15 วิวแม่น้ำเจ้าพระยา",
            "price": 3100000.00,
            "property_type": "SALE",
            "category": cat_condo,
            "location": locations["bangsue-taopoon"],
            "bedrooms": 1,
            "bathrooms": 1,
            "size_usable": 32.00,
            "floors": 15,
            "parking_spaces": 1,
            "direction": "ทิศตะวันตก",
            "furniture": "เฟอร์นิเจอร์ครบ + เครื่องใช้ไฟฟ้า",
            "common_fee": 1600.00,
            "description": "ขายคอนโดติด MRT เตาปูน อินเตอร์เชนจ์ เชื่อมต่อสถานีกลางบางซื่อ ห้องแต่งสวย ครบครัน ทิศตะวันตกรับลมเห็นวิวแม่น้ำเจ้าพระยาไกลๆ เหมาะสำหรับอยู่อาศัยเอง หรือปล่อยเช่าให้พนักงานและข้าราชการ",
            "google_maps_link": "https://maps.google.com/?q=13.8060,100.5310",
            "landmarks": [
                {"name": "MRT สถานีเตาปูน Interchange", "distance": "100 เมตร"},
                {"name": "สถานีกลางกรุงเทพอภิวัฒน์ (บางซื่อ)", "distance": "1.5 กม."},
                {"name": "Gateway บางซื่อ", "distance": "700 เมตร"}
            ],
            "features": {"mrt_connected": True, "river_view": True, "pool": True, "gym": True},
            "status": "PUBLISHED"
        },
        {
            "title": "ให้เช่า บ้านเดี่ยว 2 ชั้น หลังใหญ่ หัวหมาก-รามคำแหง เหมาะทำออฟฟิศ หรือ สถาบันกวดวิชา",
            "price": 45000.00,
            "property_type": "RENT",
            "category": cat_house,
            "location": locations["huamark-ramkhamhaeng"],
            "bedrooms": 4,
            "bathrooms": 3,
            "size_land": 85.00,
            "size_usable": 260.00,
            "floors": 2,
            "parking_spaces": 4,
            "direction": "ทิศตะวันออกเฉียงเหนือ",
            "minimum_lease": "สัญญา 1 ปี",
            "deposit": 90000.00,
            "advance_payment": 45000.00,
            "description": "ให้เช่าบ้านเดี่ยว 2 ชั้น พื้นที่กว้างขวาง จอดรถได้ถึง 4 คัน ใกล้มหาวิทยาลัยรามคำแหง และ ABAC หัวหมาก ทำเลเข้าออกสะดวกได้ทั้งซอยรามคำแหง 24 และถนนหัวหมาก อนุญาตให้จดทะเบียนบริษัทได้",
            "google_maps_link": "https://maps.google.com/?q=13.7540,100.6220",
            "landmarks": [
                {"name": "มหาวิทยาลัยอัสสัมชัญ (ABAC หัวหมาก)", "distance": "600 เมตร"},
                {"name": "สนามราชมังคลากีฬาสถาน", "distance": "800 เมตร"},
                {"name": "Airport Rail Link หัวหมาก", "distance": "2.2 กม."}
            ],
            "features": {"company_registration_allowed": True, "spacious_parking": True, "aircon": True},
            "status": "PUBLISHED"
        },
        {
            "title": "ที่ดินถมแล้ว 1 ไร่ พระราม 2 ซอย 50 ใกล้เซ็นทรัลพระราม 2 เข้าซอยเพียง 300 เมตร",
            "price": 28000000.00,
            "property_type": "SALE",
            "category": cat_land,
            "location": locations["rama2-saemdam"],
            "bedrooms": None,
            "bathrooms": None,
            "size_land": 400.00,
            "size_usable": None,
            "floors": None,
            "parking_spaces": None,
            "direction": "ทิศเหนือ",
            "description": "ขายที่ดินสวย ถมแล้วเรียบร้อยระดับเดียวกับถนน เนื้อที่ 1 ไร่ (400 ตร.วา) ซอยพระราม 2 ซอย 50 ถนนกว้าง 8 เมตร รถสวนสะดวก ผังสีส้ม (ย.๖) เหมาะปลูกบ้านพักอาศัย สร้างสำนักงาน หรืออพาร์ตเมนต์",
            "google_maps_link": "https://maps.google.com/?q=13.6680,100.4380",
            "landmarks": [
                {"name": "Central พระราม 2", "distance": "1.0 กม."},
                {"name": "โรงพยาบาลนครธน", "distance": "1.2 กม."},
                {"name": "ทางด่วนพระราม 2", "distance": "2.5 กม."}
            ],
            "features": {"filled_land": True, "orange_zone": True, "wide_street": True},
            "status": "PUBLISHED"
        },
        {
            "title": "อาคารพาณิชย์ 3.5 ชั้น ตลิ่งชัน-พุทธมณฑล สาย 1 ทำเลริมถนนใหญ่ เหมาะเปิดคลินิก/โชว์รูม",
            "price": 7800000.00,
            "property_type": "SALE",
            "category": cat_commercial,
            "location": locations["talingchan-phutthamonthon"],
            "bedrooms": 3,
            "bathrooms": 3,
            "size_land": 24.00,
            "size_usable": 210.00,
            "floors": 4,
            "parking_spaces": 2,
            "direction": "ทิศตะวันออก",
            "furniture": "เปล่า (Unfurnished)",
            "description": "ขายตึกแถว/อาคารพาณิชย์ 3 ชั้นครึ่ง มีชั้นลอย ตึกสภาพดี โครงสร้างอิฐมอญแข็งแรง ติดถนนพุทธมณฑลสาย 1 ย่านตลิ่งชัน ทำเลค้าขายดีเยี่ยม ที่จอดรถหน้าตึกสะดวกสบาย",
            "google_maps_link": "https://maps.google.com/?q=13.7710,100.4180",
            "landmarks": [
                {"name": "สถานีรถไฟฟ้าสายสีแดง ตลิ่งชัน", "distance": "1.5 กม."},
                {"name": "ตลาดน้ำตลิ่งชัน", "distance": "2.0 กม."},
                {"name": "โรงพยาบาลธนบุรี 2", "distance": "3.5 กม."}
            ],
            "features": {"mezzanine": True, "main_road_front": True, "brick_structure": True},
            "status": "PUBLISHED"
        }
    ]

    # 4. สั่ง Save ลง Database
    created_count = 0
    updated_count = 0

    for item in properties_data:
        prop, created = Property.objects.update_or_create(
            title=item["title"],
            defaults=item
        )
        if created:
            created_count += 1
            print(f"  [+] เพิ่มทรัพย์ใหม่เรียบร้อย: [{prop.property_code}] {prop.title}")
        else:
            updated_count += 1
            print(f"  [*] อัปเดตข้อมูลทรัพย์เดิม: [{prop.property_code}] {prop.title}")

    print(f"\n✅ เสร็จสิ้น! เพิ่มทรัพย์ใหม่ {created_count} รายการ, อัปเดต {updated_count} รายการ (รวม {len(properties_data)} รายการ)")

if __name__ == "__main__":
    seed_properties()

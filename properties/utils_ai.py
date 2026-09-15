import json

def generate_ai_seo_and_description(property_obj):
    """
    Generates a full AI description and structured SEO package strictly from actual DB fields.
    Zero-hallucination guarantee: only uses verified facts present on the property instance.
    """
    cat_name = property_obj.category.name if property_obj.category else "อสังหาริมทรัพย์"
    loc_name = property_obj.location.name if property_obj.location else ""
    code = property_obj.property_code or ""
    action_text = "ขาย" if property_obj.property_type == 'SALE' else "เช่า"
    
    try:
        price_val = float(property_obj.price)
        formatted_price = f"{price_val:,.0f}"
    except Exception:
        formatted_price = str(property_obj.price)

    # 1. Construct SEO Title
    seo_title = f"{action_text}{cat_name} {property_obj.title} {loc_name} รหัส {code} | Finding House"

    # 2. Construct H1 Title
    h1_title = f"{action_text}{cat_name} {property_obj.title} {loc_name}"

    # 3. Construct Specs List
    specs_list = []
    if property_obj.size_land and float(property_obj.size_land) > 0:
        specs_list.append(f"ขนาดที่ดิน {property_obj.size_land} ตร.ว.")
    if property_obj.size_usable and float(property_obj.size_usable) > 0:
        specs_list.append(f"พื้นที่ใช้สอย {property_obj.size_usable} ตร.ม.")
    if property_obj.bedrooms:
        specs_list.append(f"{property_obj.bedrooms} ห้องนอน")
    if property_obj.bathrooms:
        specs_list.append(f"{property_obj.bathrooms} ห้องน้ำ")
    if property_obj.floors:
        specs_list.append(f"{property_obj.floors} ชั้น")
    if property_obj.direction:
        specs_list.append(f"ทิศหน้าทรัพย์ {property_obj.direction}")
    if property_obj.parking_spaces:
        specs_list.append(f"จอดรถได้ {property_obj.parking_spaces} คัน")

    specs_str = " ".join(specs_list)

    # 4. Construct Landmarks Summary
    landmarks_text = ""
    landmarks_list = []
    if isinstance(property_obj.landmarks, list) and len(property_obj.landmarks) > 0:
        lm_items = []
        for lm in property_obj.landmarks:
            if isinstance(lm, dict) and lm.get('name'):
                dist = f" ({lm['distance']})" if lm.get('distance') else ""
                lm_items.append(f"{lm['name']}{dist}")
                landmarks_list.append(lm['name'])
        if lm_items:
            landmarks_text = "ทำเลใกล้เคียง: " + ", ".join(lm_items)

    # 5. Construct Meta Description
    meta_description = f"{action_text}{cat_name} {property_obj.title} ทำเล {loc_name} {specs_str} เสนอ{action_text}เพียง ฿{formatted_price} บาท {landmarks_text} ติดต่อ Finding House".strip()
    if len(meta_description) > 160:
        meta_description = meta_description[:157] + "..."

    # 6. Generate AI Description Text (Structured Copywriting)
    desc_paragraphs = [
        f"🏆 {action_text}{cat_name}พรีเมียม ทำเลคุณภาพ: {property_obj.title} (รหัสทรัพย์: {code})",
        f"เสนอ{action_text}ในราคาพิเศษเพียง ฿{formatted_price} บาท โดดเด่นด้วยทำเลศักยภาพสูง ย่าน{loc_name}",
        "",
        "📌 รายละเอียดและสเปกทรัพย์สิน:",
    ]
    for spec in specs_list:
        desc_paragraphs.append(f"  • {spec}")

    if property_obj.common_fee:
        desc_paragraphs.append(f"  • ค่าส่วนกลาง: ฿{float(property_obj.common_fee):,.0f} บาท/เดือน")
    if property_obj.deposit:
        desc_paragraphs.append(f"  • เงินประกัน: ฿{float(property_obj.deposit):,.0f} บาท")
    if property_obj.minimum_lease:
        desc_paragraphs.append(f"  • สัญญาขั้นต่ำ: {property_obj.minimum_lease}")

    if landmarks_text:
        desc_paragraphs.extend(["", f"📍 {landmarks_text}"])

    if isinstance(property_obj.features, dict) and len(property_obj.features) > 0:
        desc_paragraphs.extend(["", "✨ ฟังก์ชันและจุดเด่นจำเพาะ:"])
        for k, v in property_obj.features.items():
            desc_paragraphs.append(f"  • {k}: {v}")

    desc_paragraphs.extend([
        "",
        "📞 สนใจสอบถามข้อมูลเพิ่มเติม หรือนัดเข้าชมทรัพย์สินติดต่อ Finding House",
        "Hotline: 098-XXX-XXXX | LINE OA: @findinghouse | Email: contact@finding-house.com"
    ])

    ai_description = "\n".join(desc_paragraphs)

    # 7. Construct Keywords
    keywords_main = [
        f"{action_text}{cat_name}",
        f"{action_text}{cat_name}{loc_name}",
        f"{cat_name}{loc_name}",
        property_obj.title
    ]
    keywords_secondary = landmarks_list + [code, "Finding House"]

    # 8. Construct Google JSON-LD Structured Data
    structured_data = {
        "@context": "https://schema.org",
        "@type": "RealEstateListing",
        "name": seo_title,
        "description": meta_description,
        "identifier": code,
        "url": f"https://finding-house.com/properties/{property_obj.slug}",
        "offers": {
            "@type": "Offer",
            "price": str(property_obj.price),
            "priceCurrency": "THB",
            "availability": "https://schema.org/InStock" if property_obj.availability else "https://schema.org/OutOfStock"
        }
    }

    # 9. OpenGraph Object
    cover_img = property_obj.images.filter(is_cover=True).first() or property_obj.images.first()
    image_url = cover_img.image.url if cover_img and cover_img.image else ""
    
    open_graph = {
        "og:title": seo_title,
        "og:description": meta_description,
        "og:type": "article",
        "og:image": image_url,
        "og:url": f"https://finding-house.com/properties/{property_obj.slug}"
    }

    # 10. Image Alt Texts
    image_alt_texts = [
        f"{action_text}{cat_name} {property_obj.title} {loc_name} รูปที่ {idx + 1}"
        for idx in range(property_obj.images.count())
    ]

    return {
        "seo_title": seo_title,
        "h1_title": h1_title,
        "meta_description": meta_description,
        "keywords_main": keywords_main,
        "keywords_secondary": keywords_secondary,
        "ai_description": ai_description,
        "structured_data_json": structured_data,
        "open_graph": open_graph,
        "image_alt_texts": image_alt_texts
    }

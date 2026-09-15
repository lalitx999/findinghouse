from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from django.core.files.base import ContentFile
from django.utils.text import slugify

def generate_cover_banner(image_file, title="ประกาศอสังหาริมทรัพย์", price="0", property_code="", property_type_display="ขาย"):
    """
    Generates a branded cover image banner overlay with Title, Price, Property Code, and Finding House badge.
    """
    try:
        img = Image.open(image_file)
        if img.mode != 'RGB':
            img = img.convert('RGB')

        # Resize to standard cover banner resolution (1200 x 675 - 16:9 aspect ratio)
        target_width, target_height = 1200, 675
        img = img.resize((target_width, target_height), Image.Resampling.LANCZOS)

        # Create overlay layer for dark gradient card at bottom
        overlay = Image.new('RGBA', (target_width, target_height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)

        # Draw semi-transparent gradient card at bottom (height ~ 220px)
        card_height = 220
        card_top = target_height - card_height
        
        # Draw gradient rectangle
        for y in range(card_top, target_height):
            alpha = int(210 * ((y - card_top) / card_height))
            draw.line([(0, y), (target_width, y)], fill=(15, 23, 42, min(240, alpha + 60)))

        # Fonts setup
        try:
            font_title = ImageFont.truetype("arial.ttf", 32)
            font_price = ImageFont.truetype("arial.ttf", 44)
            font_badge = ImageFont.truetype("arial.ttf", 20)
        except IOError:
            font_title = ImageFont.load_default()
            font_price = ImageFont.load_default()
            font_badge = ImageFont.load_default()

        # 1. Draw Top Pill Badge (e.g., "ขาย | H0001")
        badge_text = f" {property_type_display.upper()} "
        if property_code:
            badge_text += f"|  รหัสทรัพย์: {property_code} "
        
        badge_x, badge_y = 50, card_top + 25
        draw.rectangle([badge_x, badge_y, badge_x + 320, badge_y + 36], fill=(234, 179, 8, 230)) # Amber badge
        draw.text((badge_x + 15, badge_y + 6), badge_text, fill=(0, 0, 0, 255), font=font_badge)

        # 2. Draw Property Title
        title_text = title if len(title) <= 45 else f"{title[:42]}..."
        draw.text((50, card_top + 75), title_text, fill=(255, 255, 255, 255), font=font_title)

        # 3. Draw Large Price
        try:
            formatted_price = f"฿{float(price):,.0f}"
        except Exception:
            formatted_price = f"฿{price}"

        draw.text((50, card_top + 125), formatted_price, fill=(255, 255, 255, 255), font=font_price)

        # 4. Draw Logo Watermark at top right
        draw.text((target_width - 240, 30), "FINDING HOUSE", fill=(255, 255, 255, 200), font=font_title)

        # Merge overlay onto main image
        banner = Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')

        # Save to ContentFile
        buffer = BytesIO()
        banner.save(buffer, format='JPEG', quality=90, optimize=True)
        buffer.seek(0)

        safe_name = slugify(title[:30], allow_unicode=True) or "banner"
        return ContentFile(buffer.getvalue(), name=f"banner-{safe_name}.jpg")
    except Exception as e:
        print(f"Error generating cover banner: {e}")
        return image_file

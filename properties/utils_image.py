import os
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from django.core.files.base import ContentFile
from django.utils.text import slugify

def process_and_watermark_image(image_file, prefix="finding-house", index=1, watermark_text="Finding House Real Estate"):
    """
    Optimizes image size, renames file for SEO, and overlays a watermark.
    """
    try:
        # Open original image
        img = Image.open(image_file)
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # 1. Resize if image is too large (max dimension 1920px)
        max_size = (1920, 1920)
        img.thumbnail(max_size, Image.Resampling.LANCZOS)
        
        width, height = img.size
        
        # 2. Apply Watermark Overlay
        overlay = Image.new('RGBA', img.size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(overlay)
        
        # Calculate font size relative to image height
        font_size = max(16, int(height * 0.035))
        try:
            # Try loading default system font or fallback to PIL default
            font = ImageFont.truetype("arial.ttf", font_size)
        except IOError:
            font = ImageFont.load_default()
        
        # Draw watermark text with semi-transparent background box at bottom-right
        text = f" {watermark_text} "
        
        # Calculate text bounding box
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        margin = int(width * 0.02)
        x = width - text_width - margin - 20
        y = height - text_height - margin - 20
        
        # Draw translucent background rectangle behind text
        bg_box = [x - 10, y - 5, x + text_width + 10, y + text_height + 5]
        draw.rectangle(bg_box, fill=(15, 23, 42, 160)) # Dark slate transparent
        
        # Draw white watermark text
        draw.text((x, y), text, fill=(255, 255, 255, 220), font=font)
        
        # Merge watermark layer onto image
        watermarked = Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')
        
        # 3. Format filename for SEO
        safe_prefix = slugify(prefix, allow_unicode=True) or "property"
        new_filename = f"{safe_prefix}-{index:02d}.jpg"
        
        # 4. Save to BytesIO buffer
        buffer = BytesIO()
        watermarked.save(buffer, format='JPEG', quality=88, optimize=True)
        buffer.seek(0)
        
        return ContentFile(buffer.getvalue(), name=new_filename)
    except Exception as e:
        print(f"Error processing image watermark: {e}")
        return image_file

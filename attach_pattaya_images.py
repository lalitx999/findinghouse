import os
import sys
import urllib.request
import django
from django.core.files.base import ContentFile

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from properties.models import Property, PropertyImage

# High Quality Curated Real Estate Sample Image URLs
IMAGE_SETS = [
    # 1. C0001: Pattaya North Luxury Condo
    [
        "https://images.unsplash.com/photo-1545324418-cc1a3fa10c00?w=1200&q=80",
        "https://images.unsplash.com/photo-1600607687939-ce8a6c25118c?w=1200&q=80",
        "https://images.unsplash.com/photo-1616594039964-ae9021a400a0?w=1200&q=80"
    ],
    # 2. H0001: Pattaya North Pool Villa
    [
        "https://images.unsplash.com/photo-1613977257363-707ba9348227?w=1200&q=80",
        "https://images.unsplash.com/photo-1512917774080-9991f1c4c750?w=1200&q=80",
        "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?w=1200&q=80"
    ],
    # 3. C0002: Pattaya Central Condo
    [
        "https://images.unsplash.com/photo-1567496898669-ee935f5f647a?w=1200&q=80",
        "https://images.unsplash.com/photo-1556911220-e15b29be8c8f?w=1200&q=80"
    ],
    # 4. B0001: Commercial Shophouse
    [
        "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?w=1200&q=80",
        "https://images.unsplash.com/photo-1497366216548-37526070297c?w=1200&q=80"
    ],
    # 5. C0003: Pattaya Central Rental Condo
    [
        "https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?w=1200&q=80",
        "https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?w=1200&q=80"
    ],
    # 6. H0002: Pattaya South Luxury Pool Villa
    [
        "https://images.unsplash.com/photo-1580587771525-78b9dba3b914?w=1200&q=80",
        "https://images.unsplash.com/photo-1512917774080-9991f1c4c750?w=1200&q=80"
    ],
    # 7. C0004: Pattaya South Beachfront Condo
    [
        "https://images.unsplash.com/photo-1512915922686-57c11dde9b6b?w=1200&q=80",
        "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=1200&q=80"
    ],
    # 8. L0001: Pattaya South Land
    [
        "https://images.unsplash.com/photo-1500382017468-9049fed747ef?w=1200&q=80",
        "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=1200&q=80"
    ],
    # 9. C0005: Pattaya North Naklua Rental Condo
    [
        "https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?w=1200&q=80",
        "https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?w=1200&q=80"
    ],
    # 10. H0003: Jomtien Beach House
    [
        "https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?w=1200&q=80",
        "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?w=1200&q=80"
    ]
]

def attach_images():
    print("Starting attaching images to 10 Pattaya properties...")
    
    # Fetch 10 Pattaya properties
    pattaya_props = Property.objects.filter(location__name__icontains="พัทยา").order_by('id')[:10]
    if len(pattaya_props) < 10:
        # Fallback to get latest 10 properties if location filter name varies
        pattaya_props = Property.objects.order_by('-id')[:10]

    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'}

    for idx, prop in enumerate(pattaya_props):
        urls = IMAGE_SETS[idx % len(IMAGE_SETS)]
        print(f"\nProcessing [{prop.property_code}] {prop.title} ({len(urls)} images)...")
        
        # Clear existing images if any to refresh cleanly
        prop.images.all().delete()
        
        for img_idx, url in enumerate(urls):
            try:
                req = urllib.request.Request(url, headers=headers)
                with urllib.request.urlopen(req, timeout=10) as response:
                    img_bytes = response.read()
                    
                is_cover = (img_idx == 0)
                file_name = f"{prop.property_code}_{img_idx+1}.jpg"
                
                img_obj = PropertyImage(
                    property=prop,
                    is_cover=is_cover
                )
                img_obj.image.save(file_name, ContentFile(img_bytes), save=True)
                print(f"  + Attached image {img_idx+1}: cover={is_cover}")
            except Exception as e:
                print(f"  ! Failed to download image {url}: {e}")

    print("\nAll 10 Pattaya properties images attached successfully!")

if __name__ == "__main__":
    attach_images()

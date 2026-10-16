from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.decorators import action
from django.db.models import Q
from .models import Category, Location, Property, Bookmark, Consignment, ConsignmentImage, ConsignmentDeed
from .serializers import (
    CategorySerializer, LocationSerializer, PropertySerializer, PropertyImageSerializer,
    BookmarkSerializer, BookmarkCreateSerializer,
    ConsignmentSerializer, ConsignmentCreateSerializer
)

class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = 'slug'


class LocationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer


class PropertyViewSet(viewsets.ModelViewSet):
    serializer_class = PropertySerializer
    lookup_field = 'slug'

    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'features_schema']:
            return [AllowAny()]
        if self.action in ['create_user_listing']:
            return [IsAuthenticated()]
        return [IsAdminUser()]

    def get_queryset(self):
        user = self.request.user
        status_param = self.request.query_params.get('status', None)

        if user and user.is_authenticated and user.is_staff:
            queryset = Property.objects.all().prefetch_related('images')
            if status_param and status_param != 'ALL':
                queryset = queryset.filter(status=status_param)
        else:
            queryset = Property.objects.filter(status='PUBLISHED').prefetch_related('images')
        
        # Parsing request query parameters for dynamic filters
        q = self.request.query_params.get('q', None)
        category = self.request.query_params.get('category', None)
        location = self.request.query_params.get('location', None)
        price_min = self.request.query_params.get('price_min', None)
        price_max = self.request.query_params.get('price_max', None)

        if q:
            queryset = queryset.filter(
                Q(title__icontains=q) | 
                Q(property_code__icontains=q) | 
                Q(description__icontains=q)
            )
        if category:
            queryset = queryset.filter(category__slug=category)
        if location:
            try:
                queryset = queryset.filter(location_id=int(location))
            except ValueError:
                # Handle cases where location query parameter is not an integer ID
                queryset = queryset.filter(location__slug=location)
        if price_min:
            queryset = queryset.filter(price__gte=price_min)
        if price_max:
            queryset = queryset.filter(price__lte=price_max)
            
        return queryset

    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def features_schema(self, request):
        from .constants import CATEGORY_FEATURES_SCHEMA, HIGHLIGHTS_CHOICES, SUITABLE_FOR_CHOICES
        return Response({
            'category_features': CATEGORY_FEATURES_SCHEMA,
            'highlights_choices': HIGHLIGHTS_CHOICES,
            'suitable_for_choices': SUITABLE_FOR_CHOICES
        })

    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def upload_image(self, request, slug=None):
        """
        Uploads and automatically watermarks a new property image for the specified property.
        """
        prop = self.get_object()
        image_file = request.FILES.get('image')
        if not image_file:
            return Response({'error': 'กรุณาแนบไฟล์รูปภาพ'}, status=status.HTTP_400_BAD_REQUEST)

        is_cover = str(request.data.get('is_cover', 'false')).lower() in ['true', '1']
        from .models import PropertyImage

        if is_cover:
            # Set other images is_cover to False
            prop.images.filter(is_cover=True).update(is_cover=False)

        last_order = prop.images.count() + 1
        img_obj = PropertyImage.objects.create(
            property=prop,
            image=image_file,
            is_cover=is_cover,
            order=last_order
        )
        return Response(PropertyImageSerializer(img_obj).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['delete'], url_path='delete_image/(?P<image_id>[0-9]+)', permission_classes=[IsAdminUser])
    def delete_image(self, request, slug=None, image_id=None):
        """
        Deletes a specific property image.
        """
        prop = self.get_object()
        from .models import PropertyImage
        try:
            img = prop.images.get(id=image_id)
            was_cover = img.is_cover
            img.delete()
            # If was cover, make first remaining image the cover
            if was_cover:
                first_img = prop.images.first()
                if first_img:
                    first_img.is_cover = True
                    first_img.save(update_fields=['is_cover'])
            return Response({'message': 'ลบรูปภาพสำเร็จ'}, status=status.HTTP_200_OK)
        except PropertyImage.DoesNotExist:
            return Response({'error': 'ไม่พบรูปภาพดังกล่าวในทรัพย์นี้'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def create_user_listing(self, request):
        images = request.FILES.getlist('images')
        if len(images) < 5 or len(images) > 20:
            return Response({
                'error': f'กรุณาอัปโหลดรูปภาพทรัพย์อย่างน้อย 5 รูป และสูงสุดไม่เกิน 20 รูป (ปัจจุบันแนบ {len(images)} รูป)'
            }, status=status.HTTP_400_BAD_REQUEST)

        title = request.data.get('title')
        price = request.data.get('price')
        category_id = request.data.get('category')
        location_id = request.data.get('location')
        seller_name = request.data.get('seller_name') or f"{request.user.first_name} {request.user.last_name}".strip() or request.user.username
        seller_phone = request.data.get('seller_phone')
        seller_line_id = request.data.get('seller_line_id', '')

        if not title or not price or not category_id or not location_id or not seller_phone:
            return Response({'error': 'กรุณากรอกข้อมูลสำคัญ (ชื่อทรัพย์, ราคา, หมวดหมู่, ทำเล และเบอร์โทรผู้ขาย) ให้ครบถ้วน'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            category = Category.objects.get(pk=int(category_id))
            location = Location.objects.get(pk=int(location_id))
        except (Category.DoesNotExist, Location.DoesNotExist, ValueError):
            return Response({'error': 'หมวดหมู่ หรือ ทำเลที่ตั้ง ไม่ถูกต้อง'}, status=status.HTTP_400_BAD_REQUEST)

        # Create Property Object
        prop = Property.objects.create(
            title=title.strip(),
            description=request.data.get('description', ''),
            price=price,
            property_type=request.data.get('property_type', 'SALE'),
            category=category,
            location=location,
            bedrooms=request.data.get('bedrooms') or None,
            bathrooms=request.data.get('bathrooms') or None,
            size_land=request.data.get('size_land') or None,
            size_usable=request.data.get('size_usable') or None,
            seller_name=seller_name,
            seller_phone=seller_phone,
            seller_line_id=seller_line_id,
            is_direct_seller=True,
            status='PUBLISHED',
            source='FINDING_HOUSE',
            agent=None
        )

        # Save and Watermark All Images automatically
        from .models import PropertyImage
        for idx, img in enumerate(images, start=1):
            PropertyImage.objects.create(
                property=prop,
                image=img,
                is_cover=(idx == 1),
                order=idx
            )

        # Send Notification Email to Company
        try:
            from django.core.mail import send_mail
            email_subject = f"[แจ้งเตือนลงทรัพย์ใหม่] คุณ {seller_name} ได้ลงประกาศขายทรัพย์ {prop.property_code}"
            email_body = f"""มีผู้ใช้งานลงประกาศขายทรัพย์ตรงในระบบ Finding House:

- ผู้ขาย: คุณ {seller_name}
- เบอร์โทรศัพท์: {seller_phone} (ยืนยัน OTP เรียบร้อย)
- LINE ID: {seller_line_id or '-'}
- รหัสทรัพย์: {prop.property_code}
- หัวข้อประกาศ: {prop.title}
- ราคาเสนอขาย/เช่า: ฿{float(price):,.2f} บาท
- ประเภท: {prop.get_property_type_display()}
- หมวดหมู่: {category.name} | ทำเล: {location.name}

ตรวจสอบประกาศในระบบหลังบ้าน:
http://127.0.0.1:8000/admin/properties/property/{prop.id}/change/
"""
            send_mail(
                email_subject,
                email_body,
                'noreply@findinghouse.co.th',
                ['contact@findinghouse.co.th'],
                fail_silently=True
            )
        except Exception as e:
            print(f"Error sending email notification: {e}")

        return Response(PropertySerializer(prop).data, status=status.HTTP_201_CREATED)


class BookmarkViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Bookmark.objects.filter(user=self.request.user).select_related('property', 'property__category', 'property__location')

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return BookmarkCreateSerializer
        return BookmarkSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ConsignmentViewSet(viewsets.ModelViewSet):
    serializer_class = ConsignmentSerializer

    def get_permissions(self):
        # Allow anyone to submit a new consignment form (POST create)
        if self.action == 'create':
            return [AllowAny()]
        # All management actions (list, retrieve, update, destroy) require Admin / Staff
        return [IsAdminUser()]

    def get_queryset(self):
        # Strict protection: Only staff/admin can query consignment records
        if not self.request.user or not self.request.user.is_authenticated or not self.request.user.is_staff:
            return Consignment.objects.none()
        return Consignment.objects.all().prefetch_related('images', 'deeds')

    def get_serializer_class(self):
        if self.action in ['create']:
            return ConsignmentCreateSerializer
        return ConsignmentSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        images = request.FILES.getlist('images')
        deeds = request.FILES.getlist('deeds')

        # Security: File Count and Size Limit Checks
        MAX_IMAGES = 25
        MAX_DEEDS = 10
        MAX_FILE_SIZE = 15 * 1024 * 1024  # 15 MB per file
        ALLOWED_EXTS = {'.jpg', '.jpeg', '.png', '.webp', '.pdf'}

        import os

        if len(images) > MAX_IMAGES:
            return Response(
                {'error': f'แนบรูปภาพทรัพย์ได้สูงสุดไม่เกิน {MAX_IMAGES} รูป (แนบมา {len(images)} รูป)'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if len(deeds) > MAX_DEEDS:
            return Response(
                {'error': f'แนบเอกสารโฉนดได้สูงสุดไม่เกิน {MAX_DEEDS} ไฟล์ (แนบมา {len(deeds)} ไฟล์)'},
                status=status.HTTP_400_BAD_REQUEST
            )

        for f in images + deeds:
            if f.size > MAX_FILE_SIZE:
                return Response(
                    {'error': f'ไฟล์ {f.name} มีขนาดเกินกำหนด (สูงสุดไม่เกิน 15 MB ต่อไฟล์)'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            ext = os.path.splitext(f.name)[1].lower()
            if ext not in ALLOWED_EXTS:
                return Response(
                    {'error': f'ไฟล์ {f.name} ไม่รองรับ (รองรับเฉพาะไฟล์รูปภาพ .jpg, .png, .webp หรือ .pdf)'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        consignment = serializer.save()

        # Handle multiple uploaded property images
        for img in images:
            ConsignmentImage.objects.create(consignment=consignment, image=img)

        # Handle multiple uploaded confidential deed images
        for deed in deeds:
            ConsignmentDeed.objects.create(consignment=consignment, deed_image=deed)

        headers = self.get_success_headers(serializer.data)
        # Return sanitized summary response without exposing deed URLs directly
        return Response({
            'id': consignment.id,
            'owner_name': consignment.owner_name,
            'property_type': consignment.property_type,
            'status': consignment.status,
            'images_count': len(images),
            'deeds_count': len(deeds),
            'message': 'ส่งเรื่องฝากขายเรียบร้อยแล้ว เจ้าหน้าที่จะติดต่อกลับเพื่อตรวจสอบข้อมูล',
            'created_at': consignment.created_at
        }, status=status.HTTP_201_CREATED, headers=headers)

    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def convert_to_property(self, request, pk=None):
        """
        1-Click Consignment to Property Converter
        Converts an approved consignment record directly into a published Property listing.
        """
        consignment = self.get_object()

        # 1. Map Category
        category_map = {
            'HOUSE': 'บ้าน',
            'CONDO': 'คอนโด',
            'LAND': 'ที่ดิน',
            'WAREHOUSE': 'โรงงาน',
            'HOTEL': 'โรงแรม',
        }
        target_cat_name = category_map.get(consignment.property_type, 'บ้าน')
        category = Category.objects.filter(name__icontains=target_cat_name).first()
        if not category:
            category = Category.objects.first()

        # 2. Map Location
        location = Location.objects.filter(name__icontains=consignment.province).first()
        if not location and consignment.district:
            location = Location.objects.filter(name__icontains=consignment.district).first()
        if not location:
            location = Location.objects.first()

        # 3. Extract Specs
        specs = consignment.specs or {}
        bedrooms = specs.get('bedrooms')
        bathrooms = specs.get('bathrooms')
        usable_size = specs.get('usable_size') or specs.get('size_usable')
        land_size = specs.get('land_size') or specs.get('size_land')

        # 4. Generate title
        title = consignment.highlights or f"{consignment.get_property_type_display()} ทำเล {consignment.district or ''} {consignment.province}"
        if consignment.project_name:
            title = f"{consignment.project_name} - {title}"

        # 5. Create Property Object
        prop = Property.objects.create(
            title=title.strip()[:200],
            description=consignment.notes or consignment.highlights or f"ทรัพย์ฝากขาย ทำเล {consignment.subdistrict} {consignment.district} {consignment.province}",
            price=consignment.target_price,
            property_type='SALE',
            category=category,
            location=location,
            bedrooms=int(bedrooms) if bedrooms and str(bedrooms).isdigit() else None,
            bathrooms=int(bathrooms) if bathrooms and str(bathrooms).isdigit() else None,
            size_usable=float(usable_size) if usable_size else None,
            size_land=float(land_size) if land_size else None,
            google_maps_link=consignment.google_maps_link or '',
            seller_name=consignment.owner_name,
            seller_phone=consignment.owner_phone,
            seller_line_id=consignment.owner_line_id or '',
            is_direct_seller=False,
            status='PUBLISHED',
            source='FINDING_HOUSE',
            agent=request.user if request.user and request.user.is_authenticated else None
        )

        # 6. Copy Property Images
        for idx, c_img in enumerate(consignment.images.all(), start=1):
            if c_img.image:
                PropertyImage.objects.create(
                    property=prop,
                    image=c_img.image,
                    is_cover=(idx == 1),
                    order=idx
                )

        # 7. Mark Consignment as APPROVED
        consignment.status = 'APPROVED'
        consignment.save(update_fields=['status'])

        return Response({
            'message': f'แปลงคำขอฝากขายเป็นทรัพย์เรียบร้อยแล้ว รหัสทรัพย์ [{prop.property_code}]',
            'property_id': prop.id,
            'property_code': prop.property_code,
            'slug': prop.slug,
            'title': prop.title
        }, status=status.HTTP_201_CREATED)




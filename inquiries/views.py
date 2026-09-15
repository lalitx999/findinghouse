from rest_framework import generics
from .models import Inquiry
from .serializers import InquirySerializer
from .utils_email import send_inquiry_notification_to_admin, send_auto_reply_to_customer

class InquiryCreateView(generics.CreateAPIView):
    queryset = Inquiry.objects.all()
    serializer_class = InquirySerializer

    def perform_create(self, serializer):
        inquiry = serializer.save()
        # Trigger Email Notifications (Sends to Admin & Auto-reply to Customer)
        send_inquiry_notification_to_admin(inquiry)
        send_auto_reply_to_customer(inquiry)


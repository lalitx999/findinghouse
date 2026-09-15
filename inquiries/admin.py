from django.contrib import admin
from .models import Inquiry

@admin.register(Inquiry)
class InquiryAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'property', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name', 'email', 'phone', 'message', 'property__property_code')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        # Limit staff to see only inquiries of properties they manage
        return qs.filter(property__agent=request.user)

    def has_change_permission(self, request, obj=None):
        # Inquiries should be read-only for all to prevent modification of lead messages
        return False

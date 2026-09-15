from django.db.models import Sum
from properties.models import Property
from crm.models import Lead, Deal, LeaseAgreement, ViewingAppointment
from audit.models import AuditLog

def admin_dashboard_stats(request):
    if not request.path.startswith('/admin/'):
        return {}

    try:
        published_properties_count = Property.objects.filter(status='PUBLISHED').count()
        active_leads_count = Lead.objects.exclude(status__in=['CLOSED_WON', 'CLOSED_LOST']).count()
        total_leads_count = Lead.objects.count()
        
        closed_won_deals = Deal.objects.filter(stage='CLOSED_WON')
        total_revenue = closed_won_deals.aggregate(total=Sum('agreed_price'))['total'] or 0.0
        commission_sum = closed_won_deals.aggregate(total=Sum('commission_amount'))['total'] or 0.0
        company_share_sum = closed_won_deals.aggregate(total=Sum('company_share'))['total'] or 0.0
        
        expiring_leases_count = LeaseAgreement.objects.filter(status__in=['EXPIRING_SOON', 'EXPIRED']).count()
        total_appointments_count = ViewingAppointment.objects.count()

        # Recent Real DB Objects for Live Admin Widgets
        recent_deals = list(Deal.objects.select_related('property', 'lead', 'agent').order_by('-updated_at')[:5])
        recent_leads = list(Lead.objects.order_by('-created_at')[:5])
        recent_properties = list(Property.objects.select_related('category', 'location').order_by('-created_at')[:5])
        recent_audit_logs = list(AuditLog.objects.select_related('user').order_by('-timestamp')[:5])

        return {
            'dashboard_stats': {
                'published_properties': published_properties_count,
                'active_leads': active_leads_count,
                'total_leads': total_leads_count,
                'total_revenue': total_revenue,
                'total_commission': commission_sum,
                'company_share': company_share_sum,
                'expiring_leases': expiring_leases_count,
                'total_appointments': total_appointments_count,
                'recent_deals': recent_deals,
                'recent_leads': recent_leads,
                'recent_properties': recent_properties,
                'recent_audit_logs': recent_audit_logs,
            }
        }
    except Exception as e:
        return {}

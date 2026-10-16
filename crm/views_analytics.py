from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from django.db.models import Count, Sum, Q, Avg
from crm.models import Lead, Deal, ViewingAppointment
from properties.models import Property
from config.permissions import IsAgentOrManager

class AnalyticsDashboardView(APIView):
    """
    Executive & Operational Analytics API for Finding House CRM
    """
    permission_classes = [permissions.IsAuthenticated, IsAgentOrManager]

    def get(self, request, *args, **kwargs):
        # 1. Lead Conversion Analytics
        total_leads = Lead.objects.count()
        closed_won_leads = Lead.objects.filter(status='CLOSED_WON').count()
        conversion_rate = round((closed_won_leads / total_leads * 100), 1) if total_leads > 0 else 0.0

        # 2. Deals & Revenue Statistics
        total_deals = Deal.objects.count()
        won_deals = Deal.objects.filter(stage='CLOSED_WON')
        total_revenue = won_deals.aggregate(total=Sum('agreed_price'))['total'] or 0
        total_commission = won_deals.aggregate(total=Sum('commission_amount'))['total'] or 0

        # 3. Top Agents Performance
        agent_stats = (
            Deal.objects.filter(stage='CLOSED_WON')
            .values('agent__id', 'agent__first_name', 'agent__last_name', 'agent__username')
            .annotate(
                deals_won=Count('id'),
                total_sales=Sum('agreed_price'),
                total_commission=Sum('agent_share')
            )
            .order_by('-total_sales')[:5]
        )

        top_agents = []
        for ag in agent_stats:
            name = f"{ag['agent__first_name']} {ag['agent__last_name']}".strip() or ag['agent__username'] or "Unassigned"
            top_agents.append({
                'id': ag['agent__id'],
                'name': name,
                'deals_won': ag['deals_won'],
                'total_sales': float(ag['total_sales'] or 0),
                'total_commission': float(ag['total_commission'] or 0),
            })

        # 4. Property Category Breakdown
        property_count = Property.objects.count()
        popular_properties = (
            Property.objects.filter(status='PUBLISHED')
            .select_related('category', 'location')
            .order_by('-id')[:5]
        )

        popular_list = []
        for prop in popular_properties:
            popular_list.append({
                'id': prop.id,
                'title': prop.title,
                'code': prop.property_code,
                'price': float(prop.price),
                'category': prop.category.name if prop.category else 'N/A',
                'location': prop.location.name if prop.location else 'N/A',
            })

        return Response({
            'overview': {
                'total_leads': total_leads,
                'closed_won_leads': closed_won_leads,
                'conversion_rate_percentage': conversion_rate,
                'total_deals': total_deals,
                'total_revenue_baht': float(total_revenue),
                'total_commission_baht': float(total_commission),
                'total_properties_published': property_count,
            },
            'top_performing_agents': top_agents,
            'featured_properties': popular_list,
        })

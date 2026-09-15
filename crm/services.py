from properties.models import Property
from crm.models import Lead, LeadMatch

def run_lead_auto_matching(lead):
    """
    Auto-Matching Engine for Finding House CRM.
    Compares a Lead's criteria against published properties and generates LeadMatch records.
    """
    published_properties = Property.objects.filter(status='PUBLISHED').select_related('category', 'location')
    
    lead_categories = set(lead.categories.values_list('id', flat=True))
    lead_locations = set(lead.locations.values_list('id', flat=True))
    
    created_or_updated_count = 0

    for prop in published_properties:
        score = 0
        reasons = []

        # 1. Property Type / Intent Check
        if lead.lead_type == 'BUYER' and prop.property_type == 'SALE':
            score += 10
            reasons.append("ตรงวัตถุประสงค์ (ขาย)")
        elif lead.lead_type == 'RENTER' and prop.property_type == 'RENT':
            score += 10
            reasons.append("ตรงวัตถุประสงค์ (เช่า)")

        # 2. Category Check (Weight 25 pts)
        if lead_categories:
            if prop.category_id in lead_categories:
                score += 25
                reasons.append(f"หมวดหมู่ตรงตามต้องการ ({prop.category.name})")
        else:
            score += 15 # Partial points if lead didn't restrict categories

        # 3. Location Check (Weight 25 pts)
        if lead_locations:
            if prop.location_id in lead_locations:
                score += 25
                reasons.append(f"ทำเลตรงตามต้องการ ({prop.location.name})")
        else:
            score += 15 # Partial points if lead didn't restrict locations

        # 4. Budget Range Check (Weight 30 pts)
        if prop.price and (lead.budget_min or lead.budget_max):
            price_val = float(prop.price)
            min_ok = (lead.budget_min is None) or (price_val >= float(lead.budget_min))
            max_ok = (lead.budget_max is None) or (price_val <= float(lead.budget_max))

            if min_ok and max_ok:
                score += 30
                reasons.append(f"อยู่ในช่วงงบประมาณ (฿{price_val:,.0f})")
            elif max_ok and price_val <= float(lead.budget_max) * 1.1: # 10% tolerance over max budget
                score += 15
                reasons.append(f"เกินงบไม่เกิน 10% (฿{price_val:,.0f})")
        else:
            score += 15

        # 5. Bedrooms Check (Weight 10 pts)
        if lead.min_bedrooms and prop.bedrooms:
            if prop.bedrooms >= lead.min_bedrooms:
                score += 10
                reasons.append(f"จำนวนห้องนอนตรงตามต้องการ ({prop.bedrooms} ห้อง)")
        elif not lead.min_bedrooms:
            score += 10

        # Final Score Normalization (Cap at 100)
        final_score = min(score, 100)

        # Threshold: Only create match if score >= 50%
        if final_score >= 50:
            match_obj, _ = LeadMatch.objects.update_or_create(
                lead=lead,
                property=prop,
                defaults={
                    'match_score': final_score,
                    'match_reasons': reasons
                }
            )
            created_or_updated_count += 1

    # Update Lead status if matches were found
    if created_or_updated_count > 0 and lead.status == 'NEW':
        lead.status = 'MATCHED'
        lead.save()

    return created_or_updated_count

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Lead, Deal
from audit.utils_notify import send_line_notification, dispatch_webhook_event
from audit.models import Notification

@receiver(post_save, sender=Lead)
def on_lead_created(sender, instance, created, **kwargs):
    if created:
        msg = f"\n📌 [ลีดใหม่เข้าสู่ระบบ]\nคุณ: {instance.name}\nโทร: {instance.phone}\nประเภท: {instance.get_lead_type_display()}\nงบประมาณ: {instance.budget_max or 'ไม่ระบุ'} บาท"
        send_line_notification(msg)

        payload = {
            'event': 'LEAD_CREATED',
            'lead_id': instance.id,
            'name': instance.name,
            'phone': instance.phone,
            'lead_type': instance.lead_type,
            'budget_max': float(instance.budget_max) if instance.budget_max else None
        }
        dispatch_webhook_event('LEAD_CREATED', payload)

        if instance.assigned_agent:
            Notification.objects.create(
                user=instance.assigned_agent,
                title=f"มีลีดใหม่: คุณ {instance.name}",
                message=f"มีลีดใหม่เข้ามาในระบบ เบอร์โทร {instance.phone}",
                link=f"/admin/crm/lead/{instance.id}/change/"
            )


@receiver(post_save, sender=Deal)
def on_deal_closed_won(sender, instance, created, **kwargs):
    if instance.stage == 'CLOSED_WON':
        msg = f"\n🎉 [ปิดการขาย/เช่าสำเร็จ!]\nดีล: {instance.title}\nราคาตกลง: ฿{instance.agreed_price:,.0f}\nค่าคอมมิชชันรวม: ฿{instance.commission_amount:,.0f}\nนายหน้าผู้ดูแล: {instance.agent.username if instance.agent else 'ไม่ระบุ'}"
        send_line_notification(msg)

        payload = {
            'event': 'DEAL_CLOSED',
            'deal_id': instance.id,
            'title': instance.title,
            'agreed_price': float(instance.agreed_price) if instance.agreed_price else 0,
            'commission_amount': float(instance.commission_amount) if instance.commission_amount else 0,
            'agent': instance.agent.username if instance.agent else None
        }
        dispatch_webhook_event('DEAL_CLOSED', payload)

        if instance.agent:
            Notification.objects.create(
                user=instance.agent,
                title=f"ปิดการขายสำเร็จ! ดีล {instance.title}",
                message=f"ยินดีด้วย! ดีลปิดสำเร็จ ยอดคอมมิชชัน ฿{instance.commission_amount:,.0f}",
                link=f"/admin/crm/deal/{instance.id}/change/"
            )

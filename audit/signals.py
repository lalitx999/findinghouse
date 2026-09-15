from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import AuditLog
from .middleware import get_current_request, get_current_user, get_client_ip

EXCLUDED_MODELS = {'AuditLog', 'Session', 'Contenttype', 'Permission', 'Group', 'LogEntry'}

@receiver(post_save)
def audit_post_save(sender, instance, created, **kwargs):
    model_name = sender.__name__
    app_label = sender._meta.app_label

    if model_name in EXCLUDED_MODELS or app_label == 'audit' or app_label == 'admin':
        return

    request = get_current_request()
    user = get_current_user()
    ip_address = None
    user_agent = None

    if request:
        ip_address = get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')[:500]

    action = 'CREATE' if created else 'UPDATE'
    object_repr = str(instance)[:255]
    object_id = str(getattr(instance, 'pk', ''))

    details = {
        'model': model_name,
        'app_label': app_label,
        'repr': object_repr
    }

    try:
        AuditLog.objects.create(
            user=user,
            action=action,
            model_name=f"{app_label}.{model_name}",
            object_id=object_id,
            object_repr=object_repr,
            details=details,
            ip_address=ip_address,
            user_agent=user_agent
        )
    except Exception:
        # Avoid breaking primary transactions if audit creation fails
        pass

@receiver(post_delete)
def audit_post_delete(sender, instance, **kwargs):
    model_name = sender.__name__
    app_label = sender._meta.app_label

    if model_name in EXCLUDED_MODELS or app_label == 'audit' or app_label == 'admin':
        return

    request = get_current_request()
    user = get_current_user()
    ip_address = None
    user_agent = None

    if request:
        ip_address = get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')[:500]

    object_repr = str(instance)[:255]
    object_id = str(getattr(instance, 'pk', ''))

    details = {
        'model': model_name,
        'app_label': app_label,
        'repr': object_repr
    }

    try:
        AuditLog.objects.create(
            user=user,
            action='DELETE',
            model_name=f"{app_label}.{model_name}",
            object_id=object_id,
            object_repr=object_repr,
            details=details,
            ip_address=ip_address,
            user_agent=user_agent
        )
    except Exception:
        pass

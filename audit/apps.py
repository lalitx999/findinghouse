from django.apps import AppConfig

class AuditConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'audit'
    verbose_name = 'บันทึกประวัติกิจกรรมระบบ (Audit Log)'

    def ready(self):
        import audit.signals  # noqa

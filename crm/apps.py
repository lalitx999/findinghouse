from django.apps import AppConfig

class CrmConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'crm'
    verbose_name = 'ระบบบริหารลูกค้าและลีด (CRM)'

    def ready(self):
        import crm.signals  # noqa

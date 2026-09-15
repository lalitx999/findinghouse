from django.db import models
from django.utils import timezone

class SoftQuerySet(models.QuerySet):
    def delete(self):
        return super().update(is_deleted=True, deleted_at=timezone.now())

    def hard_delete(self):
        return super().delete()

    def alive(self):
        return self.filter(is_deleted=False)

    def dead(self):
        return self.filter(is_deleted=True)


class SoftDeleteManager(models.Manager):
    def __init__(self, *args, **kwargs):
        self.alive_only = kwargs.pop('alive_only', True)
        super().__init__(*args, **kwargs)

    def get_queryset(self):
        if self.alive_only:
            return SoftQuerySet(self.model, using=self._db).filter(is_deleted=False)
        return SoftQuerySet(self.model, using=self._db)

    def hard_delete(self):
        return self.get_queryset().hard_delete()


class SoftDeleteMixin(models.Model):
    is_deleted = models.BooleanField(default=False, verbose_name="สถานะการลบ (Soft Delete)")
    deleted_at = models.DateTimeField(null=True, blank=True, verbose_name="เวลาที่ถูกลบ")

    objects = SoftDeleteManager()
    all_objects = SoftDeleteManager(alive_only=False)

    class Meta:
        abstract = True

    def delete(self, using=None, keep_parents=False):
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save(update_fields=['is_deleted', 'deleted_at'])

    def restore(self):
        self.is_deleted = False
        self.deleted_at = None
        self.save(update_fields=['is_deleted', 'deleted_at'])

    def hard_delete(self):
        super().delete()

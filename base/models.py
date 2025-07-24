from django.db import models
from django.utils import timezone

class BaseModel(models.Model):
    is_active = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    created_by = models.ForeignKey(
        'users.User', 
        null=True,
        blank=True,
        related_name='created_%(class)s_objects',
        on_delete=models.SET_NULL
    )
    updated_by = models.ForeignKey(
        'users.User',  
        null=True,
        blank=True,
        related_name='updated_%(class)s_objects',
        on_delete=models.SET_NULL
    )

    def soft_delete(self):
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save(update_fields=['is_deleted', 'deleted_at'])

    def restore(self):
        self.is_deleted = False
        self.deleted_at = None
        self.save(update_fields=['is_deleted', 'deleted_at'])

    class Meta:
        abstract = True

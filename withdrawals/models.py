from django.db import models

from base.models import BaseModel
from users.models import User

# Create your models here.
class Withdrawal(BaseModel):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'owner'})
    amount = models.FloatField()
    method = models.CharField(max_length=20, choices=(
        ('upi', 'UPI'),
        ('bank', 'Bank Account'),
    ))
    upi_id = models.CharField(max_length=50, blank=True)
    bank_account = models.CharField(max_length=50, blank=True)
    status = models.CharField(max_length=20, choices=(
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ), default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
from django.db import models
from base.models import BaseModel
from bookings.models import ParkingBooking

# Create your models here.
class Payment(BaseModel):
    PAYMENT_METHOD_CHOICES = (
        ('online', 'Online'),
        ('offline', 'Offline'),
    )
    booking = models.OneToOneField(ParkingBooking, on_delete=models.CASCADE)
    amount = models.FloatField()
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    qr_code = models.URLField(blank=True)  
    transaction_id = models.CharField(max_length=50, blank=True)  
    payment_status = models.CharField(max_length=20, choices=(
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ), default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    
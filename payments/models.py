from django.db import models
from base.models import BaseModel
from bookings.models import ParkingBooking
from subscription.models import DealerSubscription


class Payment(BaseModel):
    PAYMENT_METHOD_CHOICES = (
        ('online', 'Online'),
        ('offline', 'Offline'),
    )

    PAYMENT_STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    )

    booking = models.OneToOneField(ParkingBooking, on_delete=models.CASCADE, related_name="payment")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default="INR")
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    qr_code = models.URLField(blank=True, null=True)  
    transaction_id = models.CharField(max_length=100, unique=True, blank=True, null=True)  
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    paid_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Booking Payment ({self.booking.id}) - {self.payment_status}"


class SubscriptionPayment(BaseModel):
    PAYMENT_METHOD_CHOICES = (
        ('online', 'Online'),
        ('offline', 'Offline'),
    )

    PAYMENT_STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    )

    subscription = models.OneToOneField(DealerSubscription, on_delete=models.CASCADE, related_name="payment")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default="INR")
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    transaction_id = models.CharField(max_length=100, unique=True, blank=True, null=True)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    paid_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Subscription Payment ({self.subscription.owner.email}) - {self.payment_status}"

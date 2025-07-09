from django.db import models
from base.models import BaseModel
from parking.models import  VehicleInfo
from users.models import User
from vehicles.models import VehicleType

class ParkingBooking(BaseModel):
    STATUS = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed')
    )
    customer = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'user_type': 'customer'})
    parking_slot = models.ForeignKey(VehicleInfo, on_delete=models.CASCADE)
    vehicle_type = models.ForeignKey(VehicleType, on_delete=models.CASCADE)
    booking_time = models.DateTimeField(auto_now_add=True)
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    estimated_duration = models.FloatField(null=True)  # In hours, optional
    status = models.CharField(max_length=20, choices=STATUS, default='pending')
    otp_code = models.CharField(max_length=4)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    paid_online = models.BooleanField(default=False)

from django.db import models

from base.models import BaseModel
from bookings.models import ParkingBooking
from users.models import User

class Dispute(BaseModel):
    booking = models.ForeignKey(ParkingBooking, on_delete=models.CASCADE)
    raised_by = models.ForeignKey(User, on_delete=models.CASCADE)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=(
        ('open', 'Open'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ), default='open')
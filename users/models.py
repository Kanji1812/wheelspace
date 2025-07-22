from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from base.models import BaseModel
from vehicles.models import VehicleType

class User(AbstractUser):
    USER_TYPE_CHOICES = [
        ('admin', 'Admin'),
        ('owner', 'Parking Owner'),
        ('customer', 'Customer'),
        ('guard', 'Guard'),
    ]

    username = None  # Remove username field
    email = models.EmailField(_('email address'), unique=True)  # Make email required & unique

    phone_number = models.CharField(max_length=15, unique=True)
    otp = models.CharField(_("OTP"), max_length=6, null=True, blank=True)
    age = models.IntegerField(_("Age"), null=True)
    address = models.TextField(_("Address"), null=True, blank=True)
    profile_image = models.ImageField(upload_to='profiles/', null=True, blank=True)
    user_type = models.CharField(_("Role"), choices=USER_TYPE_CHOICES, null=False, blank=False)
    is_verified = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'  # Tell Django to use email as the identifier
    REQUIRED_FIELDS = ['phone_number', 'user_type']  # Fields required when creating a superuser

    def __str__(self):
        return self.email
    
class Customer(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'user_type': 'customer'})
    vehicle_type = models.ForeignKey(VehicleType, on_delete=models.CASCADE)
    number_plate = models.CharField(max_length=20, unique=True)
    licence_number = models.CharField(max_length=20, unique=True)
    rc_book_number = models.CharField(max_length=20, unique=True)
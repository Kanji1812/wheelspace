from django.contrib.auth.models import AbstractUser
from django.contrib.auth.base_user import BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _
from base.models import BaseModel
from vehicles.models import VehicleType

class CustomUserManager(BaseUserManager):
    def create_user(self, email, phone_number, user_type, password=None, **extra_fields):
        if not email:
            raise ValueError(_('The Email must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, phone_number=phone_number, user_type=user_type, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, phone_number, user_type='admin', password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_verified', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))

        return self.create_user(email, phone_number, user_type, password, **extra_fields)


class User(AbstractUser):
    USER_TYPE_CHOICES = [
        ('admin', 'Admin'),
        ('owner', 'Parking Owner'),
        ('customer', 'Customer'),
        ('guard', 'Guard'),
    ]
    objects = CustomUserManager()
    username = None  # Remove username field
    full_name = models.CharField(max_length=15, blank=True,null=True)
    email = models.EmailField(_('email address'), unique=True)  # Make email required & unique

    phone_number = models.CharField(max_length=15, unique=True)
    otp = models.CharField(_("OTP"), max_length=6, null=True, blank=True)
    age = models.IntegerField(_("Age"), null=True)
    address = models.TextField(_("Address"), null=True, blank=True)
    profile_image = models.ImageField(upload_to='profiles/', null=True, blank=True)
    user_type = models.CharField(_("Role"),choices=USER_TYPE_CHOICES,null=False,blank=False)
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
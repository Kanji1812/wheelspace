from django.db import models
from base.models import BaseModel
from vehicles.models import VehicleType
from users.models import User
from django.utils.translation import gettext_lazy as _

class ParkingArea(BaseModel):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'user_type': 'owner'})
    name = models.CharField(max_length=100)
    address = models.TextField(_("Address"),blank=True,null=True)
    property_area = models.PositiveIntegerField(_("Area of SQFT"),default=0)  # in square feet
    latitude = models.FloatField()
    longitude = models.FloatField()
    gmap_link = models.URLField(null=True,blank=True)
    total_capacity = models.PositiveIntegerField(default=0)
    available_capacity = models.PositiveIntegerField(default=0)
    is_verified = models.BooleanField(default=False)
    legal_doc = models.FileField(upload_to='land_docs/',null=True,blank=True)

class VehicleInfo(BaseModel):
    vehicle_type = models.ForeignKey(VehicleType, verbose_name=_("Vehicle Type"), on_delete=models.CASCADE)
    parking_area = models.ForeignKey(ParkingArea, on_delete=models.CASCADE,related_name='slots',verbose_name=_("Parking Area"))
    capacity = models.PositiveIntegerField(default=0)
    rate_per_hour = models.DecimalField(max_digits=6, decimal_places=2,default=0)
    available_count = models.PositiveIntegerField(default=0)

class ParkingGuard(BaseModel):
    parking_area = models.ForeignKey(ParkingArea, on_delete=models.CASCADE)
    guard_user = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'user_type': 'guard'})

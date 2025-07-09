from django.db import models
from django.utils.translation import gettext_lazy as _
from base.models import BaseModel

class VehicleType(BaseModel):
    vehicle_type = models.CharField(_("Vehicle Type"),max_length=50)
    icon = models.ImageField(_("Icon"),upload_to='vehicle_icons/')
    def __str__(self):
        return f"Type :{self.vehicle_type}"
    


    
from django.contrib import admin
from parking.models import ParkingArea,VehicleInfo,ParkingGuard
# admin.site.register(ParkingSpace)
# Register your models here.
admin.site.register([ParkingArea,VehicleInfo,ParkingGuard])
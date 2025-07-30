# urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from parking.api.views import ParkingAreaViewSet,VehicleInfoViewSet

router = DefaultRouter()
router.register(r'parking-areas', ParkingAreaViewSet, basename='parkingarea')
router.register(r'vehicle-info', VehicleInfoViewSet, basename='vehicleinfo')


urlpatterns = [
    path('', include(router.urls)),
]

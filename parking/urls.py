from django.urls import path
from rest_framework.routers import DefaultRouter

from parking.api.views import ParkingAreaViewSet, VehicleInfoViewSet

router = DefaultRouter()
router.register(r'parking-areas', ParkingAreaViewSet, basename='parking-area')
router.register(r'vehicle-info', VehicleInfoViewSet, basename='vehicle-info')

urlpatterns = router.urls

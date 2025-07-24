# urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from parking.api.views import ParkingAreaViewSet

router = DefaultRouter()
router.register(r'parking-areas', ParkingAreaViewSet, basename='parkingarea')

urlpatterns = [
    path('', include(router.urls)),
]

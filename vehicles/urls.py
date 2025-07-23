# vehicles/api/urls.py

from rest_framework import routers
from vehicles.api.views import VehicleTypeViewSet

router = routers.DefaultRouter()
router.register(r'vehicle-types', VehicleTypeViewSet, basename='vehicle-type')

urlpatterns = router.urls

# vehicles/api/urls.py

from rest_framework import routers
from vehicles.api.views import VehicleTypeView

router = routers.DefaultRouter()
router.register(r'vehicle-types', VehicleTypeView, basename='vehicle-type')

urlpatterns = router.urls

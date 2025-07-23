from rest_framework import serializers
from vehicles.models import VehicleType

class VehicleTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehicleType
        # fields = "__all__"
        exclude = ["is_active","is_deleted","deleted_at","created_at","updated_at"]
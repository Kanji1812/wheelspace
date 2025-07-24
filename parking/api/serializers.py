from rest_framework import serializers
from parking.models import ParkingArea, VehicleInfo, ParkingGuard
from vehicles.models import VehicleType
from users.models import User
from django.db import transaction
import json

class ParkingAreaSerializer(serializers.ModelSerializer):
    legal_doc = serializers.FileField(required=False)

    class Meta:
        model = ParkingArea
        exclude = ["is_active","is_deleted","deleted_at","created_at","updated_at","created_by","updated_by"]
    

    

from rest_framework import serializers
from parking.models import ParkingArea, VehicleInfo, ParkingGuard
from vehicles.models import VehicleType
from users.models import User
from django.db import transaction
import json

class VehicleInfoSerializer(serializers.ModelSerializer):
    vehicle_type_name = serializers.CharField(source='vehicle_type.name', read_only=True)
    rate_per_hour = serializers.SerializerMethodField()

    class Meta:
        model = VehicleInfo
        fields = ['id', 'vehicle_type', 'vehicle_type_name', 'capacity', 'rate_per_hour', 'available_count']

    def get_rate_per_hour(self, obj):
        return float(obj.rate_per_hour)
    
class GuardUserSerializer(serializers.ModelSerializer):
    user_type = serializers.CharField(default='guard', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'full_name', 'user_type', 'phone_number', 'age', 'email']


class ParkingAreaSerializer(serializers.ModelSerializer):
    legal_doc = serializers.FileField(required=False)
    slots = VehicleInfoSerializer(many=True, read_only=True) 
    guards = serializers.SerializerMethodField()

    class Meta:
        model = ParkingArea
        exclude = ["is_active", "is_deleted", "deleted_at", "created_at", "updated_at", "created_by", "updated_by"]

    def get_guards(self, obj):
        guards = ParkingGuard.objects.filter(parking_area=obj).select_related('guard_user')
        return GuardUserSerializer([g.guard_user for g in guards], many=True).data


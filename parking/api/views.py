# views.py

import json
from rest_framework import viewsets, permissions, status
from rest_framework.parsers import MultiPartParser, JSONParser, FormParser
from parking.models import ParkingArea, ParkingGuard,VehicleInfo
from parking.api.serializers import ParkingAreaSerializer
# from users.api.serializers import 
from base.utils.permissions import IsOwner
import json
from base.utils.standardized_response import api_response
from users.models import User
from vehicles.models import VehicleType
from django.db import transaction

class ParkingAreaViewSet(viewsets.ModelViewSet):
    queryset = ParkingArea.objects.filter(is_verified=True)
    serializer_class = ParkingAreaSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]
    parser_classes = [MultiPartParser, JSONParser, FormParser]

    def create(self, request, *args, **kwargs):
        data = request.data.copy()

        try:
            vehicle_infos = json.loads(data.get("vehicle_info", "[]")) if isinstance(data.get("vehicle_info"), str) else data.get("vehicle_info", [])
            parking_guards = json.loads(data.get("parking_guard", "[]")) if isinstance(data.get("parking_guard"), str) else data.get("parking_guard", [])
        except json.JSONDecodeError:
            return api_response({}, "Invalid JSON format in nested fields", status=400)

        data["vehicle_info"] = vehicle_infos
        data["parking_guard"] = parking_guards

        serializer = self.get_serializer(data=data)
        if not serializer.is_valid():
            return api_response(serializer.errors, "Validation failed", status=400)

        with transaction.atomic():
            instance = serializer.save(owner=request.user,created_by=request.user,updated_by=request.user)

            # Save vehicle info
            for vehicle_info in vehicle_infos:
                vehicle_type_id = int(vehicle_info.get('vehicle_type', 0))
                capacity = vehicle_info.get('capacity', 0)
                rate_per_hour = vehicle_info.get('rate_per_hour', 0)
                available_count = vehicle_info.get('available_count', 0)

                if not VehicleType.objects.filter(id=vehicle_type_id).exists():
                    return api_response({"vehicle_type": "Invalid vehicle type"}, "Enter a valid Vehicle Type", status=400)
                if capacity <= 0:
                    return api_response({"capacity": "Invalid capacity"}, "Enter a valid capacity", status=400)
                if rate_per_hour <= 0:
                    return api_response({"rate_per_hour": "Invalid Rate Per Hour"}, "Enter a valid Rate Per Hour", status=400)
                if available_count <= 0:
                    return api_response({"available_count": "Invalid Available Count"}, "Enter a valid Available Count", status=400)

                VehicleInfo.objects.create(
                    parking_area=instance,
                    vehicle_type_id=vehicle_type_id,
                    capacity=capacity,
                    rate_per_hour=rate_per_hour,
                    available_count=available_count,
                    created_by=request.user,
                    updated_by=request.user
                )

            # Save parking guards
            for guard in parking_guards:
                full_name = guard.get('full_name', '').strip()
                email = guard.get('email', '').strip()
                phone_number = guard.get('phone_number', '').strip()
                age = guard.get('age', 0)

                if not full_name:
                    return api_response({"full_name": "Invalid Full Name"}, "Enter a valid Full Name", status=400)
                if not isinstance(email, str) or User.objects.filter(email=email).exists():
                    return api_response({"email": "Enter a valid and unused email."}, "Enter a valid and unused email", status=400)
                if len(phone_number) < 10 or User.objects.filter(phone_number=phone_number).exists():
                    return api_response({"phone_number": "Enter a valid phone number."}, "Enter a valid phone number", status=400)
                if not isinstance(age, int) or age < 17:
                    return api_response({"age": "Enter a valid age."}, "Enter a valid age.", status=400)

                user = User.objects.create(
                    full_name=full_name,
                    email=email,
                    phone_number=phone_number,
                    age=age,
                    user_type="guard"
                    
                )
                user.set_password(email)  # Temporary password
                user.save()
                ParkingGuard.objects.create(
                    parking_area=instance,
                    guard_user=user,
                    created_by=request.user,
                    updated_by=request.user
                )

        return api_response(self.get_serializer(instance).data, "Parking area created", status=201)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset().filter(owner=request.user))
        serializer = self.get_serializer(queryset, many=True)
        return api_response(serializer.data, "Parking areas retrieved", status=200)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return api_response(serializer.data, "Parking area detail", status=200)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        data = request.data.copy()

        try:
            data["vehicle_info"] = json.loads(data["vehicle_info"]) if isinstance(data.get("vehicle_info"), str) else data.get("vehicle_info", [])
            data["parking_guard"] = json.loads(data["parking_guard"]) if isinstance(data.get("parking_guard"), str) else data.get("parking_guard", [])
        except json.JSONDecodeError:
            return api_response({}, "Invalid JSON format in nested fields", status=400)

        serializer = self.get_serializer(instance, data=data, partial=partial)
        if serializer.is_valid():
            instance = serializer.save()
            return api_response(self.get_serializer(instance).data, "Updated successfully", status=200)
        return api_response(serializer.errors, "Update failed", status=400)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return api_response(message="Parking area deleted", status=204)

import json
from rest_framework import viewsets, permissions, status
from rest_framework.parsers import MultiPartParser, JSONParser, FormParser
from parking.models import ParkingArea, ParkingGuard,VehicleInfo
from parking.api.serializers import GuardUserSerializer, ParkingAreaSerializer, VehicleInfoSerializer
from base.utils.permissions import IsOwner, IsOwnerOrIsAdmin
import json
from base.utils.standardized_response import api_response
from users.models import User
from vehicles.models import VehicleType
from django.db import transaction
from django.core.exceptions import ValidationError
from rest_framework.exceptions import APIException

class ParkingAreaViewSet(viewsets.ModelViewSet):
    queryset = ParkingArea.objects.all()
    serializer_class = ParkingAreaSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrIsAdmin]
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

        try:
            with transaction.atomic():
                instance = serializer.save(
                    owner=request.user,
                    created_by=request.user,
                    updated_by=request.user
                )

                # Save vehicle info
                for vehicle_info in vehicle_infos:
                    vehicle_type_id = int(vehicle_info.get('vehicle_type', 0))
                    capacity = vehicle_info.get('capacity', 0)
                    rate_per_hour = vehicle_info.get('rate_per_hour', 0)
                    available_count = vehicle_info.get('available_count', 0)

                    if not VehicleType.objects.filter(id=vehicle_type_id).exists():
                        raise ValidationError("Enter a valid Vehicle Type")
                    if not isinstance(capacity, int) or capacity <= 0:
                        raise ValidationError("Enter a valid capacity")
                    if not isinstance(rate_per_hour, (int, float)) or rate_per_hour <= 0:
                        raise ValidationError("Enter a valid rate per hour")
                    if not isinstance(available_count, int) or available_count <= 0:
                        raise ValidationError("Enter a valid available count")

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
                        raise ValidationError("Enter a valid full name")
                    if not isinstance(email, str) or User.objects.filter(email=email).exists():
                        raise ValidationError("Enter a valid and unused email")
                    if len(phone_number) < 10 or User.objects.filter(phone_number=phone_number).exists():
                        raise ValidationError("Enter a valid phone number")
                    if not isinstance(age, int) or age < 17:
                        raise ValidationError("Enter a valid age")

                    user = User.objects.create(
                        full_name=full_name,
                        email=email,
                        phone_number=phone_number,
                        age=age,
                        user_type="guard"
                    )
                    user.set_password(email)  # temp password
                    user.save()

                    ParkingGuard.objects.create(
                        parking_area=instance,
                        guard_user=user,
                        created_by=request.user,
                        updated_by=request.user
                    )

        except ValidationError as ve:
            return api_response({}, f" {str(ve)}", status=400)
        except Exception as e:
            return api_response({}, f" {str(e)}", status=500)

        return api_response(self.get_serializer(instance).data, "Parking area created", status=201)

    def list(self, request, *args, **kwargs):
        if request.user.user_type == "owner":
            queryset = ParkingArea.objects.filter(owner= request.user)
        else :
            queryset = ParkingArea.objects.all()
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

class VehicleInfoViewSet(viewsets.ModelViewSet):
    queryset= VehicleInfo.objects.all()
    serializer_class= VehicleInfoSerializer
    permission_classes= [permissions.IsAuthenticated, IsOwnerOrIsAdmin]

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return api_response(serializer.data, "Vehicle Info detail", status=200)

    def list(self, request, *args, **kwargs):
        queryset = VehicleInfo.objects.all()
        serializer = self.get_serializer(queryset, many=True)
        return api_response(serializer.data, "Vehicle Info retrieved", status=200)


class GuardUserViewSet(viewsets.ModelViewSet):
    queryset= User.objects.all()
    serializer_class= GuardUserSerializer
    permission_classes= [permissions.IsAuthenticated, IsOwnerOrIsAdmin]

    
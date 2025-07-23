from vehicles.api.serializers import VehicleTypeSerializer
from rest_framework.response import Response
from vehicles.models import VehicleType
from rest_framework import viewsets    
from rest_framework.decorators import action
from base.utils.standardized_response import api_response

class VehicleTypeViewSet(viewsets.ModelViewSet):
    serializer_class = VehicleTypeSerializer

    def get_queryset(self):
        return VehicleType.objects.filter(is_deleted=False)
    
    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        return api_response(response.data, message="Vehicle type created successfully", status=response.status_code)

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        return api_response(response.data, message="Vehicle types fetched successfully", status=response.status_code)

    def retrieve(self, request, *args, **kwargs):
        response = super().retrieve(request, *args, **kwargs)
        return api_response(response.data, message="Vehicle type fetched successfully", status=response.status_code)

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        return api_response(response.data, message="Vehicle type updated successfully", status=response.status_code)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return api_response(serializer.data, message="Vehicle type partially updated successfully", status=200)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.soft_delete()
        return api_response(data=None, message="Vehicle type deleted successfully", status=204)

    @action(detail=True, methods=['post'])
    def restore(self, request, pk=None):
        instance = self.get_object()
        instance.restore()
        serializer = self.get_serializer(instance)
        return api_response(serializer.data, message="Vehicle type restored successfully", status=200)

from rest_framework import status, viewsets
from rest_framework.decorators import action
from base.utils.standardized_response import api_response
from vehicles.api.serializers import VehicleTypeSerializer
from vehicles.models import VehicleType

class VehicleTypeViewSet(viewsets.ModelViewSet):
    serializer_class = VehicleTypeSerializer

    def get_queryset(self):
        return VehicleType.objects.filter(is_deleted=False)

    def _custom_response(self, response, message):
        return api_response(
            data=response.data,
            message=message,
            status=response.status_code,
            success=True
        )

    def create(self, request, *args, **kwargs):
        return self._custom_response(
            super().create(request, *args, **kwargs),
            "Vehicle type created successfully"
        )

    def list(self, request, *args, **kwargs):
        return self._custom_response(
            super().list(request, *args, **kwargs),
            "Vehicle types fetched successfully"
        )

    def retrieve(self, request, *args, **kwargs):
        return self._custom_response(
            super().retrieve(request, *args, **kwargs),
            "Vehicle type fetched successfully"
        )

    def update(self, request, *args, **kwargs):
        return self._custom_response(
            super().update(request, *args, **kwargs),
            "Vehicle type updated successfully"
        )

    def partial_update(self, request, *args, **kwargs):
        return self._custom_response(
            super().partial_update(request, *args, **kwargs),
            "Vehicle type partially updated successfully"
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.soft_delete()
        return api_response(
            data=None,
            message="Vehicle type deleted successfully",
            status=status.HTTP_200_OK,
            success=True
        )

    @action(detail=True, methods=["post"])
    def restore(self, request, pk=None):
        instance = self.get_object()
        instance.restore()
        serializer = self.get_serializer(instance)
        return api_response(
            serializer.data,
            message="Vehicle type restored successfully",
            status=status.HTTP_200_OK,
            success=True
        )

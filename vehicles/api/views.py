from django.shortcuts import render
from vehicles.api.serializers import VehicleTypeSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from vehicles.models import VehicleType
from rest_framework import viewsets
    
class VehicleTypeView(viewsets.ModelViewSet):
    queryset = VehicleType.objects.all()
    serializer_class = VehicleTypeSerializer

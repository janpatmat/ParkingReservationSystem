# serializers.py
from rest_framework import serializers
from .models import parkingLocation, parkingSpot, reserveTable, Archive

class ParkingLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = parkingLocation
        fields = '__all__'

class parkingSpotSerializer(serializers.ModelSerializer):
    class Meta:
        model = parkingSpot
        fields = '__all__'
        extra_kwargs = {
            'reserveStatus': {'allow_null': True, 'required': False},
            'occupied': {'allow_null': True, 'required': False},
            'location': {'allow_null': True, 'required': False},
        }

class ReserveTableInitializer(serializers.ModelSerializer):
    class Meta:
        model = reserveTable
        fields = '__all__'


class ArchiveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Archive
        fields = '__all__'
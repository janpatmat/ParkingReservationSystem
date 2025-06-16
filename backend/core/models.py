from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth.models import User
class parkingLocation(models.Model):
    locationID = models.AutoField(primary_key=True)
    locationName = models.CharField(max_length=255)

    class Meta:
        db_table = 'parkingLocation'

class reserveTable(models.Model):
    reserveID = models.AutoField(primary_key=True)
    spotID = models.ForeignKey('parkingSpot', on_delete=models.SET_DEFAULT, null=True, blank=True, default=None)
    customerID = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    date_in = models.DateTimeField()
    date_out = models.DateTimeField()

    class Meta:
        db_table = 'reserveTable'



class approvedreserveTable(models.Model):
    approvedreserveID = models.AutoField(primary_key=True)
    spotID = models.ForeignKey('parkingSpot', on_delete=models.SET_NULL, null=True, blank=True)
    customerID = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    date_in = models.DateTimeField()
    date_out = models.DateTimeField()

    class Meta:
        db_table = 'approvedreserveTable'





class parkingSpot(models.Model):
    spotID = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    
    location = models.ForeignKey('parkingLocation', on_delete=models.CASCADE, null=True, blank=True)
    


    class Meta:
        db_table = 'parkingSpot'

class customer(models.Model):
    customerID = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)




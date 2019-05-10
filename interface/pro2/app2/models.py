"""
create your models here
"""
from django.db import models


class User1(models.Model):
    first_name = models.CharField(max_length=128)
    last_name = models.CharField(max_length=128)
    email = models.EmailField(max_length=264, unique=True) #to avoid duplicates

class Measure(models.Model):
    name = models.CharField(max_length=150, unique=True)
    cost = models.IntegerField()
    lifetime = models.IntegerField()
    electricity = models.IntegerField()
    diesel_oil = models.IntegerField()
    motor_gasoline = models.IntegerField()
    natural_gas = models.IntegerField()
    biomass = models.IntegerField()
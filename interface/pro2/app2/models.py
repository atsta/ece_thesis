"""
create your models here
"""
from django.db import models

#class fcba(models.Model):

#class scba(models.Model):

class Energy_Conservation(models.Model):
    # article 3
    electricity3 = models.IntegerField(default=0)
    diesel_oil3 = models.IntegerField(default=0)
    motor_gasoline3 = models.IntegerField(default=0)
    natural_gas3 = models.IntegerField(default=0)
    biomass3 = models.IntegerField(default=0)

    # article 7
    electricity7 = models.IntegerField(default=0)
    diesel_oil7 = models.IntegerField(default=0)
    motor_gasoline7 = models.IntegerField(default=0)
    natural_gas7 = models.IntegerField(default=0)
    biomass7 = models.IntegerField(default=0)

class Measure(Energy_Conservation):
    name = models.CharField(max_length=150, unique=True)
    cost = models.IntegerField()
    lifetime = models.IntegerField()
    description = models.TextField(default=' ')
    category = models.CharField()
    measure_type = models.CharField()
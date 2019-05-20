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

    class Meta:
        abstract = True

class Benefits(models.Model):
    energy_savings = models.CharField(max_length=150, default=' ')
    maintenance = models.CharField(max_length=150, default=' ')
    externalities = models.CharField(max_length=150, default=' ')
    value_growth = models.CharField(max_length=150, default=' ') #just for buildings
    work_efficiency = models.CharField(max_length=150, default=' ')
    employability = models.CharField(max_length=150, default=' ')

class Costs(models.Model):
    equipment = models.CharField(max_length=150, default=' ')
    management = models.CharField(max_length=150, default=' ')
    reduced_income = models.CharField(max_length=150, default=' ')


class Measure(Energy_Conservation):
    name = models.CharField(max_length=150, unique=True)
    cost = models.IntegerField()
    lifetime = models.IntegerField()
    description = models.TextField(default=' ')
    category = models.CharField(max_length=150, default=' ')
    measure_type = models.CharField(max_length=150, default=' ')
    benefits = models.ManyToManyField(Benefits)
    costs = models.ManyToManyField(Costs)

class Social(models.Model):
    measure = models.CharField(max_length=150, default=' ')
    costs = models.ManyToManyField(Costs)
    benefits = models.ManyToManyField(Benefits)

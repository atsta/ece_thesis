"""
create your models here
"""
from django.db import models

from datetime import datetime  

#class fcba(models.Model):

#class scba(models.Model):

CATEGORY_CHOICES = [
    ("industry", "Industry"),
    ("household", "Household-Houses"),
    ("business", "Business"),
    ("private_transport", "Private Trasport"),
    ("public_transport", "Public Transport"),
    ("public_buildings", "Public Buildings"),

]
TYPE_CHOICES = [
    ("technical", "Technical"),
    ("behavioral", "Behavioral"),
]
class Measure(models.Model):
    name = models.CharField(max_length=150, unique=True, primary_key=True)
    cost = models.FloatField(default=0)
    lifetime = models.IntegerField(default=0)
    description = models.TextField(default=None)
    category = models.CharField(max_length=150, default=None, choices=CATEGORY_CHOICES)
    measure_type = models.CharField(max_length=150, default=None, choices=TYPE_CHOICES)
    
    def __str__(self):
        return "%s Measure: " % self.name

        
class Energy_Conservation(models.Model):
    measure = models.OneToOneField(Measure, 
                                on_delete=models.CASCADE,
                                primary_key=True, default=None)
    # article 3
    electricity3 = models.FloatField(default=0)
    diesel_oil3 = models.FloatField(default=0)
    motor_gasoline3 = models.FloatField(default=0)
    natural_gas3 = models.FloatField(default=0)
    biomass3 = models.FloatField(default=0)

    # article 7
    electricity7 = models.FloatField(default=0)
    diesel_oil7 = models.FloatField(default=0)
    motor_gasoline7 = models.FloatField(default=0)
    natural_gas7 = models.FloatField(default=0)
    biomass7 = models.FloatField(default=0)

    def __str__(self):
        return "%s Energy conservation of measure: " % self.measure.name

class Benefits(models.Model):
    measure = models.OneToOneField(Measure, 
                                on_delete=models.CASCADE,
                                primary_key=True, default=None)
    maintenance = models.FloatField(max_length=150, null=True)
    externalities = models.FloatField(max_length=150, default=0, null=True, editable=True)
    value_growth = models.FloatField(max_length=150, default=0, null=True) #just for buildings
    work_efficiency = models.FloatField(max_length=150, default=0, null=True)
    employability = models.FloatField(max_length=150, default=0, null=True)
    other_benefits = models.FloatField(max_length=150, default=0, null=True)

    def __str__(self):
        return "%s Benefits of measure: " % self.measure.name

class Costs(models.Model):
    measure = models.OneToOneField(Measure, 
                                on_delete=models.CASCADE,
                                primary_key=True, default=None)
    management = models.FloatField(max_length=150, default=0, null=True)
    maintenance = models.FloatField(max_length=150, default=0, null=True)
    reduced_income = models.FloatField(max_length=150, default=0, null=True)
    other_costs = models.FloatField(max_length=150, default=0, null=True)
    
    def __str__(self):
        return "%s Costs of measure: " % self.measure.name

class Portfolio(models.Model):
    name = models.CharField(primary_key=True, max_length=150, unique=True, default=None)
    genre = models.CharField(max_length=150, default=None)
    analysis_pieces = models.CharField(max_length=300, default=None)
    time_added = models.DateTimeField(default=datetime.now, blank=True)


class Social(models.Model):
    name = models.CharField(primary_key=True, max_length=150, unique=True, default=None)
    measure = models.ForeignKey(Measure, on_delete=models.CASCADE, default=None)
    time_added = models.DateTimeField(default=datetime.now, blank=True)

    #selected costs and benefits for this analysis
    costs = models.CharField(max_length=150, default=None, null=True)
    benefits = models.CharField(max_length=150, default=None, null=True)

    #analysis specs
    discount_rate = models.FloatField(default=0.03)
    analysis_period = models.IntegerField(default=25)
    
    #analysis results
    npv = models.FloatField(default=0, null=True)
    b_to_c = models.FloatField(default=0, null=True)
    irr = models.FloatField(default=0, null=True)
    dpbp = models.FloatField(default=0, null=True)

class Financial(models.Model):
    name = models.CharField(primary_key=True, max_length=150, unique=True, default=None)
    measure = models.ForeignKey(Measure, on_delete=models.CASCADE, default=None)
    time_added = models.DateTimeField(default=datetime.now, blank=True)

    #selected costs and benefits for this analysis
    costs = models.CharField(max_length=150, default=None, null=True)
    benefits = models.CharField(max_length=150, default=None, null=True)

    #analysis specs
    discount_rate = models.FloatField(default=0.03)
    analysis_period = models.IntegerField(default=25)
    
    #analysis results
    npv = models.FloatField(default=0, null=True)
    b_to_c = models.FloatField(default=0, null=True)
    irr = models.FloatField(default=0, null=True)
    dpbp = models.FloatField(default=0, null=True)

class Perspective(models.Model):
    name = models.CharField(primary_key=True, max_length=150, unique=True, default=None)
    measure = models.ForeignKey(Measure, on_delete=models.CASCADE, default=None)
    time_added = models.DateTimeField(default=datetime.now, blank=True)


    discount_rate = models.FloatField(default=0.03)
    analysis_period = models.IntegerField(default=25)
    financial_mechanisms = models.CharField(max_length=150, default=None, null=True)

    #selected costs and benefits for this analysis
    costs = models.CharField(max_length=150, default=None, null=True)
    benefits = models.CharField(max_length=150, default=None, null=True)

    npv = models.FloatField(default=0, null=True)
    b_to_c = models.FloatField(default=0, null=True)
    irr = models.FloatField(default=0, null=True)
    dpbp = models.FloatField(default=0, null=True)
    spbp = models.FloatField(default=0, null=True)

class Esco(models.Model):
    perspective_analysis = models.ForeignKey(Perspective, on_delete=models.CASCADE, default=None)
    discount_rate = models.FloatField(default=0.03)
    
    benefit_share = models.FloatField(default=0, null=True)
    cost_share = models.FloatField(default=0, null=True)
    contract_period = models.IntegerField(default=0, null=True)

    npv = models.FloatField(default=0, null=True)
    b_to_c = models.FloatField(default=0, null=True)
    irr = models.FloatField(default=0, null=True)
    dpbp = models.FloatField(default=0, null=True)
    spbp = models.FloatField(default=0, null=True)

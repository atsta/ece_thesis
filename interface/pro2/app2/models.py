"""
create models
"""
from django.db import models


class User1(models.Model):
    """
    create your models here
    """
    first_name = models.CharField(max_length=128)
    last_name = models.CharField(max_length=128)
    email = models.EmailField(max_length=264, unique=True) #to avoid duplicates

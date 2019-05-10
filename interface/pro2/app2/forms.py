from django import forms
from app2.models import User1
from app2.models import Measure
from django.core import validators

class NewUserForm(forms.ModelForm):
    class Meta:
        model = User1
        fields = '__all__'

class NewMeasureForm(forms.ModelForm):
    class Meta:
        model = Measure
        fields = '__all__'

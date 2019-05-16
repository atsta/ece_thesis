from django import forms
from app2.models import Measure
from django.core import validators


class NewMeasureForm(forms.ModelForm):
    class Meta:
        model = Measure
        fields = '__all__'


class SomeInput(forms.Form):
    measure = forms.CharField(max_length=15)
    analysis = forms.CharField(max_length=15)

#class ChooseMeasures(forms.Form):

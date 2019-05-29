from django import forms
from app2.models import Measure
from django.core import validators, serializers


class NewMeasureForm(forms.ModelForm):
    class Meta:
        model = Measure
        fields = '__all__'

        def get_measure(self):
            return self.model


class SomeInput(forms.Form):
    measure = forms.CharField(max_length=15)
    analysis = forms.CharField(max_length=15)

#class ChooseMeasures(forms.Form):

MECHANISM1_CHOICES = [
    ('subsidy', 'Subsidy'),
    ("tax_exemption", "Tax Exemption"), 
    ("loan", "Loan of beneficiary"),
    ("increase_factor", "Increase of depreciation factor of fixed assets"),
    ("energy_contract", "Energy Contract"),
]

MECHANISM2_CHOICES = [
    ('subsidy', 'Subsidy'),
    ("tax_exemption", "Tax Exemption"), 
    ("loan", "Loan of beneficiary"),
    ("increase_factor", "Increase of depreciation factor of fixed assets"),
]

MECHANISM3_CHOICES = [
    ('subsidy', 'Subsidy'),
    ("tax_exemption", "Tax Exemption"), 
    ("loan", "Loan of beneficiary"),
    ("energy_contract", "Energy Contract"),
]

MECHANISM4_CHOICES = [
    ('subsidy', 'Subsidy'),
    ("tax_exemption", "Tax Exemption"), 
    ("loan", "Loan of beneficiary"),
]

class MechForm1(forms.Form):
    chosen_mechanism = forms.CharField(label="Financial Mechanism", widget=forms.Select(choices=MECHANISM1_CHOICES))

class MechForm2(forms.Form):
    chosen_mechanism = forms.CharField(label="Financial Mechanism", widget=forms.Select(choices=MECHANISM2_CHOICES))

class MechForm3(forms.Form):
    chosen_mechanism = forms.CharField(label="Financial Mechanism", widget=forms.Select(choices=MECHANISM3_CHOICES))

class MechForm4(forms.Form):
    chosen_mechanism = forms.CharField(label="Financial Mechanism", widget=forms.Select(choices=MECHANISM4_CHOICES))

class LoanForm(forms.Form):
    own_funds_rate = forms.FloatField()
    annual_rate = forms.FloatField()
    subsidized_interest_rate = forms.FloatField()
    loan_period = forms.IntegerField(initial=0, required=False)
    grace_period = forms.IntegerField(initial=0)

class FactorForm(forms.Form):
    depreciation_tax_rate = forms.FloatField()
    tax_lifetime = forms.IntegerField()

CRITERION_CHOICES = [
    ('profit', 'Profit'),
    ("irr", "IRR"), 
    ("spbp", "Simple Payback Period"),
    ("dpbp", "Discounted Payback Period"),
]

SATISFY_CRITERION_CHOICES = [
    ("contract_period", "Contract Period Variation"), 
    ("benefit_share", "Benefit Share Percentage"),
    ("cost_esco", "Cost Percentage of ESCO"),
]

class ContractForm(forms.Form):
    chosen_criterion = forms.CharField(label="Choose participation criterion for ESCO", widget=forms.Select(choices=CRITERION_CHOICES))
    criterion_satisfaction = forms.CharField(label="Criterion will be satisfied by:", widget=forms.Select(choices=SATISFY_CRITERION_CHOICES))
    discount_rate = forms.FloatField()
    
class CostStatisfy(forms.Form):
    contract_period = forms.IntegerField()
    benefit_share_rate = forms.FloatField()

class PeriodSatisfy(forms.Form):
    cost_esco_rate = forms.FloatField()
    benefit_share_rate = forms.FloatField()

class BenefitSatisfy(forms.Form):
    contract_period = forms.IntegerField()
    cost_esco_rate = forms.FloatField()

class ProfitInput(forms.Form):
    profit = forms.FloatField()

class IrrInput(forms.Form):
    irr = forms.FloatField()

class SInput(forms.Form):
    spbp = forms.FloatField()

class DInput(forms.Form):
    dpbp = forms.FloatField()

class EscoLoan(forms.Form):
    own_funds_rate = forms.FloatField()
    annual_rate = forms.FloatField()
    subsidized_interest_rate = forms.FloatField()
    loan_period = forms.IntegerField(initial=0, required=False)
    grace_period = forms.IntegerField(initial=0)
from django import forms
from app2.models import User1
from django.core import validators

class NewUserForm(forms.ModelForm):
    class Meta:
        model = User1
        fields = '__all__'


#just a typical value check 
#def check_for_z(value):
#    if value[0].lower() != 'z':
#        raise forms.ValidationError('Needs to start with z')

#FormName is a subclass of Django's Form class
#This is thw way to create inheritance
"""
class FormName(forms.Form):
    name = forms.CharField(validators=[check_for_z])
    email = forms.EmailField()
    #verification via multi input
    verify_email = forms.EmailField(label='Enter your email again:')    
    text = forms.CharField(widget = forms.Textarea)
    boatcatcher = forms.CharField(required= False,
            widget=forms.HiddenInput,
            validators=[validators.MaxLengthValidator(0)]) 
            #replace validation method with pre made validators

    
    def clean(self):
        all_clean_data = super().clean()
        email = all_clean_data['email']
        vmail = all_clean_data['verify_email']
        #check whether email match
        if email!=vmail:
            raise forms.ValidationError('Make sure your email is correct')
            

    #simple validation method
    def clean_botcatcher(self):
        botcatcher = self.cleaned_data['botcatcher']
        if len(botcatcher) > 0:
            raise forms.ValidationError("Just catched a bot!")
        return botcatcher
    
"""
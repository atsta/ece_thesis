from django.shortcuts import render
#from django.http import HttpResponse

from app2.forms import NewUserForm
#from app2.models import User1


#from . import forms

# Create your views here.

#home page 
def index(request):
    return render(request,'app2/index.html')

#users view
def users(request):
        #form is an instance of class NewUserForm
        form = NewUserForm()
        
        #check is user is submitting information and have to POST the information
        if request.method == "POST":
                form = NewUserForm(request.POST)
                #then if the data is valid save the form in the db and return the index page view
                if form.is_valid():
                        form.save(commit=True)
                        return index(request)
                else: 
                        print('Error: Invalid form')
        
        return render(request,'app2/users.html',{'form':form})





"""   
#basic form view 
def form_name_view(request):
    form = forms.FormName() #just created an instance of formName class 
    
    if request.method == 'POST':
        form = forms.FormName(request.POST)

        if form.is_valid():
            #print data at terminal
            print('validation success')
            print('Name: '+ form.cleaned_data['name'])
            print('Email: '+ form.cleaned_data['email'])
            print('Text: '+ form.cleaned_data['text'])


   
    form_dict = {'form': form}
    return render(request, 'app2/form_page.html', context=form_dict)
    """
from django.shortcuts import render

from app2.forms import NewUserForm 
from app2.forms import NewMeasureForm

# Create your views here.

# home page view 
def index(request):
    return render(request,'app2/index.html')


# users view
def users(request):
        # form is an instance of class NewUserForm
        form = NewUserForm()
        
        # check is user is submitting information 
        # and have to POST the information
        if request.method == "POST":
                form = NewUserForm(request.POST)
                # then if the data is valid save the form in the db 
                # and return the index page view
                if form.is_valid():
                        form.save(commit=True)
                        return index(request)
                else: 
                        print('Error: Invalid form')
        
        return render(request,'app2/users.html', {'form':form})


def measure(request):
        form = NewMeasureForm()
        if request.method == "POST":
                form = NewMeasureForm(request.POST)
                if form.is_valid():
                        form.save(commit=True)
                        return index(request)
                else: 
                        print('Error: Invalid form')
                        
        return render(request,'app2/measure.html', {'form': form})
        



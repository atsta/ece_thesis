from django.shortcuts import render
from app2.models import User1
#from django.http import HttpResponse

# Create your views here.

#home page 
def index(request):
    return render(request,'app2/index.html')

#users view
def users(request):

    user_list = User1.objects.order_by('first_name')
    user_dict = {'users': user_list}
    return render(request, 'app2/users.html', context=user_dict)


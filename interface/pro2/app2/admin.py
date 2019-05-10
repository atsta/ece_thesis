from django.contrib import admin
from app2.models import User1
from app2.models import Measure

# Register your models here.
# in oreder to see them when logged in as admin 
admin.site.register(User1)
admin.site.register(Measure)

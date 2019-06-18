from django.contrib import admin
from app2.models import Measure, Social, Portfolio, Financial, Perspective

# Register your models here.
# in oreder to see them when logged in as admin 
admin.site.register(Measure)
admin.site.register(Portfolio)
admin.site.register(Financial)
admin.site.register(Social)
admin.site.register(Perspective)

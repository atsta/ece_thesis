"""pro2 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf.urls import include, url

from app2 import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    path('admin/', admin.site.urls), 
    url(r'^measure/', views.measure, name='measure'),
    url(r'^analysis/', views.analysis, name='analysis'),
    url(r'^measure_search_results/', views.measure_search_results, name='measure_search_results'),
    url(r'^measure_search_results_investment/', views.measure_search_results_investment, name='measure_search_results_investment'),
    url(r'^grab_selected_results/', views.grab_selected_results, name='grab_selected_results'),
    url(r'^grab_selected_results_investment/', views.grab_selected_results_investment, name='grab_selected_results_investment'),
    url(r'^choose_costs_and_benefits/', views.choose_costs_and_benefits, name='choose_costs_and_benefits'),
    url(r'^choose_costs_and_benefits_investment/', views.choose_costs_and_benefits_investment, name='choose_costs_and_benefits_investment'),  
    url(r'^financial_mechanism_params/', views.financial_mechanism_params, name='financial_mechanism_params'),
    url(r'^grab_params_and_give_results/', views.grab_params_and_give_results, name='grab_params_and_give_results'),   
    url(r'^grab_params_and_proceed/$', views.grab_params_and_proceed, name='grab_params_and_proceed'),   
    url(r'^actor_choice/', views.actor, name='actor_choice'),
    url(r'^esco_params/', views.esco_params, name='esco_params'),
    url(r'^investment_analysis_results/', views.investment_analysis_results, name='investment_analysis_results'),
    url(r'^grab_esco_params/', views.grab_esco_params, name='grab_esco_params'),
    url(r'^investment_result_page/', views.investment_result_page, name='investment_result_page'),
    url(r'^scba_result_page/', views.social_result_page, name='scba_result_page'),
    url(r'^fcba_params_results/', views.fcba_params_results, name='fcba_params_results'),
    url(r'^fcba_result_page/', views.financial_result_page, name='fcba_result_page'),

]

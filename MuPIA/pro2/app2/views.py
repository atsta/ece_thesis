from django.shortcuts import render

from app2.forms import NewMeasureForm, MechForm1, MechForm2, MechForm3, MechForm4, LoanForm, FactorForm, ContractForm
from . import forms

from app2.models import Measure, Social, Energy_Conservation, Costs, Benefits, Portfolio

from modules import energy_measure, social_investment_analysis

import string
import random

def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
        return ''.join(random.choice(chars) for _ in range(size))

# Create your views here.

# home page view 
def index(request):
    return render(request,'app2/index.html')

def measure(request):
    return render(request,'app2/measure.html')

def actor(request):
    return render(request,'app2/actor_choice.html')


def analysis(request):
        form = NewMeasureForm()
        if request.method == "POST":
                form = NewMeasureForm(request.POST)
                if form.is_valid():
                        measure = form.save(commit=True)
                        e = Energy_Conservation(measure=measure, biomass3=13)
                        e.save()
                        c = Costs(measure=measure, equipment=measure.cost)
                        c.save()
                        b = Benefits(measure=measure)
                        b.save()
                        #return analysis(request)
                else: 
                        print('Error: Invalid form')
                        
        return render(request, 'app2/analysis.html', {'form': form})
        

def measure_search_results_investment(request):
        selected_category = request.POST.get('category')
        selected_type = request.POST.get('type')

        results = Measure.objects.filter(measure_type=selected_type)
        #, category=selected_category)

        request.session['category'] = selected_category
        request.session['type'] = selected_type

        return render(request, 'app2/actor_choice.html', {'results': results, 
                                                        'selected_category': selected_category, 
                                                        'selected_type': selected_type})
def measure_search_results(request):
        selected_category = request.POST.get('category')
        selected_type = request.POST.get('type')

        results = Measure.objects.filter(measure_type=selected_type)
        #, category=selected_category)
        
        return render(request, 'app2/measure.html', {'results': results, 
                                                        'selected_category': selected_category, 
                                                        'selected_type': selected_type})

def grab_selected_results_investment(request):
        selected = request.GET.getlist('measure')
        
        #create an analysis instance for every selected measure
        #create random names for every analysis instance
        
        #remove '\' from measure name
        for i in range(len(selected)):
                k = selected[i]
                k = k[:-1]
                selected[i] = k
        #print(selected)
        #op = Portfolio(name=id_generator(), genre ='social', analysis_pieces=[])
        #op.save()
        '''
        for element in selected:
                social[element] = id_generator()
                hip = Measure.objects.get(name=element)
                hop = Social(name=social[element], measure=hip)
                op.analysis_pieces.append(social[element])
                op.save()
                hop.save()
                
        request.session['dictionary'] = social
        request.session['list'] = selected
        print(social)
        '''
        return render(request, 'app2/investment_analysis.html', {'selected': selected})

def grab_selected_results(request):
        selected = request.GET.getlist('measure')
        
        #create an analysis instance for every selected measure
        #create random names for every analysis instance
        social = {}
        #remove '\' from measure name
        for i in range(len(selected)):
                k = selected[i]
                k = k[:-1]
                selected[i] = k
        #print(selected)
        op = Portfolio(name=id_generator(), genre ='social', analysis_pieces=[])
        op.save()
        for element in selected:
                social[element] = id_generator()
                hip = Measure.objects.get(name=element)
                hop = Social(name=social[element], measure=hip)
                op.analysis_pieces.append(social[element])
                op.save()
                hop.save()
                
        request.session['dictionary'] = social
        request.session['list'] = selected
        print(social)
        return render(request, 'app2/cba.html', {'selected': selected})

def choose_costs_and_benefits(request):
        selected = request.session['list']
        social = request.session['dictionary']
        costs = {}
        benefits = {}
        print(social)
        
        for item in selected:
                hip = Social.objects.get(name=social[item])
                
                #measure name0 -> benefit 
                #measure name1 -> cost
                benefit = "%s%s" % (item, "0")
                benefits[item] = request.POST.getlist(benefit)
                hip.benefits = benefits[item]
                
                cost = "%s%s" % (item, "1")
                costs[item] = request.POST.getlist(cost)
                hip.costs = costs[item]
                hip.save()
        return render(request, 'app2/cba_params_and_results.html', {'costs': costs, 'benefits': benefits})

def choose_costs_and_benefits_investment(request):
        selected_category = request.session['category']
        selected_type = request.session['type']
        
        print(selected_category)
        print(selected_type)

        
        if selected_type == "behavioral":
                form = MechForm4()             
        elif selected_category!="household" and selected_category!="public_transport" and selected_category!="private_transport":
                form = MechForm1()
        elif selected_category == "household":
                form = MechForm2()
        else: 
                form = MechForm3()

        return render(request, 'app2/investment_analysis_params.html', {'form': form })

def grab_params_and_proceed(request):
        selected_category = request.session['category']
        selected_type = request.session['type']
 
        if request.method == "POST":
                if selected_type == "behavioral":
                        form = MechForm4(request.POST)
                elif selected_category!="household" and selected_category!="public_transport" and selected_category!="private_transport":
                        form = MechForm1(request.POST)
                elif selected_category == "household":
                        form = MechForm2(request.POST)
                else:
                        form = MechForm3(request.POST)

                if form.is_valid():
                        print('ok')
                       
                        mechanism = form.cleaned_data['chosen_mechanism']
                        print(mechanism)
                        request.session['mechanism'] = mechanism
                        if mechanism == 'loan':
                                form1 = LoanForm() 
                                return render(request, 'app2/investment_analysis_params.html', {'form': form, 'form1': form1})
                        if mechanism == 'increase_factor':
                                form1 = FactorForm()
                                return render(request, 'app2/investment_analysis_params.html', {'form': form, 'form1': form1})
                        if mechanism == 'energy_contract':
                                form1 = ContractForm()
                                return render(request, 'app2/investment_analysis_params.html', {'form': form, 'form1': form1})
                        return render(request, 'app2/investment_analysis_params.html', {'form': form})
                else: 
                        print('Error: Invalid form')
        else:
                if selected_type == "behavioral":
                        form = MechForm4()             
                elif selected_category!="household" and selected_category!="public_transport" and selected_category!="private_transport":
                        form = MechForm1()
                elif selected_category == "household":
                        form = MechForm2()
                else: 
                        form = MechForm3()

        return render(request, 'app2/investment_analysis_params.html', {'form': form})

def financial_mechanism_params(request):        
        mechanism = request.session['mechanism']
        if mechanism == 'loan':
                if request.method == "POST":
                        form1 = LoanForm(request.POST)
                        if form1.is_valid():
                                annual = form1.cleaned_data['annual_rate']
                                print(annual)
                        return render(request, 'app2/investment_analysis_params.html', {'form1': form1})
        if mechanism == 'increase_factor':
                if request.method == "POST":
                        form1 = FactorForm(request.POST)
                        return render(request, 'app2/investment_analysis_params.html', {'form1': form1})
        if mechanism == 'energy_contract':
                if request.method == "POST":
                        form1 = ContractForm(request.POST)
                        return render(request, 'app2/investment_analysis_params.html', {'form1': form1})
        
        return render(request, 'app2/investment_analysis_params.html')

                
def grab_params_and_give_results(request):
        selected = request.session['list']
        social = request.session['dictionary']

        #print(selected)
        chose_lifetime = request.POST.getlist('lifetime')
        if chose_lifetime == []:
                analysis_period = request.POST.get('analysis_period')
        else:
                #tbd, for every measure selected
                analysis_period = 0
        discount_rate = request.POST.get('discount_rate')

        for item in selected:
                hip = Social.objects.get(name=social[item])
                hip.discount_rate = discount_rate
                hop = Measure.objects.get(name=item)
                if analysis_period == 0:
                        hip.analysis_period = hop.lifetime
                else: 
                        hip.analysis_period = analysis_period
                hip.save()
                energy_conservation = {
                        "electricity": 0,
                        "diesel_oil": 0,
                        "motor_gasoline": 0, 
                        "natural_gas": 0, 
                        "biomass": 0
                }
                opa = Energy_Conservation.objects.get(measure=hop)
                #opa.electricity3 = 25
                #opa.save()
                energy_conservation['electricity'] = opa.electricity3
                energy_conservation['diesel_oil'] = opa.diesel_oil3
                energy_conservation['motor_gasoline'] = opa.motor_gasoline3
                energy_conservation['natural_gas'] = opa.natural_gas3
                energy_conservation['biomass'] = opa.biomass3

                #print(energy_conservation['electricity'])
                externalities = []
                for i in range(0, 25):
                        externalities.insert(i, 2.11)
                cost = hop.cost
                lifetime = hop.lifetime
                #print(cost)
                scba = social_investment_analysis.Social(cost, lifetime, externalities, energy_conservation)

                hip.npv = scba.npv
                hip.b_to_c = scba.b_to_c
                hip.irr = scba.irr
                hip.dpbp = scba.dpbp
                hip.save()
         
        

        #scba = social_investment_analysis.Social(33800, 20, externalities, energy_conservation)
        #print(scba.pbp)
        #  print(scba.dpbp)
        return render(request, 'app2/cba_params_and_results.html', {'analysis_period': analysis_period, 'discount_rate': discount_rate})
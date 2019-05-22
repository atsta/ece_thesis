from django.shortcuts import render

from app2.forms import NewMeasureForm
from . import forms

from app2.models import Measure, Social, Energy_Conservation, Costs, Benefits

from modules import energy_measure, social_investment_analysis

# Create your views here.

# home page view 
def index(request):
    return render(request,'app2/index.html')

def measure(request):
    return render(request,'app2/measure.html')


def analysis(request):
        form = NewMeasureForm()
        if request.method == "POST":
                form = NewMeasureForm(request.POST)
                if form.is_valid():
                        form.save(commit=True)
                        e = Energy_Conservation(measure=form.get_measure(), biomass3=13)
                        e.save()
                        c = Costs(measure=form)
                        c.save()
                        b = Benefits(measure=form)
                        b.save()
                        #return analysis(request)
                else: 
                        print('Error: Invalid form')
                        
        return render(request, 'app2/analysis.html', {'form': form})
        

def measure_search_results(request):
        selected_category = request.GET.get('category')
        selected_type = request.GET.get('type')

        results = Measure.objects.filter(measure_type=selected_type)
        #, category=selected_category)
        #print(results)
        return render(request, 'app2/measure.html', {'results': results})

def grab_selected_results(request):
        selected = request.POST.getlist('measure')
        request.session['list'] = selected
        #print(selected)
        social = []
        for element in selected:
                #sprint(element)
                hip = Social(measure=element)
                hip.save()
                social.append(hip)
        return render(request, 'app2/cba.html', {'selected': selected})

def choose_costs_and_benefits(request):
        selected = request.session['list']
        costs = {}
        benefits = {}
        for item in selected:
                benefit = "%s%s" % (item, "0")
                benefits[item] = request.POST.getlist(benefit)
                cost = "%s%s" % (item, "1")
                costs[item] = request.POST.getlist(cost)
                #print(benefits[item])
                #print(costs[item])
        return render(request, 'app2/cba_params_and_results.html', {'costs': costs, 'benefits': benefits})


def grab_params_and_give_results(request):
        chose_lifetime = request.POST.getlist('lifetime')
        if chose_lifetime == []:
                analysis_period = request.POST.get('analysis_period')
        else:
                #tbd, for every measure selected
                analysis_period = 0
        discount_rate = request.POST.get('discount_rate')
        print(analysis_period)
        print(discount_rate)
        energy_conservation = {
            "electricity": 0,
            "diesel_oil": 42.0,
            "motor_gasoline": 0, 
            "natural_gas": 65.0, 
            "biomass": 0
        }
         
        externalities = []
        for i in range(0, 25):
                externalities.insert(i, 2.11)

        #scba = social_investment_analysis.Social(33800, 20, externalities, energy_conservation)
        #print(scba.pbp)
        #  print(scba.dpbp)
        return render(request, 'app2/cba_params_and_results.html', {'analysis_period': analysis_period, 'discount_rate': discount_rate})
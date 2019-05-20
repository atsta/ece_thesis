from django.shortcuts import render

from app2.forms import NewMeasureForm
from . import forms

from app2.models import Measure, Social

from app2 import energy_measure

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
                        return analysis(request)
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
        return render(request, 'app2/cba.html', {'costs': costs, 'benefits': benefits})


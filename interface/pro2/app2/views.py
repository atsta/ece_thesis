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
        print(selected)
        social = []
        for element in selected:
                print(element)
                hip = Social(measure=element)
                hip.save()
                social.append(hip)
        return render(request, 'app2/cba.html', {'selected': selected})


"""

def analysis(request): 
        #first_measure = Measure.objects.raw('SELECT * FROM app2_measure LIMIT 5')[0]
        #print(first_measure.name) 
        #measure = energy_measure.Measure(first_measure.name)
        form = forms.SomeInput()

        if request.method == 'POST':
                form = forms.SomeInput(request.POST)
                if form.is_valid():
                        print("Measure: "+ form.cleaned_data['measure'])
                        print("Analysis: " + form.cleaned_data['analysis'])


        return render(request,'app2/analysis.html', {'form': form})

"""
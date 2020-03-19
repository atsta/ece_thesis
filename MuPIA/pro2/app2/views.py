from django.shortcuts import render

from django.http import HttpResponse

from app2.forms import SensitiveForm, NewMeasureForm, MechForm1, MechForm2, MechForm3, MechForm4, LoanForm, FactorForm, ContractForm, ProfitInput, NPVInput, BCInput,  BenefitSatisfy, PeriodSatisfy, EscoLoan, SubsidyForm
from . import forms

from app2.models import Perspective, Esco, Measure, Social, Financial, Energy_Conservation, Costs, Benefits, Portfolio

from modules import energy_measure, financial_mechanism, perspective, social_investment_analysis, financial_investment_analysis

import string
import random
import pandas as pd
#import tkinter as tk
#from tkinter import filedialog
import json
from pandas.io.json import json_normalize
import numpy as np
import matplotlib.pyplot as plt

import csv

def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
        return ''.join(random.choice(chars) for _ in range(size))

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
                        measure = form.save(commit=True)
                        e = Energy_Conservation(measure=measure, biomass3=1300, electricity3 =300, diesel_oil3=15000, motor_gasoline3 = 1000)
                        e.save()
                        c = Costs(measure=measure)
                        c.save()
                        b = Benefits(measure=measure)
                        b.maintenance = 100
                        b.employability = 10
                        b.externalities = 10
                        b.save()
                        return render(request, 'app2/measure.html', {})
                else: 
                        print('Error: Invalid form')
                        
        return render(request, 'app2/analysis.html', {'form': form})

#social analysis views 

def measure_search_results(request):
        selected_category = request.POST.get('category')
        selected_type = request.POST.get('type')
        selected_article = request.POST.get('article')
        request.session['article'] = selected_article

        results = Measure.objects.filter(measure_type=selected_type, category=selected_category)

        return render(request, 'app2/measure.html', {'results': results, 
                                                        'selected_category': selected_category, 
                                                        'selected_type': selected_type})
def grab_selected_results(request): 
        selected = request.GET.getlist('measure')

        #remove '\' from measure name
        for i in range(len(selected)):
                k = selected[i]
                k = k[:-1]
                selected[i] = k
        
        display_benefits = ['maintenance', 'employability', 'work_efficiency','value_growth', 'externalities', 'other_benefits']
        display_costs = ['management', 'maintenance', 'reduced_income', 'other_costs']

        for element in selected:
                hip = Measure.objects.get(name=element)
                b = list(Benefits.objects.filter(measure=hip).values())
                print(b)
                if b[0]['maintenance'] == 0 and "maintenance" in display_benefits:
                        print('ok')
                        display_benefits.remove("maintenance")
                if b[0]['employability'] == 0 and "employability" in display_benefits:
                        display_benefits.remove("employability")
                if b[0]['work_efficiency'] == 0 and "work_efficiency" in display_benefits:
                        display_benefits.remove("work_efficiency")
                if b[0]['value_growth'] == 0 and "value_growth" in display_benefits:
                        display_benefits.remove("value_growth")
                if b[0]['externalities'] == 0 and "externalities" in display_benefits:
                        display_benefits.remove("externalities")
                if b[0]['other_benefits'] == 0 and "other_benefits" in display_benefits:
                        display_benefits.remove("other_benefits")
                
                c = list(Costs.objects.filter(measure=hip).values())
                print(c)
                if c[0]['maintenance'] == 0 and "maintenance" in display_costs:
                        display_costs.remove("maintenance")
                if c[0]['reduced_income'] == 0 and "reduced_income" in display_costs:
                        display_costs.remove("reduced_income")
                if c[0]['management'] == 0 and "management" in display_costs:
                        display_costs.remove("management")       
                if c[0]['other_costs'] == 0 and "other_costs" in display_costs:
                        display_costs.remove("other_costs")

        request.session['list'] = selected
        return render(request, 'app2/cba.html', {'selected': selected, 'display_benefits':display_benefits, 'display_costs':display_costs})

def choose_costs_and_benefits(request):
        benefits = request.POST.getlist('benefit')
        costs = request.POST.getlist('cost')
        print(costs)
        print(benefits)

        request.session['benefits'] = benefits
        request.session['costs'] = costs

        return render(request, 'app2/cba_params_and_results.html', {'costs': costs, 'benefits': benefits})

def grab_params_and_give_results(request):
        selected = request.session['list']
        benefits = request.session['benefits'] 
        costs = request.session['costs']
        article = request.session['article']

        chose_lifetime = request.POST.getlist('lifetime')
        
        give_lifetime_as_period = 0

        if chose_lifetime == []:
                analysis_period = request.POST.get('analysis_period')
        else:
                #tbd, for every measure selected
                analysis_period = 0
                give_lifetime_as_period = 1
        
        request.session['lifetime'] = give_lifetime_as_period

        analysis_period = int(analysis_period)
        request.session['period'] = analysis_period

        discount_rate = request.POST.get('discount_rate')
        discount_rate = float(discount_rate)/100
        request.session['discount_rate'] = discount_rate

        an = []
        social = {}
        pieces = []

        for item in selected:
                hip = Measure.objects.get(name=item)
                if article == 'art3':
                        m = energy_measure.Measure(item, 3)
                else:
                        m = energy_measure.Measure(item, 7)
                if give_lifetime_as_period == 1:
                        analysis_period = m.specs['lifetime']
                        

                scba = social_investment_analysis.Social(m.specs, m.energy_conservation, m.energy_price_without_taxes, m.energy_price_growth_rate, costs, benefits, analysis_period, discount_rate)
                
                
                #fcba = social_investment_analysis.Social(m.specs, m.energy_conservation, m.energy_price_with_taxes, m.energy_price_growth_rate, costs, benefits, analysis_period, discount_rate)

                social[item] = id_generator()
                
                hop = Social(name=social[item], measure=hip)
                hop.discount_rate = discount_rate
                hop.analysis_period = analysis_period
                hop.benefits = benefits
                hop.costs = costs
                hop.save()
                
                hop.npv = scba.npv
                hop.b_to_c = scba.b_to_c
                hop.irr = scba.irr
                hop.dpbp = scba.dpbp
                hop.save()
                an.append(hop)
                pieces.append(social[item])

        op = Portfolio(name=id_generator(), genre ='social', analysis_pieces=pieces)
        op.save()
                
        return render(request, 'app2/scba_result_page.html', {'analysis':an})


def social_result_page(request):
        
        return render(request, 'app2/fcba_params_results.html')


def fcba_params_results(request):
        selected = request.session['list']
        benefits = request.session['benefits'] 
        costs = request.session['costs']
        article = request.session['article']
        lifetime = request.session['lifetime']


        discount_rate = request.POST.get('discount_rate')
        if discount_rate == '':
                return render(request, 'app2/fcba_params_results.html')

        else: 
                discount_rate = float(discount_rate)/100


        an = []
        fin = {}
        pieces = []
        for item in selected:
                hip = Measure.objects.get(name=item)
                if article == 'art3':
                        m = energy_measure.Measure(item, 3)
                else:
                        m = energy_measure.Measure(item, 7)
                if lifetime == 1:
                        analysis_period = m.specs['lifetime']
                else: 
                        analysis_period = request.session['period']
                analysis_period = int(analysis_period)

                fcba = financial_investment_analysis.Financial(m.specs, m.energy_conservation, m.energy_price_with_taxes, m.energy_price_growth_rate, costs, benefits, analysis_period, discount_rate)
        
                fin[item] = id_generator()
                
                hop = Financial(name=fin[item], measure=hip)
                hop.discount_rate = discount_rate
                hop.analysis_period = analysis_period
                hop.benefits = benefits
                hop.costs = costs
                hop.save()
                
                hop.npv = fcba.npv
                hop.b_to_c = fcba.b_to_c
                hop.irr = fcba.irr
                hop.dpbp = fcba.dpbp
                hop.save()
                an.append(hop)
                pieces.append(fin[item])

        op = Portfolio(name=id_generator(), genre ='financial', analysis_pieces=pieces)
        op.save()

        return render(request, 'app2/fcba_result_page.html', {'analysis': an})

def financial_result_page(request):
        
        return render(request, 'app2/fcba_result_page.html')

#investment analysis views

def actor(request):
    return render(request,'app2/actor_choice.html')

def measure_search_results_investment(request):
        article = request.POST.get('article')
        selected_category = request.POST.get('category')
        selected_type = request.POST.get('type')

        results = Measure.objects.filter(measure_type=selected_type, category=selected_category)
        
        request.session['category'] = selected_category
        request.session['type'] = selected_type
        request.session['article'] = article

        return render(request, 'app2/actor_choice.html', {'results': results, 
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
        display_benefits = ['maintenance', 'employability', 'work_efficiency','value_growth', 'externalities', 'other_benefits']
        display_costs = ['management', 'maintenance', 'reduced_income', 'other_costs']
        
        for item in selected:
                hip = Measure.objects.get(name=item)
                b = list(Benefits.objects.filter(measure=hip).values())
                print(b)
                if b[0]['maintenance'] == 0 and "maintenance" in display_benefits:
                        print('ok')
                        display_benefits.remove("maintenance")
                if b[0]['employability'] == 0 and "employability" in display_benefits:
                        display_benefits.remove("employability")
                if b[0]['work_efficiency'] == 0 and "work_efficiency" in display_benefits:
                        display_benefits.remove("work_efficiency")
                if b[0]['value_growth'] == 0 and "value_growth" in display_benefits:
                        display_benefits.remove("value_growth")
                if b[0]['externalities'] == 0 and "externalities" in display_benefits:
                        display_benefits.remove("externalities")
                if b[0]['other_benefits'] == 0 and "other_benefits" in display_benefits:
                        display_benefits.remove("other_benefits")
                
                c = list(Costs.objects.filter(measure=hip).values())
                print(c)
                if c[0]['maintenance'] == 0 and "maintenance" in display_costs:
                        display_costs.remove("maintenance")
                if c[0]['reduced_income'] == 0 and "reduced_income" in display_costs:
                        display_costs.remove("reduced_income")
                if c[0]['management'] == 0 and "management" in display_costs:
                        display_costs.remove("management")       
                if c[0]['other_costs'] == 0 and "other_costs" in display_costs:
                        display_costs.remove("other_costs")


        request.session['list'] = selected
        print(selected)
        
        return render(request, 'app2/investment_analysis.html', {'selected': selected, 'display_benefits':display_benefits, 'display_costs':display_costs})

def choose_costs_and_benefits_investment(request):
        selected_category = request.session['category']
        selected_type = request.session['type']
        selected = request.session['list'] 
        
        benefits = request.POST.getlist('benefit')
        costs = request.POST.getlist('cost')
        

        print(costs)
        print(benefits)        
        print(selected_category)
        print(selected_type)
        request.session['benefits_dict'] = benefits
        request.session['costs'] = costs 
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
                        mechanism = form.cleaned_data['chosen_mechanism']
                        print(mechanism)
                        form1 = " "
                        form2 = " "
                        form3 = " "
                        request.session['mechanism'] = mechanism
                        for item in mechanism:
                                if item == 'subsidy':
                                        form3 = SubsidyForm()
                                if item == 'loan':
                                        form1 = LoanForm() 
                                if item == 'increase_factor':
                                        form2 = FactorForm()
                       
                        return render(request, 'app2/investment_analysis_params.html', {'form': form, 'form1': form1, 'form2': form2, 'form3': form3})

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
        esco = 0
        for item in mechanism:
                if item == 'energy_contract':
                        esco = 1
                if item == 'loan':
                        if request.method == "POST":
                                form1 = LoanForm(request.POST)
                                if form1.is_valid():
                                        loan_rate = form1.cleaned_data['loan_rate'] 
                                        loan_rate = float(loan_rate)/100
                                        annual_interest = form1.cleaned_data['annual_rate']
                                        annual_interest = float(annual_interest)/100
                                        subsidized_interest = form1.cleaned_data['subsidized_interest_rate']
                                        subsidized_interest = float(subsidized_interest)/100
                                        print(loan_rate)
                                        print(annual_interest)
                                        print(subsidized_interest)
                                        loan_period = form1.cleaned_data['loan_period'] 
                                        grace_period = form1.cleaned_data['grace_period']
                                        request.session['lr'] = loan_rate
                                        request.session['ar'] = annual_interest
                                        request.session['sr'] = subsidized_interest
                                        request.session['lp'] = loan_period
                                        request.session['gp'] = grace_period
                if item == 'increase_factor':
                        if request.method == "POST":
                                form2 = FactorForm(request.POST)
                                if form2.is_valid():
                                        depreciation_tax_rate = form2.cleaned_data["depreciation_tax_rate"]
                                        depreciation_tax_rate = float(depreciation_tax_rate)/100
                                        tax_lifetime = form2.cleaned_data["tax_lifetime"]
                                        request.session['tax_rate'] = depreciation_tax_rate  
                                        request.session['tax_lifetime'] = tax_lifetime
                                        print(depreciation_tax_rate)
                                        print(tax_lifetime)
                if item == 'subsidy':
                        if request.method == "POST":
                                form3 = SubsidyForm(request.POST)
                                if form3.is_valid():
                                        sub_rate = form3.cleaned_data["subsidy_rate"]
                                        sub_rate = float(sub_rate)/100
                                        print(sub_rate)
                                        request.session['subsidy'] = sub_rate
        if esco == 0: 
                return render(request, 'app2/investment_analysis_results.html')
        else:
                form1 = ContractForm()
                return render(request, 'app2/esco.html', {'form1': form1})

def esco_params(request):
        if request.method == "POST":
                form1 = ContractForm(request.POST)
                esco_loan = request.POST.get('took_loan')
                print(esco_loan)
                if form1.is_valid():
                        esco_disc_rate = form1.cleaned_data['discount_rate']
                        esco_disc_rate = float(esco_disc_rate)/100
                        request.session['esco_disc_rate'] = esco_disc_rate
                        criterion = form1.cleaned_data['chosen_criterion']
                        request.session['esco_criterion'] = criterion
                        print(esco_disc_rate)
                        print(criterion)
                        if criterion == 'profit':
                                form2 = ProfitInput() 
                        if criterion == 'npv':
                                form2 = NPVInput()
                        if criterion == 'b_to_c':
                                form2 = BCInput()

                        criterion_satisfaction = form1.cleaned_data['criterion_satisfaction']
                        request.session['esco_criterion_satisfaction'] = criterion_satisfaction
                        print(criterion_satisfaction)
                        
                        if criterion_satisfaction == 'contract_period':
                                form3 = PeriodSatisfy() 
                        if criterion_satisfaction == 'benefit_share':
                                form3 = BenefitSatisfy()

                        if esco_loan == 'esco_loan':
                                request.session['took_loan'] = esco_loan
                                form4 = EscoLoan()
                                return render(request, 'app2/esco.html', {'form1': form1, 'form2':form2, 'form3': form3, 'form4': form4})

                        return render(request, 'app2/esco.html', {'form1': form1, 'form2':form2, 'form3': form3})

def grab_esco_params(request):
        criterion = request.session['esco_criterion']
        criterion_satisfaction = request.session['esco_criterion_satisfaction'] 
        took_loan = request.session['took_loan']
        form1 = ContractForm()
        if request.method == "POST":
                if criterion == 'profit':
                        form2 = ProfitInput(request.POST) 
                        if form2.is_valid():
                                esco_profit = form2.cleaned_data['profit']
                                esco_profit = float(esco_profit)/100
                                request.session['esco_profit'] = esco_profit
                if criterion == 'npv':
                        form2 = NPVInput(request.POST)
                        if form2.is_valid():
                                esco_npv = form2.cleaned_data['npv']
                                request.session['esco_npv'] = esco_npv
                if criterion == 'b_to_c':
                        form2 = BCInput(request.POST)
                        if form2.is_valid():
                                esco_bc = form2.cleaned_data['b_to_c']
                                request.session['esco_bc'] = esco_bc

                if criterion_satisfaction == 'contract_period':
                        form3 = PeriodSatisfy(request.POST) 
                        if form3.is_valid():
                                cost_esco_rate = form3.cleaned_data['cost_esco_rate']
                                cost_esco_rate = float(cost_esco_rate)/100
                                benefit_share_rate = form3.cleaned_data['benefit_share_rate']
                                benefit_share_rate = float(benefit_share_rate)/100
                                request.session['cost_share'] = cost_esco_rate
                                request.session['benefit_share'] = benefit_share_rate
                if criterion_satisfaction == 'benefit_share':
                        form3 = BenefitSatisfy(request.POST)
                        if form3.is_valid():
                                cost_esco_rate = form3.cleaned_data['cost_esco_rate']
                                cost_esco_rate = float(cost_esco_rate)/100
                                contract_period = form3.cleaned_data['contract_period']
                                request.session['cost_share'] = cost_esco_rate

                                request.session['esco_period'] = contract_period

                if took_loan == 'esco_loan':
                        form4 = EscoLoan(request.POST)
                        if form4.is_valid():
                                loan_rate = form4.cleaned_data['loan_rate'] 
                                loan_rate = float(loan_rate)/100
                                annual_rate = form4.cleaned_data['annual_rate']
                                annual_rate = float(annual_rate)/100
                                subsidized_interest = form4.cleaned_data['subsidized_interest_rate']
                                subsidized_interest = float(subsidized_interest)/100
                                loan_period = form4.cleaned_data['loan_period'] 
                                grace_period = form4.cleaned_data['grace_period']
                                request.session['esco_lr'] = loan_rate
                                request.session['esco_ar'] = annual_rate
                                request.session['esco_sr'] = subsidized_interest
                                request.session['esco_lp'] = loan_period
                                request.session['esco_gp'] = grace_period

        return render(request, 'app2/investment_analysis_results.html')
        
def investment_analysis_results(request):
        max_period = 0
        chose_lifetime = request.POST.getlist('lifetime')
        if chose_lifetime == []:
                analysis_period = request.POST.get('analysis_period')
        else:
                analysis_period = 0
        discount_rate = request.POST.get('discount_rate')
        discount_rate = float(discount_rate)/100
        article = request.session['article']
        selected_measures = request.session['list']
        selected_benefits = request.session['benefits_dict']
        selected_costs = request.session['costs'] 
        mechanism = request.session['mechanism']
        request.session['inv_analysis_period'] = analysis_period
        request.session['inv_discount_rate'] = discount_rate

        give_lifetime_as_period = 0
        if analysis_period == 0:
                give_lifetime_as_period = 1

        analysis_period = int(analysis_period)
        
        persp = {}
        an = []
        pieces = []
        dfs = {}
        cdfs = {}
        for item in selected_measures:
                hip = Measure.objects.get(name=item)
                if article == 'art3':
                        m = energy_measure.Measure(item, 3)
                else:
                        m = energy_measure.Measure(item, 7)

                if give_lifetime_as_period == 1:
                        analysis_period = m.specs['lifetime']
                
   

                sub = financial_mechanism.Subsidy(m.specs, 0.0)
                tax = financial_mechanism.Tax_depreciation(0.0, 0.0, 0)
                ln = financial_mechanism.Loan(0,0,0,0,0,0)
                esco = financial_mechanism.Esco(m.specs, [], 0, " ",0, " ", 0, 0, 0, 0, ln)
                for submech in mechanism:
                        if submech == 'subsidy':
                                sub_rate = request.session['subsidy']
                                sub = financial_mechanism.Subsidy(m.specs, sub_rate)
                        if submech == 'loan':
                                loan_rate = request.session['lr']
                                annual_interest = request.session['ar'] 
                                subsidized_interest = request.session['sr'] 
                                loan_period = request.session['lp']
                                grace_period = request.session['gp'] 
                                if loan_period > max_period:
                                        max_period = loan_period
                                for it in mechanism:
                                        if it == "subsidy":
                                                sub_rate = request.session['subsidy']
                                                logistic_cost = m.specs['cost']*1.24*(1-sub_rate)
                                                break
                                        else:
                                                logistic_cost = measure_sample['cost']*1.24
                                ln = financial_mechanism.Loan(logistic_cost, loan_rate, annual_interest, subsidized_interest, loan_period, grace_period)
                        if submech == 'increase_factor':
                                depreciation_tax_rate  = request.session['tax_rate']  
                                tax_lifetime =  request.session['tax_lifetime'] 
                                tax = financial_mechanism.Tax_depreciation(0.25, depreciation_tax_rate, tax_lifetime)
                                if tax_lifetime > max_period:
                                        max_period = tax_lifetime
                for submech in mechanism:
                        if submech == 'energy_contract':
                                per = perspective.Perspective(m.specs, m.energy_conservation, m.energy_price_with_taxes, m.energy_price_growth_rate, selected_costs, selected_benefits, analysis_period, discount_rate, sub, ln, esco, tax)
                                savings = per.benefits['Energy savings']
                                avg_ratios = per.avg_ratios

                                esco_disc_rate = request.session['esco_disc_rate']
                                criterion = request.session['esco_criterion'] 
                                criterion_satisfaction = request.session['esco_criterion_satisfaction'] 
                                took_loan = request.session['took_loan']

                                if took_loan == 'esco_loan':
                                        loan_rate = request.session['esco_lr'] 
                                        annual_rate = request.session['esco_ar']  
                                        subsidized_interest = request.session['esco_sr'] 
                                        loan_period = request.session['esco_lp']
                                        if loan_period > max_period:
                                                max_period = loan_period 
                                        grace_period = request.session['esco_gp']
                                        if criterion_satisfaction == 'cost_esco':
                                                esco_loan = financial_mechanism.Loan(m.specs['cost']*1.24 ,loan_rate, annual_rate, subsidized_interest, loan_period, grace_period )
                                        else:
                                                cost_share = request.session['cost_share']
                                                esco_loan = financial_mechanism.Loan(cost_share*m.specs['cost']*1.24, loan_rate, annual_rate, subsidized_interest, loan_period, grace_period )
                                else:
                                        esco_loan = financial_mechanism.Loan(0,0,0,0,0,0)
                                if criterion == 'profit':
                                        cr_val = request.session['esco_profit']
                                if criterion == 'spbp':
                                        cr_val = request.session['esco_spbp'] 
                                if criterion == 'dpbp':
                                        cr_val = request.session['esco_irr'] 
                                if criterion_satisfaction == 'contract_period':
                                        cost_esco_rate = request.session['cost_share']
                                        benefit_share_rate = request.session['benefit_share'] 
                                        esco = financial_mechanism.Esco(m.specs, savings, avg_ratios, criterion, cr_val, criterion_satisfaction, esco_disc_rate, cost_esco_rate, benefit_share_rate, 0, esco_loan)
                                if criterion_satisfaction == 'benefit_share':
                                        cost_esco_rate = request.session['cost_share']
                                        contract_period = request.session['esco_period']
                                        if contract_period  > max_period:
                                                max_period = contract_period 
                                        esco = financial_mechanism.Esco(m.specs, savings, int(avg_ratios), criterion, int(cr_val), criterion_satisfaction, float(esco_disc_rate), float(cost_esco_rate), 1,int(contract_period) , esco_loan)
                                        if esco.benefit_share_rate > 1: 
                                                print("Error:Benefit Share should be less than 100%")
                                                form1 = ContractForm()
                                                return render(request, 'app2/esco.html', {'form1': form1})

                                print("Esco Benefits:")
                                print(esco.benefits)
                                print("Esco Costs:")
                                print(esco.costs)
                
                print(analysis_period)
                if analysis_period < max_period:
                        #error handling
                        print("Analysis Period should be bigger than"+ max_period)
                        return render(request, 'app2/investment_analysis_results.html')
                per = perspective.Perspective(m.specs, m.energy_conservation, m.energy_price_with_taxes, m.energy_price_growth_rate, selected_costs, selected_benefits, analysis_period, discount_rate, sub, ln, esco, tax)
                
                #store perspective analysis to database 
                persp[item]= id_generator()
                hop = Perspective(name=persp[item], measure=hip)
                hop.save()
                hop = Perspective.objects.get(name=persp[item])
                hop.financial_mechanisms = mechanism
                hop.discount_rate = discount_rate              
                hop.analysis_period = analysis_period
                hop.benefits = selected_benefits
                hop.costs = selected_costs
                hop.npv = per.npv
                hop.b_to_c = per.b_to_c
                hop.irr = per.irr
                hop.dpbp = per.dpbp
                hop.spbp = per.pbp
                hop.save()
                
                pieces.append(persp[item])
                an.append(hop)
                print("Actor Benefits")
                print(per.benefits)
                print("Actor Costs")
                print(per.costs)
                dfs[item] = per.benefits
                cdfs[item] = per.costs
        op = Portfolio(name=id_generator(), genre ='perspective', analysis_pieces=pieces)
        op.save()
        for item in selected_measures:
                dfs[item] = dfs[item].to_json(orient='table')
                cdfs[item] = cdfs[item].to_json(orient='table')

        request.session['dfs'] = dfs  
        request.session['cdfs'] = cdfs  

        return render(request, 'app2/investment_result_page.html', {'analysis':an})

#def exportCSV (df):
 #   
  #  export_file_path = filedialog.asksaveasfilename(defaultextension='.csv')
   # df.to_csv (export_file_path, index = None, header=True)

def investment_result_page(request):
        selected_measures = request.session['list']
        dfs = request.session['dfs'] 
        cdfs = request.session['cdfs'] 

        if request.method == 'POST':
                for item in selected_measures: 
                        if request.POST.get(item):
                                data = dfs[item]
                                df =  pd.read_json(data, orient='table')
                                print(df)
                                response = HttpResponse(content_type='text/csv')
                                response['Content-Disposition'] = 'attachment; filename=Infilename.csv'
                                df.to_csv(path_or_buf=response,sep=',',index=False,decimal=".")
                                #saveAsButton_CSV = tk.Button(text='Export CSV', command=exportCSV(df), bg='green', fg='white', font=('helvetica', 12, 'bold'))
                                return response
                        else: 
                                data = cdfs[item]
                                df =  pd.read_json(data, orient='table')
                                print(df)
                                response = HttpResponse(content_type='text/csv')
                                response['Content-Disposition'] = 'attachment; filename=Outfilename.csv'
                                df.to_csv(path_or_buf=response,sep=',',index=False,decimal=".")
                              #  saveAsButton_CSV = tk.Button(text='Export CSV', command=exportCSV(df), bg='green', fg='white', font=('helvetica', 12, 'bold'))
                                return response
        
        return render(request, 'app2/investment_result_page.html')

def sensitivity(request):
        form = SensitiveForm()
        if request.method == "POST":
                form = SensitiveForm(request.POST)
                if form.is_valid():
                        a =  form.cleaned_data['a']
                        b =  form.cleaned_data['b']
                        c = form.cleaned_data['c']
                        var = form.cleaned_data['variable']
                        index = form.cleaned_data['indices']
                        sm = form.cleaned_data['measure']
                        print(a)



                        max_period = 0
                        analysis_period = request.session['inv_analysis_period'] 
                        discount_rate = request.session['inv_discount_rate']
                        article = request.session['article']
                        selected_measures = request.session['list']
                        selected_benefits = request.session['benefits_dict']
                        selected_costs = request.session['costs'] 
                        mechanism = request.session['mechanism']
                        give_lifetime_as_period = 0
                        if analysis_period == 0:
                                give_lifetime_as_period = 1

                        analysis_period = int(analysis_period)
        
                        persp = {}
                        an = []
                        pieces = []
                        dfs = {}
                        cdfs = {}
                        total = []

                        for item in selected_measures:
                                if article == 'art3':
                                        m = energy_measure.Measure(item, 3)
                                else:
                                        m = energy_measure.Measure(item, 7)

                                if give_lifetime_as_period == 1:
                                        analysis_period = m.specs['lifetime']
                
   

                                sub = financial_mechanism.Subsidy(m.specs, 0.0)
                                tax = financial_mechanism.Tax_depreciation(0.0, 0.0, 0)
                                ln = financial_mechanism.Loan(0,0,0,0,0,0)
                                esco = financial_mechanism.Esco(m.specs, [], 0, " ",0, " ", 0, 0, 0, 0, ln)
                                for submech in mechanism:
                                        if submech == 'subsidy':
                                                sub_rate = request.session['subsidy']
                                                sub = financial_mechanism.Subsidy(m.specs, sub_rate)
                                        if submech == 'loan':
                                                loan_rate = request.session['lr']
                                                annual_interest = request.session['ar'] 
                                                subsidized_interest = request.session['sr'] 
                                                loan_period = request.session['lp']
                                                grace_period = request.session['gp'] 
                                                if loan_period > max_period:
                                                        max_period = loan_period
                                                for it in mechanism:
                                                        if it == "subsidy":
                                                                sub_rate = request.session['subsidy']
                                                                logistic_cost = m.specs['cost']*1.24*(1-sub_rate)
                                                                break
                                                        else:
                                                                logistic_cost = measure_sample['cost']*1.24
                                                ln = financial_mechanism.Loan(logistic_cost, loan_rate, annual_interest, subsidized_interest, loan_period, grace_period)
                                        if submech == 'increase_factor':
                                                depreciation_tax_rate  = request.session['tax_rate']  
                                                tax_lifetime =  request.session['tax_lifetime'] 
                                                tax = financial_mechanism.Tax_depreciation(0.25, depreciation_tax_rate, tax_lifetime)
                                                if tax_lifetime > max_period:
                                                        max_period = tax_lifetime
                                for submech in mechanism:
                                        if submech == 'energy_contract':
                                                per = perspective.Perspective(m.specs, m.energy_conservation, m.energy_price_with_taxes, m.energy_price_growth_rate, selected_costs, selected_benefits, analysis_period, discount_rate, sub, ln, esco, tax)
                                                savings = per.benefits['Energy savings']
                                                avg_ratios = per.avg_ratios

                                                esco_disc_rate = request.session['esco_disc_rate']
                                                criterion = request.session['esco_criterion'] 
                                                criterion_satisfaction = request.session['esco_criterion_satisfaction'] 
                                                took_loan = request.session['took_loan']

                                                if took_loan == 'esco_loan':
                                                        loan_rate = request.session['esco_lr'] 
                                                        annual_rate = request.session['esco_ar']  
                                                        subsidized_interest = request.session['esco_sr'] 
                                                        loan_period = request.session['esco_lp']
                                                        if loan_period > max_period:
                                                                max_period = loan_period 
                                                        grace_period = request.session['esco_gp']
                                                        if criterion_satisfaction == 'cost_esco':
                                                                esco_loan = financial_mechanism.Loan(m.specs['cost']*1.24 ,loan_rate, annual_rate, subsidized_interest, loan_period, grace_period )
                                                        else:
                                                                cost_share = request.session['cost_share']
                                                                esco_loan = financial_mechanism.Loan(cost_share*m.specs['cost']*1.24, loan_rate, annual_rate, subsidized_interest, loan_period, grace_period )
                                                else:
                                                        esco_loan = financial_mechanism.Loan(0,0,0,0,0,0)
                                                if criterion == 'profit':
                                                        cr_val = request.session['esco_profit']
                                                if criterion == 'spbp':
                                                        cr_val = request.session['esco_spbp'] 
                                                if criterion == 'dpbp':
                                                        cr_val = request.session['esco_irr'] 
                                                if criterion_satisfaction == 'contract_period':
                                                        cost_esco_rate = request.session['cost_share']
                                                        benefit_share_rate = request.session['benefit_share'] 
                                                        esco = financial_mechanism.Esco(m.specs, savings, avg_ratios, criterion, cr_val, criterion_satisfaction, esco_disc_rate, cost_esco_rate, benefit_share_rate, 0, esco_loan)
                                                if criterion_satisfaction == 'benefit_share':
                                                        cost_esco_rate = request.session['cost_share']
                                                        contract_period = request.session['esco_period']
                                                        if contract_period  > max_period:
                                                                max_period = contract_period 
                                                        esco = financial_mechanism.Esco(m.specs, savings, int(avg_ratios), criterion, int(cr_val), criterion_satisfaction, float(esco_disc_rate), float(cost_esco_rate), 1,int(contract_period) , esco_loan)
                                                        if esco.benefit_share_rate > 1: 
                                                                print("Error:Benefit Share should be less than 100%")
                                                                form1 = ContractForm()
                                                                return render(request, 'app2/esco.html', {'form1': form1})

                                                print("Esco Benefits:")
                                                print(esco.benefits)
                                                print("Esco Costs:")
                                                print(esco.costs)
                
                                if analysis_period < max_period:
                                        #error handling
                                        print("Analysis Period should be bigger than"+ max_period)
                                        return render(request, 'app2/investment_analysis_results.html')
                                p = perspective.Perspective(m.specs, m.energy_conservation, m.energy_price_with_taxes, m.energy_price_growth_rate, selected_costs, selected_benefits, analysis_period, discount_rate, sub, ln, esco, tax)
                                
                                
                                h = plt.hist(np.random.triangular(a, b, c, 1000000), bins=100, density=True)    
                                results = []
                
                                for val in h[1]:
                                        if var == 'disc':
                                                p = perspective.Perspective(m.specs, m.energy_conservation, m.energy_price_with_taxes, m.energy_price_growth_rate, selected_costs, selected_benefits, analysis_period, val, sub, ln, esco, tax)

                                                if index == 'bc':
                                                        results.append(p.b_to_c)
                                                if index == 'npv':
                                                        results.append(p.npv)
                                                if index == 'irr':
                                                        results.append(p.irr)
                                                if index == 'pbp':
                                                        results.append(p.dpbp)
                                        if var =='period':
                                                p = perspective.Perspective(m.specs, m.energy_conservation, m.energy_price_with_taxes, m.energy_price_growth_rate, selected_costs, selected_benefits, val, discount_rate, sub, ln, esco, tax)
                                                if index == 'bc':
                                                        results.append(p.b_to_c)
                                                if index == 'npv':
                                                        results.append(p.npv)
                                                if index == 'irr':
                                                        results.append(p.irr)
                                                if index == 'pbp':
                                                        results.append(p.dpbp)  
                                        if var == 'mul':
                                                new_rate = {
                                                        "electricity": val*float(m.energy_price_growth_rate["electricity"]),
                                                        "diesel_oil": val*float(m.energy_price_growth_rate["diesel_oil"]),
                                                        "motor_gasoline": val*float(m.energy_price_growth_rate["motor_gasoline"]), 
                                                        "natural_gas": val*float(m.energy_price_growth_rate["natural_gas"]), 
                                                        "biomass": val*float(m.energy_price_growth_rate["biomass"])
                                                }

                                                p = perspective.Perspective(m.specs, m.energy_conservation, m.energy_price_with_taxes, new_rate, selected_costs, selected_benefits, analysis_period, discount_rate, sub, ln, esco, tax)
                                                if index == 'bc':
                                                        results.append(p.b_to_c)
                                                if index == 'npv':
                                                        results.append(p.npv)
                                                if index == 'irr':
                                                        results.append(p.irr)
                                                if index == 'pbp':
                                                        results.append(p.dpbp) 
                                print(results)
                                #total.append(results)

                                if item == sm:
                                        if var == 'disc':
                                                p0 = perspective.Perspective(m.specs, m.energy_conservation, m.energy_price_with_taxes, m.energy_price_growth_rate, selected_costs, selected_benefits, analysis_period, a, sub, ln, esco, tax)
                                                p1 = perspective.Perspective(m.specs, m.energy_conservation, m.energy_price_with_taxes, m.energy_price_growth_rate, selected_costs, selected_benefits, analysis_period, b, sub, ln, esco, tax)
                                                p2 = perspective.Perspective(m.specs, m.energy_conservation, m.energy_price_with_taxes, m.energy_price_growth_rate, selected_costs, selected_benefits, analysis_period, c, sub, ln, esco, tax)

                                                if index == 'bc':
                                                        li = [p0.b_to_c, p1.b_to_c, p2.b_to_c]
                                                if index == 'npv':
                                                        li = [p0.npv, p1.npv, p2.npv]
                                                if index == 'irr':
                                                        li = [p0.irr, p1.irr, p2.irr]
                                                if index == 'pbp':
                                                        li = [p0.dpbp, p1.dpbp, p2.dpbp]
                                        if var =='period':
                                                p0 = perspective.Perspective(m.specs, m.energy_conservation, m.energy_price_with_taxes, m.energy_price_growth_rate, selected_costs, selected_benefits, a, discount_rate, sub, ln, esco, tax)
                                                p1 = perspective.Perspective(m.specs, m.energy_conservation, m.energy_price_with_taxes, m.energy_price_growth_rate, selected_costs, selected_benefits, b, discount_rate, sub, ln, esco, tax)
                                                p2 = perspective.Perspective(m.specs, m.energy_conservation, m.energy_price_with_taxes, m.energy_price_growth_rate, selected_costs, selected_benefits, c, discount_rate, sub, ln, esco, tax)

                                                if index == 'bc':
                                                        li = [p0.b_to_c, p1.b_to_c, p2.b_to_c]
                                                if index == 'npv':
                                                        li = [p0.npv, p1.npv, p2.npv]
                                                if index == 'irr':
                                                        li = [p0.irr, p1.irr, p2.irr]
                                                if index == 'pbp':
                                                        li = [p0.dpbp, p1.dpbp, p2.dpbp]
                                        if var == 'mul':
                                                new_rate0 = {
                                                        "electricity": a*float(m.energy_price_growth_rate["electricity"]),
                                                        "diesel_oil": a*float(m.energy_price_growth_rate["diesel_oil"]),
                                                        "motor_gasoline": a*float(m.energy_price_growth_rate["motor_gasoline"]), 
                                                        "natural_gas": a*float(m.energy_price_growth_rate["natural_gas"]), 
                                                        "biomass": a*float(m.energy_price_growth_rate["biomass"])
                                                }
                                                new_rate1 = {
                                                        "electricity": b*float(m.energy_price_growth_rate["electricity"]),
                                                        "diesel_oil": b*float(m.energy_price_growth_rate["diesel_oil"]),
                                                        "motor_gasoline": b*float(m.energy_price_growth_rate["motor_gasoline"]), 
                                                        "natural_gas": b*float(m.energy_price_growth_rate["natural_gas"]), 
                                                        "biomass": b*float(m.energy_price_growth_rate["biomass"])
                                                }
                                                new_rate2 = {
                                                        "electricity": c*float(m.energy_price_growth_rate["electricity"]),
                                                        "diesel_oil": c*float(m.energy_price_growth_rate["diesel_oil"]),
                                                        "motor_gasoline": c*float(m.energy_price_growth_rate["motor_gasoline"]), 
                                                        "natural_gas": c*float(m.energy_price_growth_rate["natural_gas"]), 
                                                        "biomass": c*float(m.energy_price_growth_rate["biomass"])
                                                }
                                                p0 = perspective.Perspective(m.specs, m.energy_conservation, m.energy_price_with_taxes, new_rate0, selected_costs, selected_benefits, analysis_period, discount_rate, sub, ln, esco, tax)
                                                p1 = perspective.Perspective(m.specs, m.energy_conservation, m.energy_price_with_taxes, new_rate1, selected_costs, selected_benefits, analysis_period, discount_rate, sub, ln, esco, tax)
                                                p2 = perspective.Perspective(m.specs, m.energy_conservation, m.energy_price_with_taxes, new_rate2, selected_costs, selected_benefits, analysis_period, discount_rate, sub, ln, esco, tax)

                                                if index == 'bc':
                                                        li = [p0.b_to_c, p1.b_to_c, p2.b_to_c]
                                                if index == 'npv':
                                                        li = [p0.npv, p1.npv, p2.npv]
                                                if index == 'irr':
                                                        li = [p0.irr, p1.irr, p2.irr]
                                                if index == 'pbp':
                                                        li = [p0.dpbp, p1.dpbp, p2.dpbp]

                                        #with open('/home/atsta/Documents/ECE NTUA/Thesis/code/ece_thesis/MuPIA/pro2/app2/sensitivity.csv', "w") as file:
                                        #        writer = csv.writer(file)
                                        #        if var == "disc":
                                        #                writer.writerow(["discount rate"])
                                        #        elif var == 'period':
                                        #                writer.writerow(["analysis period"])
                                        #        else: 
                                        #                writer.writerow(["energy rate multiplier"])
#
                                        #        if index == 'bc':
                                        #                writer.writerow(["B/C"]) 
                                        #        if index == 'npv':
                                        #                writer.writerow(["NPV"]) 
                                       #         if index == 'irr':
                                        #                writer.writerow(["IRR"]) 
                                        #        if index == 'pbp':
                                        #                writer.writerow(["Payback Period"]) 
                                        #        writer.writerow(li)
                                        #        writer.writerow(results)  
                                
                              

                # #print(h[0])
                # print(h[1])
                # print(result_b_to_c)
        return render(request, 'app2/sensitivity.html', {'form': form})


import energy_measure
import social_investment_analysis
import financial_investment_analysis

import perspective
import financial_mechanism

import decimal 
import matplotlib.pyplot as plt
import numpy as np


import tkinter as tk
from tkinter import filedialog
from pandas import DataFrame

def exportCSV (df):
    
    export_file_path = filedialog.asksaveasfilename(defaultextension='.csv')
    df.to_csv (export_file_path, index = None, header=True)


def main():
#temporarily tertiary prices
    energy_price_with_taxes = {
        "electricity": 166.4,
        "diesel_oil": 79.5,
        "motor_gasoline": 134.7, 
        "natural_gas": 62.0, 
        "biomass": 64.6
    }

    energy_price_without_taxes = {
        "electricity": 116,
        "diesel_oil": 41.8,
        "motor_gasoline": 45, 
        "natural_gas": 51, 
        "biomass": 52.1
    }

    energy_conservation = {
            "electricity": 0,
            "diesel_oil": 42.0,
            "motor_gasoline": 0, 
            "natural_gas": 65.0, 
            "biomass": 0
    }

    energy_price_growth_rate = {
        "electricity": 0.015,
        "diesel_oil": 0.025,
        "motor_gasoline": 0.025, 
        "natural_gas": 0.017, 
        "biomass": 0.02
    }

    m = energy_measure.Measure("test_social", 3)
    print(m.specs)
    print(m.energy_conservation)

    selected_benefits = ["energy_savings", "maintenance", "residual_value", "tax_depreciation"]
    selected_costs = ["equipment"]

    #SCBA
    # social = social_investment_analysis.Social(m.specs, m.energy_conservation, m.energy_price_without_taxes, m.energy_price_growth_rate, selected_costs, selected_benefits, 25, 0.03)
    
    # print(social.benefits)
    # print(social.costs)
    # print(social.pure_cash_flow)
    # print(social.cost_pv)
    # print(social.benefit_pv)
    # print(social.npv)
    # print(social.b_to_c)
    # print(social.irr)
    # print(social.pbp)



    #FCBA

    # financial = financial_investment_analysis.Financial(m.specs, m.energy_conservation, m.energy_price_with_taxes, m.energy_price_growth_rate, selected_costs, selected_benefits, 25, 0.05)
    
    # print(financial.benefits)
    # print(financial.costs)
    # print(financial.pure_cash_flow)
    # print(financial.cost_pv)
    # print(financial.benefit_pv)
    # print(financial.npv)
    # print(financial.b_to_c)
    # print(financial.irr)
    # print(financial.pbp)



    #PERSPECTIVE

    sub = financial_mechanism.Subsidy(m.specs, 0.4)
    tax = financial_mechanism.Tax_depreciation(0.25, 0.1, 10)

    if sub.subsidy_rate > 0:
        logistic_cost = m.specs['cost']*1.24*(1-sub.subsidy_rate)
    else:
        logistic_cost = m.specs['cost']*1.24
      
    loan = financial_mechanism.Loan(logistic_cost, 0.5, 0.08, 0.024, 3, 0)
    
    esco_loan = financial_mechanism.Loan(m.specs['cost'], 0.5, 0.08, 0.024, 10, 0)

    test_esco = financial_mechanism.Esco(m.specs, [], 0, " ", 0, " ", 0, 0, 0, 0, esco_loan)

    test_per = perspective.Perspective(m.specs, energy_conservation, energy_price_with_taxes, energy_price_growth_rate, selected_costs, selected_benefits, 25, 0.05, sub, loan, test_esco, tax)

    esco_actor = financial_mechanism.Esco(m.specs, test_per.savings_per_year_taxable, 0, "npv", 8328, "benefit_share", 0.06, 0.8, 0.7, 8, esco_loan)
    
        
    p =  perspective.Perspective(m.specs, m.energy_conservation, m.energy_price_with_taxes, m.energy_price_growth_rate, selected_costs, selected_benefits, 25, 0.05, sub, loan, esco_actor, tax)



    print(p.benefits)
    print(p.costs)
    print(p.pure_cash_flow)
    print(p.cost_pv)
    print(p.benefit_pv)
    print(p.npv)
    print(p.b_to_c)
    print(p.irr)
    print(p.pbp)
    print(esco_actor.benefit_share_rate)


    #root= tk.Tk()

    #canvas1 = tk.Canvas(root, width = 300, height = 300, bg = 'lightsteelblue2', relief = 'raised')
    #canvas1.pack()

    saveAsButton_CSV = tk.Button(text='Export CSV', command=exportCSV(p.benefits), bg='green', fg='white', font=('helvetica', 12, 'bold'))
    #canvas1.create_window(150, 150, window=saveAsButton_CSV)

    #root.mainloop()

    # #gia na doso logistic cost daneiou elegho an ehei parei epidotisi
    # if sub.subsidy_rate > 0:
    #     logistic_cost = measure_sample['cost']*1.24*(1-sub.subsidy_rate)
    # else:
    #     logistic_cost = measure_sample['cost']*1.24

    # loan = financial_mechanism.Loan(logistic_cost, 0.5, 0.08, 0.024, 3, 0)

    # esco_took_loan = 1
    # if esco_took_loan == 0:
    #     esco_loan = financial_mechanism.Loan(0,0,0,0,0,0)
    # else: 
    #     cost_esco = measure_sample['cost']*1.24
    #     esco_loan = financial_mechanism.Loan(0.8*cost_esco, 0.5, 0.08, 0.024, 10, 0)
    
    # #savings = [7369.68, 7521.68,	7676.93,	7835.51,	7997.49,	8162.93,	8331.93,	8504.56,	8680.90,	8861.02,	9045.03,	9232.99,	9425.01,	9621.17,	9821.56,	10026.27	,10235.42,	10449.08	,10667.37,	10890.38	,11118.23	,11351.02,	11588.86,	11831.87	,12080.16]

    # test_esco = financial_mechanism.Esco(measure_sample, [], 0, " ", 0, " ", 0, 0, 0, 0, esco_loan)

    # test_per = perspective.Perspective(measure_sample, energy_conservation, energy_price_with_taxes, energy_price_growth_rate, selected_costs, selected_benefits, 25, 0.05, sub, loan, test_esco, tax)

    # esco_actor = financial_mechanism.Esco(measure_sample, test_per.savings_per_year_taxable, 0, "npv", 8328, "benefit_share", 0.06, 0.8, 0.7, 8, esco_loan)

    # p =  perspective.Perspective(measure_sample, energy_conservation, energy_price_with_taxes, energy_price_growth_rate, selected_costs, selected_benefits, 25, 0.05, sub, loan, esco_actor, tax)
    #print(p.benefits)
    #print(p.costs)
    #print(p.pure_cash_flow)
    #print(p.b_to_c)
    #print(p.npv)
    #print(p.irr)

    #h = plt.hist(np.random.triangular(0.02, 0.05, 0.1, 1000000), bins=100, density=True)    
    #result_b_to_c = []
    
    #for discount_rate in h[1]:
    #    p = perspective.Perspective(measure_sample, energy_conservation, energy_price_with_taxes, energy_price_growth_rate, selected_costs, selected_benefits, 25, discount_rate, sub, loan, esco_actor, tax)
    #    result_b_to_c.append(p.b_to_c)
    #result_b_to_c.pop()
    
    
    # #print(h[0])
    # print(h[1])
    # print(result_b_to_c)
    # print(len(result_b_to_c), len(h[0]))
    

if __name__ == "__main__":
    main()
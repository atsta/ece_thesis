import energy_measure
import social_investment_analysis
import financial_investment_analysis
import investment_analysis_perspective

import perspective
import financial
import measure

import decimal 

def main():
    #select actors 
    #select measures 
    #check social 
    #check financial 
    #check esco 
    #check every other perspective
    #check for subsidy
    #return cost and whatever for each actor


    #to be taken from db, from simplicity still here
    #will be retrieved from measure module


#temporarily tertiary prices
    energy_price_with_taxes = {
        "electricity": 166.4,
        "diesel_oil": 79.5,
        "motor_gasoline": 134.7, 
        "natural_gas": 62.0, 
        "biomass": 64.6
    }

    energy_price_without_taxes = {
        "electricity": 0.015,
        "diesel_oil": 0.025,
        "motor_gasoline": 0.025, 
        "natural_gas": 0.017, 
        "biomass": 0.02
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

    m = measure.Measure("BOIL", 3)

    selected_benefits = ["energy_savings", "residual_value", "tax_depreciation", "maintenance"]
    selected_costs = ["equipment"]
    
    measure_sample = {
        'name': "BOIL",
        'cost': 33800,
        'lifetime': 20,
        'type': "technical",
        'category': "household"
    }
    sub = financial.Subsidy(measure_sample, 0.4)
    tax = financial.Tax_depreciation(measure_sample, 0.25, 0.1, 10)
    #gia na doso logistic cost daneiou elegho an ehei parei epidotisi
    if sub.subsidy_rate > 0:
        logistic_cost = measure_sample['cost']*1.24*(1-sub.subsidy_rate)
    else:
        logistic_cost = measure_sample['cost']*1.24

    fake_loan = financial.Loan(0,0,0,0,0,0)

    esco = financial.Esco(measure_sample, [], 0, "irr", "metavoli_periodou", 0, 0, 0, 0, fake_loan)

    fake_loan.clear()

    #(logistic_cost, loan_rate, annual_interest, subsidized_interest, loan_period, grace_period):
    loan = financial.Loan(logistic_cost, 0.5, 0.08, 0.024, 3, 0)
    
    psub =  perspective.Perspective(measure_sample, energy_conservation, energy_price_with_taxes, energy_price_growth_rate, selected_costs, selected_benefits, 25, 0.05, sub, loan, esco, tax)
    
    esco.clear()

    esco_took_loan = 1
    if esco_took_loan == 0:
        esco_loan = financial.Loan(0,0,0,0,0,0)
    else: 
        cost_share = 0.8
        cost_esco = cost_share*measure_sample['cost']*1.24
        #print(cost_esco)
        loan.clear()
        esco_loan = financial.Loan(cost_esco, 0.5, 0.08, 0.024, 10, 0)

    esco_actor = financial.Esco(measure_sample, psub.benefits['Energy savings'], psub.avg_ratios, "irr", "metavoli_periodou", 0.06, 0.8, 0.7, 8, esco_loan)
    
    psub.clear()
    
    loan = financial.Loan(logistic_cost, 0.5, 0.08, 0.024, 3, 0)

    p =  perspective.Perspective(measure_sample, energy_conservation, energy_price_with_taxes, energy_price_growth_rate, selected_costs, selected_benefits, 25, 0.05, sub, loan, esco_actor, tax)


if __name__ == "__main__":
    main()
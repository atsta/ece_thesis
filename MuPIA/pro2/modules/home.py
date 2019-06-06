import energy_measure
import social_investment_analysis
import financial_investment_analysis
import investment_analysis_perspective

import perspective
import financial_mechanism
import energy_measure

import decimal 

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

    m = energy_measure.Measure("BOIL", 3)

    selected_benefits = ["energy_savings", "residual_value", "tax_depreciation", "maintenance"]
    selected_costs = ["equipment"]
    
    measure_sample = {
        'name': "BOIL",
        'cost': 33800,
        'lifetime': 20,
        'type': "technical",
        'category': "household"
    }
    
    sub = financial_mechanism.Subsidy(measure_sample, 0.4)
    tax = financial_mechanism.Tax_depreciation(0.25, 0.1, 10)
    
    #gia na doso logistic cost daneiou elegho an ehei parei epidotisi
    if sub.subsidy_rate > 0:
        logistic_cost = measure_sample['cost']*1.24*(1-sub.subsidy_rate)
    else:
        logistic_cost = measure_sample['cost']*1.24

    loan = financial_mechanism.Loan(logistic_cost, 0.5, 0.08, 0.024, 3, 0)

    esco_took_loan = 1
    if esco_took_loan == 0:
        esco_loan = financial_mechanism.Loan(0,0,0,0,0,0)
    else: 
        cost_esco = measure_sample['cost']*1.24
        esco_loan = financial_mechanism.Loan(0.8*cost_esco, 0.5, 0.08, 0.024, 10, 0)
    
    #savings = [7369.68, 7521.68,	7676.93,	7835.51,	7997.49,	8162.93,	8331.93,	8504.56,	8680.90,	8861.02,	9045.03,	9232.99,	9425.01,	9621.17,	9821.56,	10026.27	,10235.42,	10449.08	,10667.37,	10890.38	,11118.23	,11351.02,	11588.86,	11831.87	,12080.16]

    test_esco = financial_mechanism.Esco(measure_sample, [], 0, " ", 0, " ", 0, 0, 0, 0, esco_loan)

    test_per = perspective.Perspective(measure_sample, energy_conservation, energy_price_with_taxes, energy_price_growth_rate, selected_costs, selected_benefits, 25, 0.05, sub, loan, test_esco, tax)

    esco_actor = financial_mechanism.Esco(measure_sample, test_per.savings_per_year_taxable, 0, "profit", 0.35, "benefit_share", 0.06, 0.8, 0.7, 8, esco_loan)

    p =  perspective.Perspective(measure_sample, energy_conservation, energy_price_with_taxes, energy_price_growth_rate, selected_costs, selected_benefits, 25, 0.05, sub, loan, esco_actor, tax)

if __name__ == "__main__":
    main()
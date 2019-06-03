from financial_mechanisms import loan
import investment_analysis_perspective 

import numpy as np  
import decimal

discount_rate = 0.06

class Esco():
    cost_with_taxes = []
    cost_without_taxes = []
    cost_discounted_cash_flow = []
    benefit = []
    benefit_discounted_cash_flow = []
    pure_discounted_cash_flow = []
    esco_npv = 0 
    esco_irr = 0
    esco_pbp = 0
    esco_dpbp = 0
    esco_profit = 0
    def __init__(self, cost, contract_period, benefit_sharing, took_loan):
        self.cost = cost
        self.contract_period = contract_period
        self.benefit_sharing = benefit_sharing
        self.took_loan = took_loan
        
        externalities = []
        for i in range(0, 25):
            externalities.insert(i, 0)

        energy_conservation = {
            "electricity": 0,
            "diesel_oil": 42.0,
            "motor_gasoline": 0, 
            "natural_gas": 65.0, 
            "biomass": 0
        }

        Esco.benefit.append(0)
        inv = investment_analysis_perspective.Perspective(33800, 20, externalities, energy_conservation, decimal.Decimal(0.1), decimal.Decimal(0.4))
        bf = inv.getEnergyBenefits()
        Esco.benefit[0] = bf[0]*self.benefit_sharing
        Esco.benefit_discounted_cash_flow.append(Esco.benefit[0])

        for year in range(1, self.contract_period):
            Esco.benefit.append(bf[year]*self.benefit_sharing)
            Esco.benefit_discounted_cash_flow.append(Esco.benefit[year]/(1+discount_rate**year))
        print(Esco.benefit)

        if self.took_loan == True: 
            #pare daneio
            esco_loan_terms = loan.Terms(0.5, float(self.cost), 0)
            esco_loan_return = loan.Return()

            #init
            Esco.cost_with_taxes.append(loan.Terms.own_funds_amount)
            Esco.cost_without_taxes.append(Esco.cost_with_taxes[0]/1.24)
            Esco.cost_discounted_cash_flow.append(Esco.cost_without_taxes[0])

            for year in range(1, loan.loan_period + 1):
                Esco.cost_with_taxes.append(loan.Return.interest_rate[year] + loan.Return.interest_paid[year])
                Esco.cost_without_taxes.append(loan.Return.interest_rate[year]/1.24 + loan.Return.interest_paid[year])
                Esco.cost_discounted_cash_flow.append(float(Esco.cost_without_taxes[year])/(1+discount_rate**year))
        else: 
            Esco.cost_with_taxes.append(self.cost)
            Esco.cost_without_taxes.append(Esco.cost_with_taxes[0]/decimal.Decimal(1.24))
            Esco.cost_discounted_cash_flow.append(Esco.cost_without_taxes[0])

        if len(Esco.cost_without_taxes) > len(Esco.benefit): 
            for k in range(len(Esco.benefit), len(Esco.cost_without_taxes)):
                Esco.benefit.insert(k-1, 0)
        else:
            for k in range(len(Esco.cost_without_taxes), len(Esco.benefit)):
                Esco.cost_without_taxes.insert(k-1, 0)

        for year in range(0, max(len(Esco.cost_without_taxes),len(Esco.benefit))):
            Esco.pure_discounted_cash_flow.append(Esco.benefit[year]-float(Esco.cost_without_taxes[year]))

        Esco.esco_npv = self.calculate_npv()
        Esco.esco_irr = self.calculate_irr()

        """
        if Esco.benefit[0] > 0:
            Esco.esco_pbp = self.cost/Esco.benefit[0]
        else: 
            Esco.esco_pbp = 0
        """

        #simple payback period, alternative method 
        Esco.esco_pbp = 1 
        diff = Esco.pure_discounted_cash_flow[0]
        while diff < 0:
            diff = diff + Esco.pure_discounted_cash_flow[Esco.esco_pbp]
            Esco.esco_pbp = Esco.esco_pbp +1 
        print(Esco.esco_pbp)

        #discounted payback period
        Esco.esco_dpbp = np.log((Esco.esco_pbp*(1+discount_rate))*((1 + investment_analysis_perspective.Perspective.avg_ratios)/(1+discount_rate)-1)+1)/np.log((1 + investment_analysis_perspective.Perspective.avg_ratios)/(1+discount_rate))
        print(Esco.esco_dpbp)
        
        sum_cost = sum(Esco.cost_without_taxes)
        sum_benefit = sum(Esco.benefit)
        Esco.esco_profit = (sum_benefit-float(sum_cost))/float(sum_cost)

    def calculate_npv(self):
        esco_npv = Esco.pure_discounted_cash_flow[0] + np.npv(discount_rate, Esco.pure_discounted_cash_flow)
        return esco_npv
    def calculate_irr(self):
        esco_irr = np.irr(Esco.pure_discounted_cash_flow)
        return esco_irr




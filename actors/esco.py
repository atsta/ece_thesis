from financial_mechanisms import loan

import numpy as np  
import decimal

discount_rate = decimal.Decimal(0.06)

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
    esco_profit = 0
    def __init__(self, cost, contract_period, benefit_sharing, took_loan):
        self.cost = cost
        self.contract_period = contract_period
        self.benefit_sharing = benefit_sharing
        self.took_loan = took_loan
        #self.fund_take_over_rate = fund_take_over_rate

        Esco.benefit_discounted_cash_flow.insert(0, Esco.benefit[0])

        for year in range(1, self.contract_period):
            Esco.benefit_discounted_cash_flow.insert(year, Esco.benefit[year]/(1+discount_rate**year))

        if self.took_loan == True: 
            #pare daneio
            esco_loan_terms = loan.Terms()
            esco_loan_return = loan.Return()

            #init
            Esco.cost_with_taxes.insert(0, loan.own_funds)
            Esco.cost_without_taxes.insert(0, Esco.cost_with_taxes[0]/decimal.Decimal(1.24))
            Esco.cost_discounted_cash_flow.insert(0, Esco.cost_without_taxes[0])

            for year in range(1, loan.loan_period + 1):
                Esco.cost_with_taxes.insert(year, loan.interest_rate[year] + loan.interest_paid[year])
                Esco.cost_without_taxes.insert(year, loan.interest_rate[year]/decimal.Decimal(1.24) + loan.interest_paid[year])
                Esco.cost_discounted_cash_flow(year, Esco.cost_without_taxes[year]/(1+discount_rate**year))
        else: 
            Esco.cost_with_taxes.insert(0, self.cost)
            Esco.cost_without_taxes.insert(0, Esco.cost_with_taxes[0]/decimal.Decimal(1.24))
            Esco.cost_discounted_cash_flow.insert(0, Esco.cost_without_taxes[0])

        if len(Esco.cost_without_taxes) > len(Esco.benefit): 
            for k in range(len(Esco.benefit), len(Esco.cost_without_taxes)):
                Esco.benefit.insert(k-1, 0)
        else:
            for k in range(len(Esco.cost_without_taxes), len(Esco.benefit)):
                Esco.cost_without_taxes.insert(k-1, 0)

        for year in range(0, max(len(Esco.cost_without_taxes),len(Esco.benefit))):
            Esco.pure_discounted_cash_flow.insert(year, Esco.benefit[year]-Esco.cost_without_taxes[year])

        Esco.esco_npv = self.calculate_npv()
        Esco.esco_irr = self.calculate_irr()
        Esco.esco_pbp = self.cost/Esco.benefit[0]
        sum_cost = sum(Esco.cost_without_taxes)
        sum_benefit = sum(Esco.benefit)
        Esco.esco_profit = (sum_benefit-sum_cost)/sum_cost

    def calculate_npv(self):
        esco_npv = Esco.pure_discounted_cash_flow[0] + np.npv(discount_rate, Esco.pure_discounted_cash_flow)
        return esco_npv
    def calculate_irr(self):
        esco_irr = np.irr(Esco.pure_discounted_cash_flow)
        return esco_irr




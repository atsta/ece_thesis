#numpy, pandas
import numpy as np
import pandas as pd

class Subsidy():
    subsidy_rate = 0
    state_cost = 0
    def __init__(self, measure, subsidy_rate):
        self.measure = measure
        self.subsidy_rate = subsidy_rate

        Subsidy.subsidy_rate = self.subsidy_rate
        Subsidy.state_cost = self.measure['cost']*self.subsidy_rate*1.24


class Tax_depreciation():
    tax_depreciation_rate = 0
    tax_lifetime = 0 
    tax_rate = 0
    def __init__(self, measure, tax_rate, tax_depreciation_rate, tax_lifetime):
        self.tax_rate = tax_rate
        self.tax_depreciation_rate= tax_depreciation_rate
        self.tax_lifetime = tax_lifetime

        Tax_depreciation.tax_depreciation_rate = self.tax_depreciation_rate
        Tax_depreciation.tax_lifetime = self.tax_lifetime
        Tax_depreciation.tax_rate = self.tax_rate

class Loan(): 
    own_funds_rate = 0
    own_fund = 0
    loan_fund = 0
    period = 0
    repayment_amount = 0
    #tok/ki dosi ana etos danismou
    interest_rate_instalment = []
    #xreolisio ana etos danismou
    interest_rate = []
    #tokos
    interest = []
    #epidotisi tokou 
    interest_subsidy = []
    #tokos pliroteos 
    interest_paid = []
    #aneksoflito ipolipo
    unpaid = []
    def __init__(self, logistic_cost, loan_rate, annual_interest, subsidized_interest, loan_period, grace_period):
        self.logistic_cost = logistic_cost #with taxes
        self.loan_rate = loan_rate
        self.annual_interest = annual_interest
        self.subsidized_interest = subsidized_interest
        self.loan_period = loan_period
        self.grace_period = grace_period

        Loan.own_funds_rate = 1 - self.loan_rate
        Loan.own_fund = self.logistic_cost*Loan.own_funds_rate
        Loan.loan_fund = self.loan_rate*self.logistic_cost

        if self.loan_period == 0:
            Loan.period = self.calculate_loan_period()
        else: 
            Loan.period = self.loan_period
        
        self.grace_period_tokos = self.annual_interest*self.grace_period*Loan.loan_fund
        Loan.repayment_amount = Loan.loan_fund + self.grace_period_tokos

        # some intialization
        Loan.unpaid.append(Loan.repayment_amount)
        sum_xreolisio = 0
        Loan.interest_rate_instalment.append(0)
        Loan.interest_rate.append(0)
        Loan.interest.append(0)
        Loan.interest_subsidy.append(0)
        Loan.interest_paid.append(0)

        for year in range(1, Loan.period+1):
            Loan.interest_rate_instalment.append(-np.pmt(self.annual_interest, Loan.period, Loan.repayment_amount, 0))
            Loan.interest_rate.append(-np.ppmt(self.annual_interest, year, Loan.period, Loan.repayment_amount))
            Loan.interest.append(Loan.interest_rate_instalment[year] - Loan.interest_rate[year])
            if year == 1:
                Loan.interest_subsidy.append(Loan.repayment_amount*self.subsidized_interest)
            else:
                sum_xreolisio = sum_xreolisio + Loan.interest_rate[year-1]
                endiameso = Loan.repayment_amount - sum_xreolisio
                Loan.interest_subsidy.append(endiameso*self.subsidized_interest)
            
            Loan.interest_paid.append(Loan.interest[year] - Loan.interest_subsidy[year])
            Loan.unpaid.append(Loan.unpaid[year-1] - Loan.interest_rate[year])

    def calculate_loan_period(self):
        if Loan.loan_fund < 15000: 
            return 3
        else: 
            return 10

class Esco():
    costs = pd.DataFrame([])
    benefits = pd.DataFrame([])

    pure_discounted_cash_flow = []
    benefit_share = 0
    period = 0

    """

    Investment sustainability criteria:
        PV κόστους
        PV οφέλους
        NPV
        B/C ratio
        IRR
        Simple Payback period (years)
        Discounted Payback period (years)

    """
    cost_pv = 0.0 
    benefit_pv = 0.0
    npv = 0.0
    b_to_c = 0.0
    irr = 0.0
    profit = 0.0
    pbp = 0.0
    dpbp = 0.0

    
    def __init__(self, measure, energy_savings, avg_ratios, criterion, criterion_satisfaction, discount_rate, cost_share_rate, benefit_share_rate, contract_period, loan):
        self.measure = measure
        self.energy_savings = energy_savings
        self.avg_ratios = avg_ratios
        self.criterion = criterion
        self.criterion_satisfaction = criterion_satisfaction
        self.discount_rate = discount_rate
        self.cost_share_rate = cost_share_rate
        self.benefit_share_rate = benefit_share_rate 
        self.contract_period = contract_period
        self.loan = loan
        Esco.benefit_share = self.benefit_share_rate
        Esco.period = self.contract_period

        self.savings_per_year_nontaxable = self.energy_savings

        self.construct_benefits_df()
        self.construct_cost_df()
        if Esco.benefit_share > 0:
            self.esco_judgment()


    def construct_benefits_df(self):
        esco_savings = []
        for year in range(self.contract_period):
            esco_savings.append(self.benefit_share_rate*self.savings_per_year_nontaxable[year])
        if self.loan.loan_fund > 0:
            if self.contract_period < self.loan.period:
                diff = self.loan.period - self.contract_period 
                while diff > 0:
                    esco_savings.append(0)
                    diff = diff -1
        Esco.benefits['Energy savings'] = esco_savings
        #print(esco_savings)
        #print(Esco.benefits['Energy savings'])
        flow = []
        Esco.pure_discounted_cash_flow = esco_savings
        #print(Esco.pure_discounted_cash_flow)
        for year in range(self.contract_period):
            flow.append(esco_savings[year]/(1.0 + self.discount_rate)**year)
        if self.loan.loan_fund > 0:
            if self.contract_period < self.loan.period:
                diff = self.loan.period - self.contract_period 
                while diff > 0:
                    Esco.pure_discounted_cash_flow.append(0)
                    flow.append(0)
                    diff = diff -1
        #print(len(esco_savings), len(flow))
        #print(esco_savings) +2 miden dunno why
        #print(flow)
        Esco.benefits['Discounted Cash Flow'] = flow
        #print(Esco.benefits['Discounted Cash Flow'])

    def construct_cost_df(self):
        initial_cost = []
        if self.loan.loan_fund == 0:
            # me foro ? horis
            initial_cost.append(self.measure['cost']*self.cost_share_rate)
            for year in range(1, self.contract_period):
                initial_cost.append(0)
            flow = []
            Esco.costs['Equipment Cost'] = initial_cost
            sum_costs = Esco.costs.sum(axis=1)
            for year in range(self.contract_period):
                Esco.pure_discounted_cash_flow[year] = Esco.pure_discounted_cash_flow[year] - sum_costs[year]
                flow.append(sum_costs[year]/(1.0 + self.discount_rate)**year)
            Esco.costs['Discounted Cash Flow'] = flow
        else: 
            initial_cost.append(self.loan.own_fund)
            for year in range(1, self.loan.period):
                initial_cost.append(self.loan.interest_rate[year]/1.24 + self.loan.interest_paid[year])
                #print(self.loan.interest_paid[year])
            flow = []
            Esco.costs['Equipment Cost'] = initial_cost
            sum_costs = Esco.costs.sum(axis=1)
            for year in range(self.loan.period):
                Esco.pure_discounted_cash_flow[year] = Esco.pure_discounted_cash_flow[year] - sum_costs[year]
                flow.append(sum_costs[year]/(1.0 + self.discount_rate)**year)
            Esco.costs['Discounted Cash Flow'] = flow
        #print(Esco.costs['Equipment Cost'])


    def calculate_simplePBP(self):
        pbp = 1 
        diff = Esco.pure_discounted_cash_flow[0]
        while diff < 0 and pbp < len(Esco.pure_discounted_cash_flow)-1:
            #print(pbp)
            diff = diff + Esco.pure_discounted_cash_flow[pbp]
            pbp = pbp +1 
        return pbp

    def calculate_discountedPBP(self):
        dpbp = np.log((Esco.pbp*(1+self.discount_rate))*((1 + self.avg_ratios)/(1+self.discount_rate)-1)+1)/np.log((1 + self.avg_ratios)/(1+self.discount_rate))
        return dpbp


    def esco_judgment(self):
        Esco.cost_pv = Esco.costs[['Discounted Cash Flow']].sum()
        Esco.benefit_pv = Esco.benefits[['Discounted Cash Flow']].sum()
        #print(Perspective.benefit_pv)

        Esco.npv = Esco.benefit_pv - Esco.cost_pv
        Esco.b_to_c = Esco.benefit_pv/Esco.cost_pv
        Esco.irr =  irr = np.irr(Esco.pure_discounted_cash_flow)
        sum1 = Esco.costs[['Equipment Cost']].sum()
        if not(sum1.empty) :
            Esco.profit = (Esco.benefits[['Energy savings']].sum() - Esco.costs[['Equipment Cost']].sum())/sum1

        Esco.pbp = self.calculate_simplePBP()
        Esco.dpbp = self.calculate_discountedPBP()
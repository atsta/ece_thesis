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
    def clear(self):
        Subsidy.subsidy_rate = 0
        Subsidy.state_cost = 0


class Tax_depreciation():
    tax_depreciation_rate = 0
    tax_lifetime = 0 
    tax_rate = 0
    def __init__(self,tax_rate, tax_depreciation_rate, tax_lifetime):
        self.tax_rate = tax_rate
        self.tax_depreciation_rate= tax_depreciation_rate
        self.tax_lifetime = tax_lifetime

        Tax_depreciation.tax_depreciation_rate = self.tax_depreciation_rate
        Tax_depreciation.tax_lifetime = self.tax_lifetime
        Tax_depreciation.tax_rate = self.tax_rate
    
    def clear(self):
        Tax_depreciation.tax_depreciation_rate = 0
        Tax_depreciation.tax_lifetime = 0 
        Tax_depreciation.tax_rate = 0

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
    
    def clear(self):
        Loan.own_funds_rate = 0
        Loan.own_fund = 0
        Loan.loan_fund = 0
        Loan.period = 0
        Loan.repayment_amount = 0
        #tok/ki dosi ana etos danismou
        Loan.interest_rate_instalment = []
        #xreolisio ana etos danismou
        Loan.interest_rate = []
        #tokos
        Loan.interest = []
        #epidotisi tokou 
        Loan.interest_subsidy = []
        #tokos pliroteos 
        Loan.interest_paid = []
        #aneksoflito ipolipo
        Loan.unpaid = []

class Esco():
    costs = pd.DataFrame([])
    benefits = pd.DataFrame([])

    pure_discounted_cash_flow = []
    benefit_share = 0
    period = 0

    sum_costs = 0
    sum_benefits = 0

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

    
    def __init__(self, measure, energy_savings, avg_ratios, criterion, criterion_value, criterion_satisfaction, discount_rate, cost_share_rate, benefit_share_rate, contract_period, loan):
        self.measure = measure
        self.energy_savings = energy_savings
        self.avg_ratios = avg_ratios
        self.criterion = criterion
        self.criterion_value = criterion_value
        self.criterion_satisfaction = criterion_satisfaction
        self.discount_rate = discount_rate
        self.cost_share_rate = cost_share_rate
        self.benefit_share_rate = benefit_share_rate 
        self.contract_period = contract_period
        self.loan = loan
        Esco.benefit_share = self.benefit_share_rate
        Esco.period = self.contract_period

        self.savings_per_year_nontaxable = self.energy_savings
        self.initialize_criterion_params()
        if Esco.benefit_share > 0:
            self.construct_benefits_df()
            self.construct_cost_df()
            self.esco_criterion_satisfy()
        self.clear()
        Esco.benefit_share = self.benefit_share_rate
        Esco.period = self.contract_period
        if Esco.benefit_share > 0:
            self.construct_benefits_df()
            self.construct_cost_df()
            self.measure_judgement()

    def initialize_criterion_params(self):
        if self.criterion_satisfaction == 'benefit_share':
            self.benefit_share_rate = 1
        elif self.criterion_satisfaction == 'cost_esco':
            self.cost_share_rate = 1

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
            for year in range(self.contract_period):
                if year == 0:            
                    initial_cost.append(self.measure['cost']*self.cost_share_rate)
                else:
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
        dpbp = float(np.log((Esco.pbp*(1+self.discount_rate))*(float((1 + self.avg_ratios))/(1+self.discount_rate)-1)+1))/np.log(float(1 + self.avg_ratios)/(1+self.discount_rate))
        return dpbp

    def get_cost_share(self):
        sum_loan_costs = Esco.costs['Equipment Cost'].sum() - Esco.costs.iloc[0]['Equipment Cost']
        desired_cost = Esco.sum_costs - sum_loan_costs
        #print(desired_cost)
        self.cost_share_rate = desired_cost/Esco.costs.iloc[0]['Equipment Cost']
        print(self.cost_share_rate)
    
    def get_benefit_share(self):
        print(Esco.benefits)
        self.benefit_share = Esco.sum_benefits/Esco.benefits['Energy savings'].sum()
        print(self.benefit_share)

    def calculate_flow_from_pbp(self):
        pbp = self.criterion_value
        if self.criterion_satisfaction == "cost_esco":
            new_cost = Esco.benefits.iloc[pbp-1]['Discounted Cash Flow']
            self.cost_share_rate = new_cost/Esco.costs.iloc[pbp-1]['Discounted Cash Flow']
        if self.criterion_satisfaction == "benefit_share":
            new_benefit = Esco.costs.iloc[pbp-1]['Discounted Cash Flow']
            self.benefit_share_rate = new_benefit/Esco.benefits.iloc[pbp-1]['Discounted Cash Flow']


    def esco_criterion_satisfy(self):
        if self.criterion == "npv":
            if self.criterion_satisfaction == 'cost_esco':
                Esco.sum_costs = Esco.benefits['Discounted Cash Flow'].sum() - self.criterion_value 
                sum_loan_costs = Esco.costs['Discounted Cash Flow'].sum() - Esco.costs.iloc[0]['Discounted Cash Flow']
                desired_cost = Esco.sum_costs - sum_loan_costs
                self.cost_share_rate = desired_cost/Esco.costs.iloc[0]['Discounted Cash Flow']
                print(self.cost_share_rate)            
            else:
                Esco.sum_benefits = Esco.costs['Discounted Cash Flow'].sum() + self.criterion_value
                self.benefit_share_rate = Esco.sum_benefits/Esco.benefits['Discounted Cash Flow'].sum()
        if self.criterion == "b_to_c":
            if self.criterion_satisfaction == 'cost_esco':
                Esco.sum_costs = Esco.benefits['Energy savings'].sum()/self.criterion_value 
                self.get_cost_share()
            else:
                Esco.sum_benefits = Esco.costs['Equipment Cost'].sum()*self.criterion_value
                self.get_benefit_share()
                 
        if self.criterion == "profit":
            if self.criterion_satisfaction == 'cost_esco':
                Esco.sum_costs = Esco.benefits['Energy savings'].sum()/(self.criterion_value + 1)
                self.get_cost_share()
            else:
                Esco.sum_benefits = Esco.costs['Equipment Cost'].sum()*(1+self.criterion_value)
                self.get_benefit_share()

        if self.criterion == 'spbp':
            self.calculate_flow_from_pbp()

    
    def measure_judgement(self):
        #print(Esco.costs)
        #print(Esco.benefits)
        Esco.cost_pv = Esco.costs['Discounted Cash Flow'].sum()
        Esco.benefit_pv = Esco.benefits['Discounted Cash Flow'].sum()
        Esco.npv = Esco.benefit_pv - Esco.cost_pv
        Esco.b_to_c = Esco.benefit_pv/Esco.cost_pv  
        Esco.irr =  irr = np.irr(Esco.pure_discounted_cash_flow)
        print(Esco.irr)
        Esco.pbp = self.calculate_simplePBP()
        Esco.dpbp = self.calculate_discountedPBP()
        sum1 = Esco.costs['Equipment Cost'].sum()
        if sum1 !=0 :
            Esco.profit = (Esco.benefits['Energy savings'].sum() - Esco.costs['Equipment Cost'].sum())/sum1

    
    
    def clear(self):
        Esco.costs = pd.DataFrame([])
        Esco.benefits = pd.DataFrame([])

        Esco.pure_discounted_cash_flow = []
        Esco.benefit_share = 0
        Esco.period = 0
        sum_costs = 0 
        sum_benefits = 0

        Esco.cost_pv = 0.0 
        Esco.benefit_pv = 0.0
        Esco.npv = 0.0
        Esco.b_to_c = 0.0
        Esco.irr = 0.0
        Esco.profit = 0.0
        Esco.pbp = 0.0
        Esco.dpbp = 0.0

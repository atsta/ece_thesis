#numpy, pandas
import numpy as np
import pandas as pd


class Subsidy():
    def __init__(self, measure, subsidy_rate):
        self.measure = measure
        self.subsidy_rate = subsidy_rate
        self.state_cost = 0

        self.state_cost = self.measure['cost']*self.subsidy_rate*1.24
        cost = round(self.state_cost, 2)
        self.state_cost = cost


class Tax_depreciation():
    def __init__(self,tax_rate, tax_depreciation_rate, tax_lifetime):
        self.tax_rate = tax_rate
        self.tax_depreciation_rate= tax_depreciation_rate
        self.tax_lifetime = tax_lifetime


class Loan(): 
    def __init__(self, logistic_cost, loan_rate, annual_interest, subsidized_interest, loan_period, grace_period):
        self.logistic_cost = logistic_cost #with taxes
        self.loan_rate = loan_rate
        self.annual_interest = annual_interest
        self.subsidized_interest = subsidized_interest
        self.loan_period = loan_period
        self.grace_period = grace_period

        self.own_funds_rate = 1 - self.loan_rate
        self.own_fund = self.logistic_cost*self.own_funds_rate
        self.loan_fund = self.loan_rate*self.logistic_cost

        if self.loan_period == 0:
            self.calculate_loan_period()

        self.grace_period_tokos = self.annual_interest*self.grace_period*self.loan_fund
        self.repayment_amount = self.loan_fund + self.grace_period_tokos

        #tok/ki dosi ana etos danismou
        self.interest_rate_instalment = []
        self.interest_rate_instalment.append(0)

        #xreolisio ana etos danismou
        self.interest_rate = []
        self.interest_rate.append(0)

        #tokos
        self.interest = []
        self.interest.append(0)

        #epidotisi tokou 
        self.interest_subsidy = []
        self.interest_subsidy.append(0)

        #tokos pliroteos 
        self.interest_paid = []
        self.interest_paid.append(0)

        #aneksoflito ipolipo
        self.unpaid = []
        self.unpaid.append(self.repayment_amount)
        
        sum_xreolisio = 0

        for year in range(1, self.loan_period+1):
            self.interest_rate_instalment.append(-np.pmt(self.annual_interest, self.loan_period, self.repayment_amount, 0))
            self.interest_rate.append(-np.ppmt(self.annual_interest, year, self.loan_period, self.repayment_amount))
            self.interest.append(self.interest_rate_instalment[year] - self.interest_rate[year])
            if year == 1:
                self.interest_subsidy.append(self.repayment_amount*self.subsidized_interest)
            else:
                sum_xreolisio = sum_xreolisio + self.interest_rate[year-1]
                endiameso = self.repayment_amount - sum_xreolisio
                self.interest_subsidy.append(endiameso*self.subsidized_interest)
            
            self.interest_paid.append(self.interest[year] - self.interest_subsidy[year])
            self.unpaid.append(self.unpaid[year-1] - self.interest_rate[year])

    def calculate_loan_period(self):
        if self.loan_fund < 15000: 
            self.loan_period = 3
        else: 
            self.loan_period = 10
    

class Esco():
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

        self.costs = pd.DataFrame([])
        self.benefits = pd.DataFrame([])
        self.pure_discounted_cash_flow = []

        self.sum_costs = 0
        self.sum_benefits = 0

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
        self.cost_pv = 0.0 
        self.benefit_pv = 0.0
        self.npv = 0.0
        self.b_to_c = 0.0
        self.irr = 0.0
        self.profit = 0.0
        self.pbp = 0.0
        self.dpbp = 0.0

        if self.benefit_share_rate > 0:
            self.initialize_criterion_params()
            self.construct_benefits_df()
            self.construct_cost_df()
            self.esco_criterion_satisfy()
            self.measure_judgement()

    def initialize_criterion_params(self):
        if self.criterion_satisfaction == 'benefit_share':
            self.benefit_share_rate = 1
        elif self.criterion_satisfaction == 'cost_esco':
            self.cost_share_rate = 1

    def construct_benefits_df(self):
        esco_savings = []
        for year in range(len(self.energy_savings)):
            if year < self.contract_period:
                esco_savings.append(self.benefit_share_rate*self.energy_savings[year])
            else:
                esco_savings.append(0)
        rounded_savings = [ round(elem, 2) for elem in esco_savings ]
        self.benefits['Energy savings'] = rounded_savings
        flow = []
        self.pure_discounted_cash_flow = esco_savings
        for year in range(len(self.energy_savings)):
            if year < self.contract_period:
                flow.append(esco_savings[year]/(1.0 + self.discount_rate)**year)
            else:
                self.pure_discounted_cash_flow.append(0)
                flow.append(0)
        rounded_flow = [ round(elem, 2) for elem in flow ]
        self.benefits['Discounted Cash Flow'] = rounded_flow

    def construct_cost_df(self):
        initial_cost = []
        if self.loan.loan_fund > 0:
            esco_loan = Loan(self.measure['cost']*self.cost_share_rate*1.24, self.loan.loan_rate, self.loan.annual_interest, self.loan.subsidized_interest,self.loan.loan_period, self.loan.grace_period)
        
        for year in range(len(self.energy_savings)):
            if self.loan.loan_fund == 0:
                if year == 0:            
                    initial_cost.append(self.measure['cost']*self.cost_share_rate)
                else:
                    initial_cost.append(0)
            else:
                if year == 0:
                    initial_cost.append(esco_loan.own_fund)
                else:
                    if year <= esco_loan.loan_period:
                        initial_cost.append(esco_loan.interest_rate[year]/1.24 + esco_loan.interest_paid[year])
                    else:
                        initial_cost.append(0)
        rounded_cost = [ round(elem, 2) for elem in initial_cost ]
        self.costs['Equipment Cost'] = rounded_cost
        flow = []
        sum_costs = self.costs.sum(axis=1)
        for year in range(len(self.energy_savings)):
            self.pure_discounted_cash_flow[year] = self.pure_discounted_cash_flow[year] - sum_costs[year]
            flow.append(sum_costs[year]/(1.0 + self.discount_rate)**year)
        rounded_flow = [ round(elem, 2) for elem in flow ]
        self.costs['Discounted Cash Flow'] = rounded_flow

    def calculate_simplePBP(self):
        pbp = 1 
        diff = self.pure_discounted_cash_flow[0]
        while diff < 0 and pbp < len(self.pure_discounted_cash_flow)-1:
            diff = diff + self.pure_discounted_cash_flow[pbp]
            pbp = pbp +1 
        return pbp

    def calculate_discountedPBP(self):
        dpbp = float(np.log((self.pbp*(1+self.discount_rate))*(float((1 + self.avg_ratios))/(1+self.discount_rate)-1)+1))/np.log(float(1 + self.avg_ratios)/(1+self.discount_rate))
        rounded_dpbp = round(dpbp, 2)
        dpbp = rounded_dpbp
        return dpbp

    def get_cost_share(self):
        self.cost_share_rate = self.sum_costs/self.costs['Equipment Cost'].sum() 
        rounded_rate = round(self.cost_share_rate, 2)
        self.cost_share_rate = rounded_rate
        print(self.cost_share_rate)
    
    def get_benefit_share(self):
        self.benefit_share_rate = self.sum_benefits/self.benefits['Energy savings'].sum()
        rounded_rate = round(self.benefit_share_rate, 2)
        self.benefit_share_rate = rounded_rate
        print(self.benefit_share_rate)

    def calculate_flow_from_pbp(self):
        pbp = int(self.criterion_value)
        if self.criterion_satisfaction == "cost_esco":
            new_cost = self.benefits.iloc[pbp-1]['Discounted Cash Flow']
            self.cost_share_rate = new_cost/self.costs.iloc[pbp-1]['Discounted Cash Flow']
        if self.criterion_satisfaction == "benefit_share":
            new_benefit = self.costs.iloc[pbp-1]['Discounted Cash Flow']
            self.benefit_share_rate = new_benefit/self.benefits.iloc[pbp-1]['Discounted Cash Flow']

    def esco_criterion_satisfy(self):
        if self.criterion == "npv":
            if self.criterion_satisfaction == 'cost_esco':
                self.sum_costs = self.benefits['Discounted Cash Flow'].sum() - self.criterion_value 
                self.cost_share_rate = self.sum_costs/self.costs['Discounted Cash Flow'].sum() 
                self.costs = pd.DataFrame([])
                self.construct_cost_df()
                print(self.cost_share_rate)            
            else:
                self.sum_benefits = self.costs['Discounted Cash Flow'].sum() + self.criterion_value
                self.benefit_share_rate = self.sum_benefits/self.benefits['Discounted Cash Flow'].sum()
                self.benefits = pd.DataFrame([])
                self.construct_benefits_df()
                print(self.benefit_share_rate)
        if self.criterion == "b_to_c":
            if self.criterion_satisfaction == 'cost_esco':
                self.sum_costs = self.benefits['Energy savings'].sum()/self.criterion_value 
                self.get_cost_share()
                self.costs = pd.DataFrame([])
                self.construct_cost_df()
            else:
                self.sum_benefits = self.costs['Equipment Cost'].sum()*self.criterion_value
                self.get_benefit_share()
                self.benefits = pd.DataFrame([])
                self.construct_benefits_df()

        if self.criterion == "profit":
            if self.criterion_satisfaction == 'cost_esco':
                self.sum_costs = self.benefits['Energy savings'].sum()/(self.criterion_value + 1)
                self.get_cost_share()
                self.costs = pd.DataFrame([])
                self.construct_cost_df()
            else:
                self.sum_benefits = self.costs['Equipment Cost'].sum()*(1+self.criterion_value)
                self.get_benefit_share()
                self.benefits = pd.DataFrame([])
                self.construct_benefits_df()

        if self.criterion == 'spbp':
            self.calculate_flow_from_pbp()

    
    def measure_judgement(self):
        self.cost_pv = self.costs['Discounted Cash Flow'].sum()
        self.benefit_pv = self.benefits['Discounted Cash Flow'].sum()
        self.npv = self.benefit_pv - self.cost_pv
        self.b_to_c = self.benefit_pv/self.cost_pv  
        self.irr =  irr = np.irr(self.pure_discounted_cash_flow)
        self.pbp = self.calculate_simplePBP()
        self.dpbp = self.calculate_discountedPBP()
        sum1 = self.costs['Equipment Cost'].sum()
        if sum1 !=0 :
            self.profit = (self.benefits['Energy savings'].sum() - self.costs['Equipment Cost'].sum())/sum1

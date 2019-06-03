#import perspective
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

        for year in range(1, Loan.period):
            Loan.interest_rate_instalment.append(-np.pmt(self.annual_interest, Loan.period, Loan.repayment_amount, 0))
            sum_xreolisio = sum_xreolisio + Loan.interest_rate_instalment[year]
            Loan.interest_rate.append(-np.ppmt(self.annual_interest, year, Loan.period, Loan.repayment_amount))
            Loan.interest.append(Loan.interest_rate_instalment[year] - Loan.interest_rate[year])
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
    tax_depreciation_rate = 0
    tax_lifetime = 0 
    def __init__(self, measure, tax_rate, tax_depreciation_rate, tax_lifetime):
        self.tax_rate = tax_rate
        self.tax_depreciation_rate= tax_depreciation_rate
        self.tax_lifetime = tax_lifetime

        Tax_depreciation.tax_depreciation_rate = self.tax_depreciation_rate
        Tax_depreciation.tax_lifetime = self.tax_lifetime


import numpy as np  
import decimal


annual_interest_rate = 0.08
hip = round(annual_interest_rate, 2)
annual_interest_rate = hip 

grace_period = 0 

repayment_amount = 0
loan_period = 0
subsidized_interest_rate = 0

class Terms():
    own_funds_rate = 0
    investment_cost_taxable = 0
    own_funds_amount = 0
    loan_amount = 0
    interest_grace = 0
    #initial cost = total cost of investment, without sibsidy
    def __init__(self, loan_rate, initial_cost, subsity_rate):
        self.loan_rate = loan_rate
        self.initial_cost = float(initial_cost)
        self.subsity_rate = subsity_rate

        Terms.own_funds_rate = 1 - self.loan_rate
        Terms.investment_cost_taxable = float(self.initial_cost)*float(1-self.subsity_rate)
        hip = round(Terms.investment_cost_taxable, 2)
        Terms.investment_cost_taxable = hip
        
        #calculate exact amounts (own, from loan)
        Terms.own_funds_amount = float(Terms.own_funds_rate)*Terms.investment_cost_taxable
        Terms.loan_amount = self.loan_rate*Terms.investment_cost_taxable
        hip = round(Terms.loan_amount, 2)
        Terms.loan_amount = hip

        global subsidized_interest_rate 
        subsidized_interest_rate = 0.3*annual_interest_rate
        hip = round(subsidized_interest_rate, 4)
        subsidized_interest_rate = hip
        
        global loan_period 
        loan_period = self.calculate_loan_period()
      
        global grace_period
        grace_period = 0
        endiameso = annual_interest_rate*grace_period
        Terms.interest_grace = Terms.loan_amount*float(endiameso)
        hip = round(Terms.interest_grace, 2)
        Terms.interest_grace = hip 
        
        global repayment_amount 
        repayment_amount = Terms.loan_amount + Terms.interest_grace

    def calculate_loan_period(self):
        if Terms.loan_amount < 15000: 
            return 3
        else: 
            return 10


class Return():
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

    #xreolisio, tokoxreolitiki dosi: interest_rate, interest_rate_instalment
    def __init__(self):
        #init
        Return.interest_rate_instalment.insert(0, 0)
        Return.interest_rate.insert(0, 0)
        self.sum_xreolisio = 0
        Return.interest.insert(0, 0)
        Return.interest_subsidy.insert(0, 0)
        Return.interest_paid.insert(0, 0)
        Return.unpaid.insert(0, repayment_amount)

        for year in range(1, loan_period+1):
            Return.interest_rate_instalment.insert(year, -np.pmt(annual_interest_rate, loan_period, repayment_amount, 0))
            hip = round(Return.interest_rate_instalment[year], 2)
            Return.interest_rate_instalment[year] = hip 
            self.sum_xreolisio = self.sum_xreolisio + Return.interest_rate_instalment[year]
            Return.interest_rate.insert(year, -np.ppmt(annual_interest_rate, year, loan_period, repayment_amount))
            hip = round(Return.interest_rate[year], 2)
            Return.interest_rate[year] = hip 
            Return.interest.insert(year, Return.interest_rate_instalment[year] - Return.interest_rate[year])
            endiameso = repayment_amount - self.sum_xreolisio
            Return.interest_subsidy.insert(year, endiameso*subsidized_interest_rate)
            Return.interest_paid.insert(year, Return.interest[year] - Return.interest_subsidy[year])
            Return.unpaid.insert(year, Return.unpaid[year-1] - Return.interest_rate[year])
            print(Return.unpaid[year])




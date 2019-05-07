import numpy as np  
import decimal


annual_interest_rate = decimal.Decimal(0.08)
hip = round(annual_interest_rate, 2)
annual_interest_rate = hip 

grace_period = 0 

repayment_amount = 0
loan_period = 0
subsidized_interest_rate = 0

class Terms():
    #initial cost = total cost of investment, without sibsidy
    def __init__(self, loan_rate, initial_cost, subsity_rate):
        self.loan_rate = loan_rate
        self.initial_cost = initial_cost
        self.subsity_rate = subsity_rate

        self.own_funds_rate = 1 - self.loan_rate
        self.investment_cost_taxable = self.initial_cost*(1-self.subsity_rate)
        hip = round(self.investment_cost_taxable, 2)
        self.investment_cost_taxable = hip
        
        #calculate exact amounts (own, from loan)
        self.own_funds_amount = self.own_funds_rate*self.investment_cost_taxable
        self.loan_amount = self.loan_rate*self.investment_cost_taxable
        hip = round(self.loan_amount, 2)
        self.loan_amount = hip

        global subsidized_interest_rate 
        subsidized_interest_rate = decimal.Decimal(0.3)*annual_interest_rate
        hip = round(subsidized_interest_rate, 4)
        subsidized_interest_rate = hip
        
        global loan_period 
        loan_period = self.calculate_loan_period()
      
        global grace_period
        grace_period = 0
        endiameso = decimal.Decimal(annual_interest_rate*grace_period)
        self.interest_grace = self.loan_amount*endiameso
        hip = round(self.interest_grace, 2)
        self.interest_grace = hip 
        
        global repayment_amount 
        repayment_amount = self.loan_amount + self.interest_grace

    def calculate_loan_period(self):
        if self.loan_amount < 20000: 
            return 3
        else: 
            return 10


class Return():
    #xreolisio, tokoxreolitiki dosi: interest_rate, interest_rate_instalment
    def __init__(self):
        #tok/ki dosi ana etos danismou
        self.interest_rate_instalment = []
        self.interest_rate_instalment.insert(0, 0)

        #xreolisio ana etos danismou
        self.interest_rate = []
        self.interest_rate.insert(0, 0)
        self.sum_xreolisio = 0

        #tokos
        self.interest = []
        self.interest.insert(0, 0)

        #epidotisi tokou 
        self.interest_subsidy = []
        self.interest_subsidy.insert(0,0)

        #tokos pliroteos 
        self.interest_paid = []
        self.interest_paid.insert(0,0)

        #aneksoflito ipolipo
        self.unpaid = []
        self.unpaid.insert(0, repayment_amount)

        for year in range(1, loan_period+1):
            # print(loan_period)
            self.interest_rate_instalment.insert(year, -np.pmt(annual_interest_rate, loan_period, repayment_amount, 0))
            hip = round(self.interest_rate_instalment[year], 2)
            self.interest_rate_instalment[year] = hip 
            self.sum_xreolisio = self.sum_xreolisio + self.interest_rate_instalment[year]
            self.interest_rate.insert(year, -np.ppmt(annual_interest_rate, year, loan_period, repayment_amount))
            self.interest.insert(year, self.interest_rate_instalment[year] - self.interest_rate[year])
            endiameso = repayment_amount - self.sum_xreolisio
            self.interest_subsidy.insert(year, endiameso*decimal.Decimal(subsidized_interest_rate))
            self.interest_paid.insert(year, self.interest[year] - self.interest_subsidy[year])
            self.unpaid.insert(year, self.unpaid[year-1] - self.interest_rate[year])
            print(self.unpaid[year])




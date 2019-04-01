
annual_interest_rate = 0.8
grace_period = 0 

class Terms():
    def __init__(self, loan_rate, initial_cost, subsity_rate):
        self.loan_rate = loan_rate
        self.initial_cost = initial_cost
        self.subsity_rate = subsity_rate

        self.own_funds_rate = 1 - self.loan_rate
        self.investment_cost_taxable = self.initial_cost*(1-self.subsity_rate)*1.24
        
        #calculate exact amounts (own, from loan)
        self.own_funds_amount = self.own_funds_rate*self.investment_cost_taxable
        self.loan_amount = self.loan_rate*self.investment_cost_taxable

        self.subsidized_interest_rate = 0.3*annual_interest_rate
    
        self.loan_period = self.calculate_loan_period()
        self.interest_grace = self.loan_amount*annual_interest_rate*grace_period
        self.repayment amount = self.loan_amount + self.interest_grace

    def calculate_loan_period(self):
        if self.loan_amout < 20000: 
            return 3
        else: 
            return 10
    #methods to access specs 
    def get_repayment_amout(self):
        return self.get_repayment_amout

class Return():
    def __init__(self):

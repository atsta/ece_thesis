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
    tax_depreciation_rate = 0
    tax_lifetime = 0 
    def __init__(self, measure, tax_rate, tax_depreciation_rate, tax_lifetime):
        self.tax_rate = tax_rate
        self.tax_depreciation_rate= tax_depreciation_rate
        self.tax_lifetime = tax_lifetime

        Tax_depreciation.tax_depreciation_rate = self.tax_depreciation_rate
        Tax_depreciation.tax_lifetime = self.tax_lifetime

class Esco():
    tax_depreciation_rate = 0
    tax_lifetime = 0 
    def __init__(self, measure, tax_rate, tax_depreciation_rate, tax_lifetime):
        self.tax_rate = tax_rate
        self.tax_depreciation_rate= tax_depreciation_rate
        self.tax_lifetime = tax_lifetime

        Tax_depreciation.tax_depreciation_rate = self.tax_depreciation_rate
        Tax_depreciation.tax_lifetime = self.tax_lifetime


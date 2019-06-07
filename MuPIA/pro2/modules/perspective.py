# db libs
import psycopg2
from psycopg2 import Error
import sys
import pprint
import psycopg2.extras

#numpy, pandas
import numpy as np
import pandas as pd

conn_string = "host='localhost' dbname='energy_db' user='postgres' password='45452119'"
# get a connection with energy db
conn = psycopg2.connect(conn_string)

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
    

class Perspective():   
    
    def __init__(self, measure, energy_conservation, energy_price, energy_price_growth_rate, selected_costs, selected_benefits, analysis_period, discount_rate, subsidy, loan, esco, tax_depreciation):
        self.measure = measure
        self.energy_conservation = energy_conservation
        self.energy_price = energy_price
        self.energy_price_growth_rate = energy_price_growth_rate
        self.selected_costs = selected_costs
        self.selected_benefits = selected_benefits
        self.analysis_period = analysis_period
        self.discount_rate = discount_rate
        self.subsidy = subsidy
        self.loan = loan 
        self.esco = esco 
        self.tax_depreciation = tax_depreciation

        # να υπολογιστει
        self.savings_per_year_nontaxable = []

        self.savings_per_year_taxable = []
        self.residual_value = []
        
        self.avg_ratios= 0

        self.costs = pd.DataFrame([])
        self.benefits = pd.DataFrame([])

        self.logistic_cost = 0
        self.pure_cash_flow = []
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
        self.pbp = 0.0
        self.dpbp = 0.0
          
        self.logistic_cost_without_taxes = self.measure['cost']*(1-self.subsidy.subsidy_rate)*(1-self.esco.cost_share_rate)
        self.energy_savings_with_taxes = {
            "electricity": [],
            "diesel_oil": [],
            "motor_gasoline": [], 
            "natural_gas": [], 
            "biomass": []
        }

        self.calculate_savings()
        self.calculate_annual_savings()
        
        self.calculate_residual_value()

        if tax_depreciation.tax_lifetime > 0:
            self.tax_depreciation_per_year = []
            self.calculate_tax_depreciation()

        self.equipment_cost = []
        self.calculate_equipment_cost()
        self.logistic_cost_with_taxes = self.logistic_cost_without_taxes*1.24

        self.construct_benefits_df()
        self.construct_cost_df()
        # whether or not a measure is social sustainable
        # criteria usage 
        self.measure_judgment()


    def calculate_equipment_cost(self):
        if self.esco.cost_share_rate > 0 : 
            loan_fund = (1-self.esco.cost_share_rate)*self.loan.loan_fund/self.loan.loan_rate
            new_loan = Loan(loan_fund, self.loan.loan_rate, self.loan.annual_interest, self.loan.subsidized_interest, self.loan.loan_period, self.loan.grace_period)
        for year in range(self.analysis_period):
            if year == 0:
                if self.loan.loan_fund > 0:
                    #without taxes
                    if self.esco.cost_share_rate > 0 : 
                        self.equipment_cost.append(new_loan.own_fund/1.24)
                    else:
                        self.equipment_cost.append(self.loan.own_fund/1.24)
                else:
                    self.equipment_cost.append(self.logistic_cost_without_taxes)
            elif year == self.measure['lifetime']:
                if self.loan.loan_fund > 0:
                    if year < self.loan.loan_period+1:
                        if self.esco.cost_share_rate > 0 : 
                            self.equipment_cost.append(self.logistic_cost_without_taxes + new_loan.interest_rate[year]/1.24 + new_loan.interest_paid[year])
                        else:
                            self.equipment_cost.append(self.logistic_cost_without_taxes + self.loan.interest_rate[year]/1.24 + self.loan.interest_paid[year])
                    else:
                        self.equipment_cost.append(self.logistic_cost_without_taxes)
                else:
                    self.equipment_cost.append(self.logistic_cost_without_taxes)
            else:
                if self.loan.loan_fund > 0:
                    if year < self.loan.loan_period+1:
                        if self.esco.cost_share_rate > 0:
                            self.equipment_cost.append(new_loan.interest_rate[year]/1.24 + new_loan.interest_paid[year])
                        else:
                            self.equipment_cost.append(self.loan.interest_rate[year]/1.24 + self.loan.interest_paid[year])
                    else:
                        self.equipment_cost.append(0)
                else:
                    self.equipment_cost.append(0)

    def calculate_savings(self):
        self.energy_savings_with_taxes['electricity'].append(self.energy_conservation["electricity"]*float(self.energy_price['electricity']))
        self.energy_savings_with_taxes['diesel_oil'].append(self.energy_conservation["diesel_oil"]*float(self.energy_price['diesel_oil']))
        self.energy_savings_with_taxes['motor_gasoline'].append(self.energy_conservation["motor_gasoline"]*float(self.energy_price['motor_gasoline']))
        self.energy_savings_with_taxes['natural_gas'].append(self.energy_conservation["natural_gas"]*float(self.energy_price['natural_gas']))
        self.energy_savings_with_taxes['biomass'].append(self.energy_conservation["biomass"]*float(self.energy_price['biomass']))
        
        for year in range(1, self.analysis_period):
            self.energy_savings_with_taxes['electricity'].append(self.energy_savings_with_taxes['electricity'][year-1]*float((1+self.energy_price_growth_rate['electricity'])))
            self.energy_savings_with_taxes['diesel_oil'].append(self.energy_savings_with_taxes['diesel_oil'][year-1]*float((1+self.energy_price_growth_rate['diesel_oil'])))
            self.energy_savings_with_taxes['motor_gasoline'].append(self.energy_savings_with_taxes["motor_gasoline"][year-1]*float((1+self.energy_price_growth_rate['motor_gasoline'])))
            self.energy_savings_with_taxes['natural_gas'].append(self.energy_savings_with_taxes["natural_gas"][year-1]*float((1+self.energy_price_growth_rate['natural_gas'])))
            self.energy_savings_with_taxes['biomass'].append(self.energy_savings_with_taxes["biomass"][year-1]*float((1+self.energy_price_growth_rate['biomass'])))

    def calculate_annual_savings(self):
        savings_sum = sum(self.energy_savings_with_taxes[k][0] for k in self.energy_conservation)
        if self.esco.benefit_share_rate == 0 :
            self.savings_per_year_taxable.append(savings_sum)
        else: 
            self.savings_per_year_taxable.append((1-self.esco.benefit_share_rate)*savings_sum)

        for year in range(1, self.analysis_period):
            savings_sum = sum(self.energy_savings_with_taxes[k][year] for k in self.energy_conservation)
            if self.esco.benefit_share_rate == 0 or year >= self.esco.contract_period:
                self.savings_per_year_taxable.append(savings_sum)
            else: 
                self.savings_per_year_taxable.append((1-self.esco.benefit_share_rate)*savings_sum)            

    
    def calculate_residual_value(self):
        for year in range(self.analysis_period):
            if year == self.analysis_period -1:
                self.residual_value.append((2*self.measure['lifetime']-self.analysis_period)*self.logistic_cost_without_taxes*1.24/self.measure['lifetime'])
            else: 
                self.residual_value.append(0)

    def calculate_tax_depreciation(self):
        for year in range(self.analysis_period):
            if year + 1 <= self.tax_depreciation.tax_lifetime:
                self.tax_depreciation_per_year.append(self.logistic_cost_without_taxes*self.tax_depreciation.tax_depreciation_rate*self.tax_depreciation.tax_rate)
            elif year + 1 - self.measure['lifetime'] > 0 and year + 1 - self.measure['lifetime'] <= self.tax_depreciation.tax_lifetime:
                self.tax_depreciation_per_year.append(self.logistic_cost_without_taxes*self.tax_depreciation.tax_depreciation_rate*self.tax_depreciation.tax_rate)
            else:
                self.tax_depreciation_per_year.append(0)

    def get_benefit(self, par):
        try: 
            cursor1 = conn.cursor('cursor_backup', cursor_factory=psycopg2.extras.DictCursor)
            cursor1.execute('SELECT * FROM app2_benefits LIMIT 2000')
            for row in cursor1:
                if(row[0].strip() == self.measure['name']):
                    if par == 'maintenance':
                        return row[2]
                    if par == 'externalities':
                        return row[3]
                    break

        except (Exception, psycopg2.Error) as error :
                    print ("Error while connecting to PostgreSQL", error)
        finally:
            #closing database connection cursor.
            if(conn):
                cursor1.close()

    def construct_benefits_df(self):
        for item in self.selected_benefits:
            if item == 'energy_savings':
                my_rounded_list = [ round(elem, 2) for elem in self.savings_per_year_taxable ]
                self.savings_per_year_taxable = my_rounded_list
                self.benefits['Energy savings'] = self.savings_per_year_taxable
                continue
            if self.subsidy.subsidy_rate > 0 and item == 'tax_depreciation':
                my_rounded_list = [ round(elem, 2) for elem in self.tax_depreciation_per_year ]
                self.tax_depreciation_per_year = my_rounded_list
                self.benefits['Benefit from Tax Depreciation'] = self.tax_depreciation_per_year
                continue
            if item == 'maintenance':
                val = self.get_benefit("maintenance")
                maintenance = []
                for year in range(self.analysis_period):
                    maintenance.append(val)
                my_rounded_list = [ round(elem, 2) for elem in maintenance]
                maintenance = my_rounded_list
                self.benefits['Maintenance'] = maintenance
            if item == 'residual_value':
                my_rounded_list = [ round(elem, 2) for elem in self.residual_value]
                self.residual_value = my_rounded_list
                self.benefits['Residual Value'] = self.residual_value
                continue
        flow = []
        sum_benefits = self.benefits.sum(axis=1)
        for year in range(len(sum_benefits)):
            self.pure_cash_flow.append(sum_benefits[year])
        for year in range(self.analysis_period):
            flow.append(sum_benefits[year]/(1.0 + self.discount_rate)**year)
        my_rounded_list = [ round(elem, 2) for elem in flow]
        flow = my_rounded_list
        self.benefits['Discounted Cash Flow'] = flow

    def construct_cost_df(self):
        for item in self.selected_costs:
            if item == 'equipment':
                my_rounded_list = [ round(elem, 2) for elem in self.equipment_cost ]    
                self.equipment_cost = my_rounded_list          
                self.costs['Equipment Cost'] = self.equipment_cost
        flow = []
        sum_costs = self.costs.sum(axis=1)
        for year in range(self.analysis_period):
            self.pure_cash_flow[year] = self.pure_cash_flow[year] - sum_costs[year]
            flow.append(sum_costs[year]/(1.0 + self.discount_rate)**year)
        my_rounded_list = [ round(elem, 2) for elem in flow ]
        self.costs['Discounted Cash Flow'] = my_rounded_list


    def calculate_avg_ratios(self):
        sum_ratios = 0
        num_ratios = 0
        if self.energy_conservation['electricity'] > 0:
            num_ratios = num_ratios + 1 
            sum_ratios = sum_ratios  + self.energy_price_growth_rate['electricity']
        if self.energy_conservation['diesel_oil'] > 0:
            num_ratios = num_ratios + 1 
            sum_ratios = sum_ratios  + self.energy_price_growth_rate['diesel_oil']
        if self.energy_conservation['motor_gasoline'] > 0:
            num_ratios = num_ratios + 1 
            sum_ratios = sum_ratios  + self.energy_price_growth_rate['motor_gasoline']
        if self.energy_conservation["natural_gas"] > 0:
            num_ratios = num_ratios + 1 
            sum_ratios = sum_ratios + self.energy_price_growth_rate["natural_gas"]
        if self.energy_conservation["biomass"] > 0:
            num_ratios = num_ratios +1 
            sum_ratios = sum_ratios + self.energy_price_growth_rate["biomass"]
        self.avg_ratios = sum_ratios/num_ratios 

    def calculate_simplePBP(self):
        pbp = 1 
        diff = self.pure_cash_flow[0]
        while diff < 0 and pbp < self.analysis_period-1:
            diff = diff + self.pure_cash_flow[pbp]
            pbp = pbp +1 
        return pbp

    def calculate_discountedPBP(self):
        self.calculate_avg_ratios()
        dpbp = float(np.log((self.pbp*(1+self.discount_rate))*(float((1 + self.avg_ratios))/(1+self.discount_rate)-1)+1))/np.log(float(1 + self.avg_ratios)/(1+self.discount_rate))
        return dpbp

    def measure_judgment(self):
        self.cost_pv = round(self.costs['Discounted Cash Flow'].sum(), 2)
        self.benefit_pv = round(self.benefits['Discounted Cash Flow'].sum(),2)
        self.npv = round(self.benefit_pv - self.cost_pv, 2)
        self.b_to_c = round(self.benefit_pv/self.cost_pv, 2)
        self.irr = round(np.irr(self.pure_cash_flow), 2)
        self.pbp = round(self.calculate_simplePBP(), 2)
        self.dpbp = round(self.calculate_discountedPBP(), 2)
    
    
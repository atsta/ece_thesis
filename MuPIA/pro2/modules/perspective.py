# db libs
import psycopg2
from psycopg2 import Error
import sys
import pprint
import psycopg2.extras

#numpy, pandas
import numpy as np
import pandas as pd

import financial

conn_string = "host='localhost' dbname='energy_db' user='postgres' password='45452119'"
# get a connection with energy db
conn = psycopg2.connect(conn_string)


class Perspective():   
    # να υπολογιστει
    savings_per_year_nontaxable = []
    # να μπουν σε σελφ
    savings_per_year_taxable = []
    residual_value = []
    
    #για πειμπακ
    avg_ratios= 0

    costs = pd.DataFrame([])
    benefits = pd.DataFrame([])

    logistic_cost = 0
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
    pbp = 0.0
    dpbp = 0.0
    def __delete__(self, val):
        del self

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
          
        self.logistic_cost_without_taxes = self.measure['cost']
        self.energy_savings_with_taxes = {
            "electricity": [],
            "diesel_oil": [],
            "motor_gasoline": [], 
            "natural_gas": [], 
            "biomass": []
        }

        #calculate energy savings with taxes
        self.calculate_savings()
        #total savings per year
        self.calculate_annual_savings()
        
        self.calculate_residual_value()

        if tax_depreciation.tax_lifetime > 0:
            self.tax_depreciation_per_year = []
            self.calculate_tax_depreciation()

        self.equipment_cost = []
        self.calculate_equipment_cost()
        Perspective.logistic_cost = self.logistic_cost_without_taxes*1.24

        self.construct_benefits_df()
        self.construct_cost_df()
        # whether or not a measure is social sustainable
        # criteria usage 
        self.measure_judgment()


    def calculate_equipment_cost(self):
        for year in range(self.analysis_period):
            if year == 0:
                if self.loan.loan_fund > 0:
                    self.equipment_cost.append(self.loan.own_fund)
                else:
                    self.equipment_cost.append(self.logistic_cost_without_taxes)
            elif year == self.measure['lifetime']:
                if self.loan.loan_fund > 0:
                    if year < self.loan.period+1:
                        self.equipment_cost.append(self.logistic_cost_without_taxes + self.loan.interest_rate[year]/1.24 + self.loan.interest_paid[year])
                    else:
                        self.equipment_cost.append(self.logistic_cost_without_taxes)
                else:
                    self.equipment_cost.append(self.logistic_cost_without_taxes)
            else:
                if self.loan.loan_fund > 0:
                    if year < self.loan.period+1:
                        self.equipment_cost.append(self.loan.interest_rate[year]/1.24 + self.loan.interest_paid[year])
                    else:
                        self.equipment_cost.append(0)
                else:
                    self.equipment_cost.append(0)
        #print(self.equipment_cost)

    def calculate_savings(self):
        self.energy_savings_with_taxes['electricity'].append(self.energy_conservation["electricity"]*self.energy_price['electricity'])
        self.energy_savings_with_taxes['diesel_oil'].append(self.energy_conservation["diesel_oil"]*self.energy_price['diesel_oil'])
        self.energy_savings_with_taxes['motor_gasoline'].append(self.energy_conservation["motor_gasoline"]*self.energy_price['motor_gasoline'])
        self.energy_savings_with_taxes['natural_gas'].append(self.energy_conservation["natural_gas"]*self.energy_price['natural_gas'])
        self.energy_savings_with_taxes['biomass'].append(self.energy_conservation["biomass"]*self.energy_price['biomass'])
        #print(self.energy_savings_with_taxes)
        
        for year in range(1, self.analysis_period):
            self.energy_savings_with_taxes['electricity'].append(self.energy_savings_with_taxes['electricity'][year-1]*(1+self.energy_price_growth_rate['electricity']))
            self.energy_savings_with_taxes['diesel_oil'].append(self.energy_savings_with_taxes['diesel_oil'][year-1]*(1+self.energy_price_growth_rate['diesel_oil']))
            self.energy_savings_with_taxes['motor_gasoline'].append(self.energy_savings_with_taxes["motor_gasoline"][year-1]*(1+self.energy_price_growth_rate['motor_gasoline']))
            self.energy_savings_with_taxes['natural_gas'].append(self.energy_savings_with_taxes["natural_gas"][year-1]*(1+self.energy_price_growth_rate['natural_gas']))
            self.energy_savings_with_taxes['biomass'].append(self.energy_savings_with_taxes["biomass"][year-1]*(1+self.energy_price_growth_rate['biomass']))

    def calculate_annual_savings(self):
        savings_sum = sum(self.energy_savings_with_taxes[k][0] for k in self.energy_conservation)
        if self.esco.benefit_share ==0 :
            Perspective.savings_per_year_taxable.append(savings_sum)
        else: 
            Perspective.savings_per_year_taxable.append((1-self.esco.benefit_share)*savings_sum)

        for year in range(1, self.analysis_period):
            savings_sum = sum(self.energy_savings_with_taxes[k][year] for k in self.energy_conservation)
            if self.esco.benefit_share ==0 or year >= self.esco.period:
                Perspective.savings_per_year_taxable.append(savings_sum)
            else: 
                Perspective.savings_per_year_taxable.append((1-self.esco.benefit_share)*savings_sum)            
        #print(Perspective.savings_per_year_taxable)

    
    def calculate_residual_value(self):
        self.logistic_cost_without_taxes = self.measure['cost']*(1-self.subsidy.subsidy_rate)
        for year in range(self.analysis_period):
            if year == self.analysis_period -1:
                Perspective.residual_value.append((2*self.measure['lifetime']-self.analysis_period)*self.logistic_cost_without_taxes*1.24/self.measure['lifetime'])
            else: 
                Perspective.residual_value.append(0)

    def calculate_tax_depreciation(self):
        for year in range(self.analysis_period):
            if year + 1 <= self.tax_depreciation.tax_lifetime:
                self.tax_depreciation_per_year.append(self.logistic_cost_without_taxes*self.tax_depreciation.tax_depreciation_rate*self.tax_depreciation.tax_rate)
                #self.benefits['Tax depreciation'][year] = self.logistic_cost_without_taxes*self.tax_depreciation*decimal.Decimal(0.25)
            elif year + 1 - self.measure['lifetime'] > 0 and year + 1 - self.measure['lifetime'] <= self.tax_depreciation.tax_lifetime:
                self.tax_depreciation_per_year.append(self.logistic_cost_without_taxes*self.tax_depreciation.tax_depreciation_rate*self.tax_depreciation.tax_rate)
                #self.benefits['Tax depreciation'][year] = self.logistic_cost_without_taxes*self.tax_depreciation*decimal.Decimal(0.25)
            else:
                self.tax_depreciation_per_year.append(0)
                #self.benefits['Tax depreciation'][year] = 0
        #print(self.tax_depreciation_per_year)

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
                print(len(Perspective.savings_per_year_taxable))
                Perspective.benefits['Energy savings'] = Perspective.savings_per_year_taxable

                continue
            if self.subsidy.subsidy_rate > 0 and item == 'tax_depreciation':
                Perspective.benefits['Benefit from Tax Depreciation'] = self.tax_depreciation_per_year
                continue
            if item == 'maintenance':
                val = self.get_benefit("maintenance")
                #print(val)
                maintenance = []
                for year in range(self.analysis_period):
                    maintenance.append(val)
                Perspective.benefits['Maintenance'] = maintenance
            if item == 'residual_value':
                Perspective.benefits['Residual Value'] = Perspective.residual_value
                continue
        flow = []
        sum_benefits = Perspective.benefits.sum(axis=1)
        Perspective.pure_cash_flow = sum_benefits
        #print(Perspective.pure_cash_flow)
        for year in range(self.analysis_period):
            flow.append(sum_benefits[year]/(1.0 + self.discount_rate)**year)
        Perspective.benefits['Discounted Cash Flow'] = flow
        #print(flow)
        #print(Perspective.benefits)

    def construct_cost_df(self):
        for item in self.selected_costs:
            if item == 'equipment':
                Perspective.costs['Equipment Cost'] = self.equipment_cost
            # if loan add special column gia tis doseis
            
        flow = []
        sum_costs = Perspective.costs.sum(axis=1)
        for year in range(self.analysis_period):
            Perspective.pure_cash_flow[year] = Perspective.pure_cash_flow[year] - sum_costs[year]
            flow.append(sum_costs[year]/(1.0 + self.discount_rate)**year)
        Perspective.costs['Discounted Cash Flow'] = flow
        #print(Perspective.costs)


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
        Perspective.avg_ratios = sum_ratios/num_ratios 

    def calculate_simplePBP(self):
        pbp = 1 
        diff = Perspective.pure_cash_flow[0]
        while diff < 0:
            diff = diff + Perspective.pure_cash_flow[pbp]
            pbp = pbp +1 
        return pbp

    def calculate_discountedPBP(self):
        self.calculate_avg_ratios()
        dpbp = np.log((Perspective.pbp*(1+self.discount_rate))*((1 + Perspective.avg_ratios)/(1+self.discount_rate)-1)+1)/np.log((1 + Perspective.avg_ratios)/(1+self.discount_rate))
        return dpbp

    def measure_judgment(self):
        Perspective.cost_pv = Perspective.costs[['Discounted Cash Flow']].sum()
        Perspective.benefit_pv = Perspective.benefits[['Discounted Cash Flow']].sum()
        #print(Perspective.benefit_pv)

        Perspective.npv = Perspective.benefit_pv - Perspective.cost_pv
        Perspective.b_to_c = Perspective.benefit_pv/Perspective.cost_pv
        Perspective.irr =  irr = np.irr(Perspective.pure_cash_flow)
        Perspective.pbp = self.calculate_simplePBP()
        Perspective.dpbp = self.calculate_discountedPBP()

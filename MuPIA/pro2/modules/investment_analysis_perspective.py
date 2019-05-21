# db libs
import psycopg2
from psycopg2 import Error
import sys
import pprint
import psycopg2.extras

#numpy, pandas
import numpy as np
import pandas as pd

import decimal

analysis_period = 25
discount_rate = 0.05
tax_lifetime = 10

cost_growth_rate = {
    "electricity": 1.015,
    "diesel_oil": 1.025,
    "motor_gasoline": 1.025, 
    "natural_gas": 1.017, 
    "biomass": 1.02
}

conn_string = "host='localhost' dbname='energy_db' user='postgres' password='45452119'"
# get a connection with energy db
conn = psycopg2.connect(conn_string)

class Perspective():
    sum_ratios = 0
    num_ratios = 0
    avg_ratios = 0
    def __init__(self, cost, lifetime, externalities, energy_conservation, tax_depreciation, subsidy_rate):
        self.cost = cost
        self.lifetime = lifetime
        self.externalities = externalities
        self.energy_conservation = energy_conservation
        self.tax_depreciation = tax_depreciation
        self.subsidy_rate = subsidy_rate
        self.savings_per_year_taxable = []
        self.savings_per_year_taxable.append(0)

        self.logistic_cost_without_taxes = self.cost*(1-self.subsidy_rate)
    
        self.costs = pd.DataFrame([])
        self.benefits = pd.DataFrame([])

        self.cost_pv = 0 
        self.benefit_pv = 0

        self.energy_savings_with_taxes = {
            "electricity": [],
            "diesel_oil": [],
            "motor_gasoline": [], 
            "natural_gas": [], 
            "biomass": []
        }
        self.energy_savings_with_taxes["electricity"].append(0)
        self.energy_savings_with_taxes["diesel_oil"].append(0)
        self.energy_savings_with_taxes["motor_gasoline"].append(0)
        self.energy_savings_with_taxes["natural_gas"].append(0)
        self.energy_savings_with_taxes["biomass"].append(0)   

        #calculate energy savings with taxes
        self.calculate_savings_t()
        Perspective.avg_ratios = Perspective.sum_ratios/Perspective.num_ratios
        print(Perspective.avg_ratios)
        self.calculate_energy_cost_per_year()

        #calculate energy savings during period of analysis
        self.savings_calculation_per_year()

        #construct cost per year dataframe 
        self.create_costdf()

        #construct benefit per year dataframe
        self.create_benefitdf()
        
        #determine whether or not a measure is acceptable 
        self.measure_judgment()

    def create_benefitdf(self):
        for year in range(analysis_period):
            self.benefits = self.benefits.append(pd.DataFrame({'Discounted cash flow': 0, 'Energy savings': 0, 'Maintenance': 0, 'Residual value': 0, 'Tax depreciation': 0}, index=[0]), ignore_index=True)
        self.benefits["Energy savings"] = self.savings_per_year_taxable
        for year in range(analysis_period):
            if year == analysis_period:
                self.benefits['Residual_value'][year] = 2*float(self.lifetime-analysis_period)*float(self.logistic_cost_without_taxes)*1.24/self.lifetime
            else: 
                self.benefits['Residual value'][year] = 0
            if year + 1 > analysis_period:
                self.benefits['Maintenance'][year] = 0
            else: 
                self.benefits['Maintenance'][year] = 100
            if year + 1 <= tax_lifetime:
                self.benefits['Tax depreciation'][year] = self.logistic_cost_without_taxes*self.tax_depreciation*decimal.Decimal(0.25)
            elif year + 1 - self.lifetime > 0 and year + 1 - self.lifetime <= tax_lifetime:
                self.benefits['Tax depreciation'][year] = self.logistic_cost_without_taxes*self.tax_depreciation*decimal.Decimal(0.25)
            else:
                self.benefits['Tax depreciation'][year] = 0
            #ipologismos proeks. tam. rois
            self.benefits['Discounted cash flow'][year] = (self.benefits['Energy savings'][year] + self.benefits['Residual value'][year] + self.benefits['Maintenance'][year] + self.benefits['Tax depreciation'][year])/(1+discount_rate)**year 
            self.total_benefit_flow = self.benefits[['Discounted cash flow']].sum()
        print(self.benefits)

    def create_costdf(self):
        for year in range(analysis_period):
            if year==0 or year==self.lifetime:
                self.costs = self.costs.append(pd.DataFrame({'Technology_cost': self.logistic_cost_without_taxes, 'Discounted_cash_flow': float(self.logistic_cost_without_taxes)/(1+discount_rate)**year}, index=[0]), ignore_index=True)
            else: 
                self.costs = self.costs.append(pd.DataFrame({'Technology_cost': 0, 'Discounted_cash_flow': 0}, index=[0]), ignore_index=True)
            self.total_cost_flow = self.costs[['Discounted_cash_flow']].sum()
        print(self.costs)

    def calculate_savings_t(self):
        try: 
            cursor1 = conn.cursor('cursor_backup', cursor_factory=psycopg2.extras.DictCursor)
            cursor1.execute('SELECT * FROM energy_cost LIMIT 1000')
            #energy price WITHOUT tax
            for row in cursor1:
                if(row[0].strip() == 'Electricity hh'):
                    self.energy_savings_with_taxes["electricity"][0] = self.energy_conservation["electricity"]*float(row[2])
                    if self.energy_conservation['electricity'] > 0 :
                        Perspective.num_ratios = Perspective.num_ratios +1 
                        Perspective.sum_ratios = Perspective.sum_ratios - 1+cost_growth_rate['electricity']
                    #print(row[2])
                if(row[0].strip() == 'Diesel oil hh'):
                    self.energy_savings_with_taxes["diesel_oil"][0] = self.energy_conservation["diesel_oil"]*float(row[2])
                    #print(self.energy_savings_with_taxes['diesel_oil'][0])
                    #print(row[1])
                    if self.energy_conservation['diesel_oil'] > 0 :
                        Perspective.num_ratios = Perspective.num_ratios +1 
                        Perspective.sum_ratios = Perspective.sum_ratios - 1 +cost_growth_rate['diesel_oil']
                if(row[0].strip() == 'Motor Gasoline'):
                    self.energy_savings_with_taxes["motor_gasoline"][0] = self.energy_conservation["motor_gasoline"]*float(row[2])
                    #print(row[2])
                    if self.energy_conservation['motor_gasoline'] > 0 :
                        Perspective.num_ratios = Perspective.num_ratios +1 
                        Perspective.sum_ratios = Perspective.sum_ratios - 1+cost_growth_rate['motor_gasoline']
                if(row[0].strip() == 'Natural gas hh'):
                    self.energy_savings_with_taxes["natural_gas"][0] = self.energy_conservation["natural_gas"]*float(row[2])
                    #print(row[1])
                    if self.energy_conservation["natural_gas"] > 0 :
                        Perspective.num_ratios = Perspective.num_ratios +1 
                        Perspective.sum_ratios = Perspective.sum_ratios - 1+cost_growth_rate["natural_gas"]
                if(row[0].strip() == 'Biomass hh'):
                    self.energy_savings_with_taxes["biomass"][0] = self.energy_conservation["biomass"]*float(row[2])
                    #print(row[2])
                    if self.energy_conservation["biomass"] > 0 :
                        Perspective.num_ratios = Perspective.num_ratios +1 
                        Perspective.sum_ratios = Perspective.sum_ratios - 1+cost_growth_rate["biomass"]
        except (Exception, psycopg2.Error) as error :
            print ("Error while connecting to PostgreSQL", error)
        finally:
            #closing database connection cursor.
            if(conn):
                cursor1.close()
    
    def savings_calculation_per_year(self):
        self.savings_per_year_taxable[0] = self.energy_savings_with_taxes["electricity"][0]+ self.energy_savings_with_taxes["diesel_oil"][0] + self.energy_savings_with_taxes["motor_gasoline"][0] + self.energy_savings_with_taxes["natural_gas"][0] + float(self.energy_savings_with_taxes["biomass"][0])
        for year in range(1, analysis_period):
            #with taxes
            self.savings_per_year_taxable.append(self.energy_savings_with_taxes["electricity"][year]+ self.energy_savings_with_taxes["diesel_oil"][year] + self.energy_savings_with_taxes["motor_gasoline"][year] + self.energy_savings_with_taxes["natural_gas"][year] + self.energy_savings_with_taxes["biomass"][year])
            
    def calculate_energy_cost_per_year(self):
        for year in range(1, analysis_period):
            #calculate energy costs during analysis period, based on growth rate of each energy genre
            #with taxes
            self.energy_savings_with_taxes["electricity"].append(self.energy_savings_with_taxes["electricity"][year-1]*cost_growth_rate["electricity"])
            self.energy_savings_with_taxes["diesel_oil"].append(self.energy_savings_with_taxes["diesel_oil"][year-1]*cost_growth_rate["diesel_oil"])
            self.energy_savings_with_taxes["motor_gasoline"].append(self.energy_savings_with_taxes["motor_gasoline"][year-1]*cost_growth_rate["motor_gasoline"])
            self.energy_savings_with_taxes["natural_gas"].append(self.energy_savings_with_taxes["natural_gas"][year-1]*cost_growth_rate["natural_gas"])
            self.energy_savings_with_taxes["biomass"].append(float(self.energy_savings_with_taxes["biomass"][year-1])*cost_growth_rate["biomass"])
          

    def calculate_benefit_pv(self):
        #initialization
        benefit_per_year = [] 
        benefit_per_year.insert(0, self.savings_per_year_taxable[0] + self.externalities[0])
        total_flow = benefit_per_year[0]/(1+discount_rate)**0

        #calculate residual value at the end of analysis period
        residual_value = (2*self.lifetime - analysis_period)/(self.cost/self.lifetime)

        #annual calculation 
        for year in range(1, analysis_period):
            benefit_per_year.insert(year, self.savings_per_year_taxable[year] + self.externalities[year])
            if year == analysis_period: 
                total_flow = total_flow + benefit_per_year[year]/(1 + discount_rate)**year + residual_value
            else: 
                total_flow = total_flow + benefit_per_year[year]/(1 + discount_rate)**year 
        return total_flow
          

    def calculate_cost_pv(self):
        #initialization
        cost_per_year = [] 
        cost_per_year.insert(0, self.cost)
        total_flow = cost_per_year[0]/(1+discount_rate)**0

        #annual calculation 
        for year in range(1, analysis_period):
            if year == self.lifetime: 
                cost_per_year.insert(year, self.cost)
            else: 
                cost_per_year.insert(year, 0)
            #calculate cost cash flow in total 
            total_flow = total_flow + cost_per_year[year]/(1+discount_rate)**year
        return total_flow
       
    def measure_judgment(self):
        judgement = []
        #calculate cost of technology during analysis period and in total
        self.cost_pv = self.calculate_cost_pv()
        
        #calculate benefits of technology during analysis period and in total
        self.benefit_pv = self.calculate_benefit_pv()
    
        #calculate NPV
        npv = self.benefit_pv - self.cost_pv
        #print(npv)
        if (npv > 0):
            judgement.insert(0, "investment sustainable according to npv criterion")
        else: 
            judgement.insert(0, "investment not sustainable according to npv criterion")
        
        #calσculate B/C 
        b_to_c = self.benefit_pv/self.cost_pv
        #print(b_to_c)
        if (b_to_c > 1):
            judgement.insert(1, "investment sustainable according to B/C criterion")
        else: 
            judgement.insert(1, "investment not sustainable according to B/C criterion")
        
        #calculate IRR

        return judgement
    
    def getEnergyBenefits(self):
        return self.benefits['Energy savings']

 
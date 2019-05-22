# db libs
import psycopg2
from psycopg2 import Error
import sys
import pprint
import psycopg2.extras

import numpy as np
import decimal

analysis_period = 25
discount_rate = 0.04

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

class Social():   
    cost_per_year = []
    benefit_per_year = []
    savings_per_year_nontaxable = []
    pure_cash_flow = []
    residual_value = 0
    avg_ratios= 0

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
    
    def __init__(self, cost, lifetime, externalities, energy_conservation):
        self.cost = cost
        self.lifetime = lifetime
        self.externalities = externalities
        self.energy_conservation = energy_conservation
        
        self.energy_savings_without_taxes = {
            "electricity": [],
            "diesel_oil": [],
            "motor_gasoline": [], 
            "natural_gas": [], 
            "biomass": []
        }

        # energy savings with untaxable price of fuel 
        self.calculate_savings_wt()

        # per year per fuel savings based on energy prices growth rate
        self.calculate_energy_cost_per_year()

        # total per year savings 
        self.savings_calculation_per_year()

        # whether or not a measure is social sustainable
        # criteria usage 
        self.measure_judgment()

    def calculate_savings_wt(self):
        sum_ratios = 0
        num_ratios = 0
        #get energy cost data from cost table of energy db
        try: 
            cursor1 = conn.cursor('cursor_backup', cursor_factory=psycopg2.extras.DictCursor)
            cursor1.execute('SELECT * FROM energy_cost LIMIT 1000')
            for row in cursor1:
                if(row[0].strip() == 'Electricity hh'):
                    self.energy_savings_without_taxes["electricity"].append(self.energy_conservation["electricity"]*float(row[2]))
                    if self.energy_conservation['electricity'] > 0 :
                            num_ratios = num_ratios +1 
                            sum_ratios = sum_ratios - 1+cost_growth_rate['electricity']
                    print(self.energy_savings_without_taxes["electricity"])
                if(row[0].strip() == 'Diesel oil hh'):
                    self.energy_savings_without_taxes["diesel_oil"].append(self.energy_conservation["diesel_oil"]*float(row[2]))
                    if self.energy_conservation['diesel_oil'] > 0 :
                        num_ratios = num_ratios +1 
                        sum_ratios = sum_ratios - 1 +cost_growth_rate['diesel_oil']
                    print(self.energy_savings_without_taxes["diesel_oil"])
                if(row[0].strip() == 'Motor Gasoline'):
                    self.energy_savings_without_taxes["motor_gasoline"].append(self.energy_conservation["motor_gasoline"]*float(row[2]))
                    if self.energy_conservation['motor_gasoline'] > 0 :
                        num_ratios = num_ratios +1 
                        sum_ratios = sum_ratios - 1+cost_growth_rate['motor_gasoline']
                    print(self.energy_savings_without_taxes["motor_gasoline"])
                if(row[0].strip() == 'Natural gas hh'):
                    self.energy_savings_without_taxes["natural_gas"].append(self.energy_conservation["natural_gas"]*float(row[2]))
                    if self.energy_conservation["natural_gas"] > 0 :
                        num_ratios = num_ratios +1 
                        sum_ratios = sum_ratios - 1+cost_growth_rate["natural_gas"]
                    print(self.energy_savings_without_taxes["natural_gas"])
                if(row[0].strip() == 'Biomass hh'):
                    self.energy_savings_without_taxes["biomass"].append(self.energy_conservation["biomass"]*float(row[2]))
                    if self.energy_conservation["biomass"] > 0 :
                        num_ratios = num_ratios +1 
                        sum_ratios = sum_ratios - 1+cost_growth_rate["biomass"]
                    print(self.energy_savings_without_taxes["biomass"])    
            Social.avg_ratios = sum_ratios/num_ratios
            #print(self.energy_savings_without_taxes["diesel_oil"])
            #print(self.energy_conservation["diesel_oil"])   
        except (Exception, psycopg2.Error) as error :
            print ("Error while connecting to PostgreSQL", error)
        finally:
            #closing database connection cursor.
            if(conn):
                cursor1.close()

    def savings_calculation_per_year(self):
        savings_sum = sum(self.energy_savings_without_taxes[k][0]*self.energy_conservation[k] for k in self.energy_conservation)
        Social.savings_per_year_nontaxable.append(savings_sum)
        #print(self.energy_savings_without_taxes["natural_gas"][0])
        for year in range(1, analysis_period):
            savings_sum = sum(self.energy_savings_without_taxes[k][year] for k in self.energy_conservation)
            Social.savings_per_year_nontaxable.append(savings_sum)
    
    def calculate_energy_cost_per_year(self):
        for year in range(1, analysis_period):
            self.energy_savings_without_taxes["electricity"].append(float(self.energy_savings_without_taxes["electricity"][year-1])*cost_growth_rate["electricity"])
            self.energy_savings_without_taxes["diesel_oil"].append(float(self.energy_savings_without_taxes["diesel_oil"][year-1])*cost_growth_rate["diesel_oil"])
            self.energy_savings_without_taxes["motor_gasoline"].append(float(self.energy_savings_without_taxes["motor_gasoline"][year-1])*cost_growth_rate["motor_gasoline"])
            self.energy_savings_without_taxes["natural_gas"].append(float(self.energy_savings_without_taxes["natural_gas"][year-1])*cost_growth_rate["natural_gas"])
            self.energy_savings_without_taxes["biomass"].append(float(self.energy_savings_without_taxes["biomass"][year-1])*cost_growth_rate["biomass"])

    def calculate_benefit_pv(self):
        # init
        Social.benefit_per_year.append(Social.savings_per_year_nontaxable[0] + self.externalities[0])
        total_flow = float(Social.benefit_per_year[0])/(1+discount_rate)**0

        # residual value at the end of analysis period
        Social.residual_value = (2*self.lifetime - analysis_period)/(self.cost/self.lifetime)

        # annual calculation 
        for year in range(1, analysis_period):
            Social.benefit_per_year.append(Social.savings_per_year_nontaxable[year] + float(self.externalities[year]))
            if year == analysis_period -1: 
                total_flow = total_flow + Social.benefit_per_year[year]/(1 + discount_rate)**year + float(Social.residual_value)
            else: 
                total_flow = total_flow + Social.benefit_per_year[year]/(1 + discount_rate)**year 
        
        return total_flow
          

    def calculate_cost_pv(self):
        # init
        Social.cost_per_year.append(self.cost)
        total_flow = float(Social.cost_per_year[0])/(1+discount_rate)**0

        # annual calculation 
        for year in range(1, analysis_period):
            if year == self.lifetime: 
                Social.cost_per_year.append(self.cost)
            else: 
                Social.cost_per_year.append(0)
            total_flow = total_flow + float(Social.cost_per_year[year])/(1+discount_rate)**year
        
        return total_flow

    def calculate_npv(self):
        npv = Social.benefit_pv - Social.cost_pv
        if (npv > 0):
            print("investment sustainable according to npv criterion")
        else: 
            print("investment not sustainable according to npv criterion")
        return npv
       
    def calculate_b_to_c(self):
        bc = Social.benefit_pv/Social.cost_pv
        if (bc > 1):
            print("investment sustainable according to B/C criterion")
        else: 
            print("investment not sustainable according to B/C criterion")
        return bc

    def calculate_cash_flow(self):
        for year in range(analysis_period):
            if year == analysis_period -1: 
                Social.pure_cash_flow.append(float(Social.savings_per_year_nontaxable[year]) + float(Social.residual_value) + float(self.externalities[year]) - float(Social.cost_per_year[year]))
            else: 
                Social.pure_cash_flow.append(float(Social.savings_per_year_nontaxable[year]) + float(self.externalities[year]) - float(Social.cost_per_year[year]))


    def calculate_irr(self):
        irr = np.irr(Social.pure_cash_flow)
        return irr

    def calculate_simplePBP(self):
        pbp = 1 
        diff = Social.pure_cash_flow[0]
        while diff < 0:
            diff = diff + Social.pure_cash_flow[pbp]
            pbp = pbp +1 
        return pbp

    def calculate_discountedPBP(self):
        dpbp = np.log((Social.pbp*(1+discount_rate))*((1 + Social.avg_ratios)/(1+discount_rate)-1)+1)/np.log((1 + Social.avg_ratios)/(1+discount_rate))
        return dpbp

    def measure_judgment(self):
        #judgement = []
        # cost of technology in total
        Social.cost_pv = self.calculate_cost_pv()
        
        # benefits of technology in total
        Social.benefit_pv = self.calculate_benefit_pv()
    
        Social.npv = self.calculate_npv() 
        Social.b_to_c = self.calculate_b_to_c()

        self.calculate_cash_flow()
        Social.irr = self.calculate_irr()

        Social.pbp = self.calculate_simplePBP()
        Social.dpbp = self.calculate_discountedPBP()
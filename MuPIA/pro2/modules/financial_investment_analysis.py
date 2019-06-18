# db libs
import psycopg2
from psycopg2 import Error
import sys
import pprint
import psycopg2.extras

import numpy as np
import pandas as pd

conn_string = "host='localhost' dbname='energy_db' user='postgres' password='45452119'"
# get a connection with energy db
conn = psycopg2.connect(conn_string)

class Financial():   
    """Class of Social Investment CBA.
    """
    def __init__(self, measure, energy_conservation, energy_price, energy_price_growth_rate, selected_costs, selected_benefits, analysis_period, discount_rate):
        """
        Args:
            measure (dict): name of the examined measure.
            energy_conservation (dict) : conservation of the examined measure.
            energy_price (dict): energy price with taxes due to financial analysis.
            energy_price_growth_rate (dict): growth rate of energy price.
            selected_costs (list of str): costs that take part in the analysis, selected by the user.
            selected_benefits (list of str): benefits that take part in the analysis, selected by the user.
            analysis_period (int)
            discount_rate (float)
        """
        
        self.measure = measure
        self.energy_conservation = energy_conservation
        self.energy_price = energy_price
        self.energy_price_growth_rate = energy_price_growth_rate
        self.selected_costs = selected_costs
        self.selected_benefits = selected_benefits
        self.analysis_period = analysis_period
        self.discount_rate = discount_rate
        
        self.savings_per_year = []
        self.residual_value = []

        self.avg_ratios= 0
        self.costs = pd.DataFrame([])
        self.benefits = pd.DataFrame([])
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

        self.energy_savings = {
            "electricity": [],
            "diesel_oil": [],
            "motor_gasoline": [], 
            "natural_gas": [], 
            "biomass": []
        }

        # energy savings with untaxable price of fuel 
        self.calculate_savings_wt()

        # total per year savings 
        self.savings_calculation_per_year()

        self.calculate_residual_value()
        self.equipment_cost = []
        self.calculate_equipment_cost()

        self.construct_benefits_df()
        self.construct_cost_df()
        # whether or not a measure is social sustainable
        # criteria usage 
        self.measure_judgment()

    def calculate_savings_wt(self):
        self.energy_savings['electricity'].append(self.energy_conservation["electricity"]*float(self.energy_price['electricity']))
        self.energy_savings['diesel_oil'].append(self.energy_conservation["diesel_oil"]*float(self.energy_price['diesel_oil']))
        self.energy_savings['motor_gasoline'].append(self.energy_conservation["motor_gasoline"]*float(self.energy_price['motor_gasoline']))
        self.energy_savings['natural_gas'].append(self.energy_conservation["natural_gas"]*float(self.energy_price['natural_gas']))
        self.energy_savings['biomass'].append(self.energy_conservation["biomass"]*float(self.energy_price['biomass']))
        
        for year in range(1, self.analysis_period):
            self.energy_savings['electricity'].append(self.energy_savings['electricity'][year-1]*float((1+self.energy_price_growth_rate['electricity'])))
            self.energy_savings['diesel_oil'].append(self.energy_savings['diesel_oil'][year-1]*float((1+self.energy_price_growth_rate['diesel_oil'])))
            self.energy_savings['motor_gasoline'].append(self.energy_savings["motor_gasoline"][year-1]*float((1+self.energy_price_growth_rate['motor_gasoline'])))
            self.energy_savings['natural_gas'].append(self.energy_savings["natural_gas"][year-1]*float((1+self.energy_price_growth_rate['natural_gas'])))
            self.energy_savings['biomass'].append(self.energy_savings["biomass"][year-1]*float((1+self.energy_price_growth_rate['biomass'])))

    def savings_calculation_per_year(self):
        savings_sum = sum(self.energy_savings[k][0] for k in self.energy_conservation)
        self.savings_per_year.append(savings_sum)

        for year in range(1, self.analysis_period):
            savings_sum = sum(self.energy_savings[k][year] for k in self.energy_conservation)
            self.savings_per_year.append(savings_sum)
    
    def calculate_residual_value(self):
        for year in range(self.analysis_period):
            if year == self.analysis_period -1:
                self.residual_value.append((2*self.measure['lifetime']-self.analysis_period)*self.measure['cost']*1.24/self.measure['lifetime'])
            else: 
                self.residual_value.append(0)

    def get_benefit(self, par):
        try: 
            cursor1 = conn.cursor('cursor_backup', cursor_factory=psycopg2.extras.DictCursor)
            cursor1.execute('SELECT * FROM app2_benefits LIMIT 2000')
            for row in cursor1:
                if(row[0].strip() == self.measure['name']):
                    if par == 'maintenance':
                        return row[1]
                    if par == 'externalities':
                        return row[2]
                    if par == 'value_growth':
                        return row[3]
                    if par == 'work_efficiency':
                        return row[4]
                    if par == 'employability':
                        return row[5]
                    if par == 'other_benefits':
                        return row[6]
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
                my_rounded_list = [ round(elem, 2) for elem in self.savings_per_year ]
                self.savings_per_year = my_rounded_list
                self.benefits['Energy savings'] = self.savings_per_year
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
    
    def calculate_equipment_cost(self):
        for year in range(self.analysis_period):
            if year == 0:
                self.equipment_cost.append(1.24*self.measure['cost'])
            elif year == self.measure['lifetime']:
                    self.equipment_cost.append(1.24*self.measure['cost'])
            else:
                    self.equipment_cost.append(0)

    def construct_cost_df(self):
        for item in self.selected_costs:
            if item == 'equipment':
                my_rounded_list = [ round(elem, 2) for elem in self.equipment_cost ]    
                self.equipment_cost = my_rounded_list          
                self.costs['Equipment Cost'] = self.equipment_cost
        flow = []
        sum_costs = self.costs.sum(axis=1)
        for year in range(self.analysis_period):
            self.pure_cash_flow[year] = round(self.pure_cash_flow[year] - sum_costs[year], 2)
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
        if num_ratios > 0 : 
            self.avg_ratios = sum_ratios/num_ratios 
        else: 
            self.avg_ratios = 0

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
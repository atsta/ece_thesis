# db libs
import psycopg2
from psycopg2 import Error
import sys
import pprint
import psycopg2.extras

analysis_period = 25
discount_rate = 0.04
cost_growth_rate = {
    "electricity": 1.5,
    "diesel_oil": 2.5,
    "motor_gasoline": 2.5, 
    "natural_gas": 1.7, 
    "biomass": 2
}

conn_string = "host='localhost' dbname='energy_db' user='postgres' password='45452119'"
# get a connection with energy db
conn = psycopg2.connect(conn_string)

class Social():   
    def __init__(self, cost, lifetime, externalities, energy_conservation):
        self.cost = cost
        self.lifetime = lifetime
        self.externalities = externalities
        self.energy_conservation = energy_conservation
        self.savings_per_year_nontaxable = []
        self.cost_pv = 0 
        self.benefit_pv = 0
        self.energy_savings_without_taxes = {
            "electricity": [],
            "diesel_oil": [],
            "motor_gasoline": [], 
            "natural_gas": [], 
            "biomass": []
        }
        
        #calculate energy savings without taxes, social analysis
        self.calculate_savings_wt()
        self.calculate_energy_cost_per_year()

        #calculate energy savings during period of analysis
        self.savings_calculation_per_year()

        #determin whethe or not a measure is social acceptable 
        self.measure_judgment()

    def calculate_savings_wt(self):
        #get energy cost data from cost table of energy db
        try: 
            cursor1 = conn.cursor('cursor_backup', cursor_factory=psycopg2.extras.DictCursor)
            cursor1.execute('SELECT * FROM energy_cost LIMIT 1000')
            for row in cursor1:
                if(row[0].strip() == 'Electricity hh'):
                    self.energy_savings_without_taxes["electricity"].insert(0, self.energy_conservation["electricity"]*row[2])
                if(row[0].strip() == 'Diesel oil hh'):
                    self.energy_savings_without_taxes["diesel_oil"].insert(0,self.energy_conservation["diesel_oil"]*row[2])
                if(row[0].strip() == 'Motor Gasoline'):
                    self.energy_savings_without_taxes["motor_gasoline"].insert(0, self.energy_conservation["motor_gasoline"]*row[2])
                if(row[0].strip() == 'Natural gas hh'):
                    self.energy_savings_without_taxes["natural_gas"].insert(0, self.energy_conservation["natural_gas"]*row[2])
                if(row[0].strip() == 'Biomass hh'):
                    self.energy_savings_without_taxes["biomass"].insert(0, self.energy_conservation["biomass"]*row[2])
                    
        except (Exception, psycopg2.Error) as error :
            print ("Error while connecting to PostgreSQL", error)
        finally:
            #closing database connection cursor.
            if(conn):
                cursor1.close()

    def savings_calculation_per_year(self):
        self.savings_per_year_nontaxable.insert(0, self.energy_savings_without_taxes["electricity"][0]*self.energy_conservation["electricity"]+ self.energy_savings_without_taxes["diesel_oil"][0]*self.energy_conservation["diesel_oil"]+ self.energy_savings_without_taxes["motor_gasoline"][0]*self.energy_conservation["motor_gasoline"] + self.energy_savings_without_taxes["natural_gas"][0]*self.energy_conservation["natural_gas"] + self.energy_savings_without_taxes["biomass"][0]*self.energy_conservation["biomass"])
        for year in range(1, analysis_period):
            self.savings_per_year_nontaxable.insert(year, self.energy_savings_without_taxes["electricity"][year]*self.energy_conservation["electricity"]+ self.energy_savings_without_taxes["diesel_oil"][year]*self.energy_conservation["diesel_oil"]+ self.energy_savings_without_taxes["motor_gasoline"][year]*self.energy_conservation["motor_gasoline"] + self.energy_savings_without_taxes["natural_gas"][year]*self.energy_conservation["natural_gas"] + self.energy_savings_without_taxes["biomass"][year]*self.energy_conservation["biomass"])
    
    def calculate_energy_cost_per_year(self):
        for year in range(1, analysis_period):
            self.energy_savings_without_taxes["electricity"].insert(year, self.energy_savings_without_taxes["electricity"][year-1]*cost_growth_rate["electricity"])
            self.energy_savings_without_taxes["diesel_oil"].insert(year, self.energy_savings_without_taxes["diesel_oil"][year-1]*cost_growth_rate["diesel_oil"])
            self.energy_savings_without_taxes["motor_gasoline"].insert(year, self.energy_savings_without_taxes["motor_gasoline"][year-1]*cost_growth_rate["motor_gasoline"])
            self.energy_savings_without_taxes["natural_gas"].insert(year, self.energy_savings_without_taxes["natural_gas"][year-1]*cost_growth_rate["natural_gas"])
            self.energy_savings_without_taxes["biomass"].insert(year, self.energy_savings_without_taxes["biomass"][year-1]*cost_growth_rate["biomass"])

    def calculate_benefit_pv(self):
        #initialization
        benefit_per_year = [] 
        benefit_per_year[0] = self.savings_per_year_nontaxable[0] + self.externalities[0]
        total_flow = benefit_per_year[0]/(1+discount_rate)**0

        #calculate residual value at the end of analysis period
        residual_value = (2*self.lifetime - analysis_period)/(self.cost/self.lifetime)

        #annual calculation 
        for year in range(1, analysis_period):
            benefit_per_year.insert(year, self.savings_per_year_nontaxable[year] + self.externalities[year])
            if year == analysis_period: 
                total_flow = total_flow + benefit_per_year[year]/(1 + discount_rate)**year + residual_value
            else: 
                total_flow = total_flow + benefit_per_year[year]/(1 + discount_rate)**year 
        return total_flow
          

    def calculate_cost_pv(self):
        #initialization
        cost_per_year = [] 
        cost_per_year[0] = self.cost
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
        if (npv > 0):
            judgement.insert(0, "investment sustainable according to npv criterion")
        else: 
            judgement.insert(0, "investment not sustainable according to npv criterion")
        
        #calculate B/C 
        b_to_c = self.benefit_pv/self.cost_pv
        if (b_to_c > 1):
            judgement.insert(1, "investment sustainable according to B/C criterion")
        else: 
            judgement.insert(1, "investment not sustainable according to B/C criterion")
        
        #calculate IRR

        return judgement
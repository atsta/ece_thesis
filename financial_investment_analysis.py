# db libs
import psycopg2
from psycopg2 import Error
import sys
import pprint
import psycopg2.extras


analysis_period = 25
discount_rate = 0.05
cost_growth_rate = {
    "electricity": 1.5,
    "diesel_oil": 2.5,
    "motor_gasoline": 2.5, 
    "natural_gas": 1.7, 
    "biomass": 2
}

conn_string = "host='localhost' dbname='energy_db' user='postgres' password='45452119'"
# get a connection
conn = psycopg2.connect(conn_string)

class Financial():   
    def __init__(self, cost, lifetime, externalities, energy_conservation):
        self.cost = cost
        self.lifetime = lifetime
        self.externalities = externalities
        self.energy_conservation = energy_conservation
        self.savings_per_year_taxable = []
        self.cost_pv_per_year = []
        self.total_cost_pv = 0 
        self.benefit_pv_per_year = []
        self.total_benefit_pv = 0
        
        self.energy_savings_with_taxes = {
            "electricity": [],
            "diesel_oil": [],
            "motor_gasoline": [], 
            "natural_gas": [], 
            "biomass": []
        }

        self.calculate_savings_t()
        self.calculate_energy_cost_per_year()

        #calculate energy savings during period of analysis
        self.savings_calculation_per_year()

        #calculate cost of technology during analysis period and in total
        self.calculate_cost_pv()

        #calculate benefits of technology during analysis period and in total
        self.calculate_benefit_pv()

    def calculate_savings_t(self):
        try: 
            cursor1 = conn.cursor('cursor_backup', cursor_factory=psycopg2.extras.DictCursor)
            cursor1.execute('SELECT * FROM energy_cost LIMIT 1000')

            for row in cursor1:
                if(row[0].strip() == 'Electricity hh'):
                    self.energy_savings_with_taxes["electricity"].insert(0, self.energy_conservation["electricity"]*row[3])
                if(row[0].strip() == 'Diesel oil hh'):
                    self.energy_savings_with_taxes["diesel_oil"].insert(0, self.energy_conservation["diesel_oil"]*row[3])
                if(row[0].strip() == 'Motor Gasoline'):
                    self.energy_savings_with_taxes["motor_gasoline"].insert(0, self.energy_conservation["motor_gasoline"]*row[3])
                if(row[0].strip() == 'Natural gas hh'):
                    self.energy_savings_with_taxes["natural_gas"].insert(0, self.energy_conservation["natural_gas"]*row[3])
                if(row[0].strip() == 'Biomass hh'):
                    self.energy_savings_with_taxes["biomass"].insert(0, self.energy_conservation["biomass"]*row[3])   
        
        except (Exception, psycopg2.Error) as error :
            print ("Error while connecting to PostgreSQL", error)
        finally:
            #closing database connection cursor.
            if(conn):
                cursor1.close()
    

    def savings_calculation_per_year(self):
        self.savings_per_year_taxable.insert(0, self.energy_savings_with_taxes["electricity"][0]*self.energy_conservation["electricity"]+ self.energy_savings_with_taxes["diesel_oil"][0]*self.energy_conservation["diesel_oil"]+ self.energy_savings_with_taxes["motor_gasoline"][0]*self.energy_conservation["motor_gasoline"] + self.energy_savings_with_taxes["natural_gas"][0]*self.energy_conservation["natural_gas"] + self.energy_savings_with_taxes["biomass"][0]*self.energy_conservation["biomass"])

        for year in range(1, analysis_period):
            #with taxes
            self.savings_per_year_taxable[year] = self.energy_savings_with_taxes["electricity"][year]*self.energy_conservation["electricity"]+ self.energy_savings_with_taxes["diesel_oil"][year]*self.energy_conservation["diesel_oil"]+ self.energy_savings_with_taxes["motor_gasoline"][year]*self.energy_conservation["motor_gasoline"] + self.energy_savings_with_taxes["natural_gas"][year]*self.energy_conservation["natural_gas"] + self.energy_savings_with_taxes["biomass"][year]*self.energy_conservation["biomass"]
            
    def calculate_energy_cost_per_year(self):
        for year in range(1, analysis_period):
            #calculate energy costs during analysis period, based on growth rate of each energy genre
            #with taxes
            self.energy_savings_with_taxes["electricity"][year] = self.energy_savings_with_taxes["electricity"][year-1]*cost_growth_rate["electricity"]
            self.energy_savings_with_taxes["diesel_oil"][year] = self.energy_savings_with_taxes["diesel_oil"][year-1]*cost_growth_rate["diesel_oil"]
            self.energy_savings_with_taxes["motor_gasoline"][year] = self.energy_savings_with_taxes["motor_gasoline"][year-1]*cost_growth_rate["motor_gasoline"]
            self.energy_savings_with_taxes["natural_gas"][year] = self.energy_savings_with_taxes["natural_gas"][year-1]*cost_growth_rate["natural_gas"]
            self.energy_savings_with_taxes["biomass"][year] = self.energy_savings_with_taxes["biomass"][year-1]*cost_growth_rate["biomass"]

    
    def calculate_benefit_pv(self):
        self.total_benefit_pv = 0
        
        for year in range(analysis_period):
            self.benefit_pv_per_year[year] = self.savings_per_year_taxable[year]+ self.externalities[year]
        for year in range(analysis_period):
            self.benefit_pv_per_year[year] = self.benefit_pv_per_year[year]/((1+discount_rate)**year)
            self.total_benefit_pv = self.total_benefit_pv + self.benefit_pv_per_year[year]

    def calculate_cost_pv(self):
        self.cost_pv_per_year[0] = self.cost
        self.total_cost_pv = self.cost_pv_per_year[0]

        #annual calculation 
        for year in range(1, analysis_period):
            if year == self.lifetime: 
                self.cost_pv_per_year[year] = self.cost
            else: 
                self.cost_pv_per_year[year] = 0
            #calculate in total 
            self.total_cost_pv = self.total_cost_pv + self.cost_pv_per_year[year]
    
    def measure_judgment(self):
        judgement = "investment sustainable"
        judgement = "investment not sustainable"
        return judgement
       

   
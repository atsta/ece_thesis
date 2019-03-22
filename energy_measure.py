# db libs
import psycopg2
from psycopg2 import Error
import sys
import pprint
import psycopg2.extras


conn_string = "host='localhost' dbname='energy_db' user='postgres' password='45452119'"
# get a connection
conn = psycopg2.connect(conn_string)

cost_growth_rate = {
    "electricity": 1.5,
    "diesel_oil": 2.5,
    "motor_gasoline": 2.5, 
    "natural_gas": 1.7, 
    "biomass": 2
}

analysis_period = 25

class Measure():   
    discount_rate = 0.04

    def __init__(self, name):
       
        self.name = name
        self.cost = 0
        self.lifetime = 0 
        self.externalities = []
        self.savings_per_year_taxable = []
        self.savings_per_year_nontaxable = []

        self.energy_savings_with_taxes = {
            "electricity": [],
            "diesel_oil": [],
            "motor_gasoline": [], 
            "natural_gas": [], 
            "biomass": []
        }
        self.energy_savings_without_taxes = {
            "electricity": [],
            "diesel_oil": [],
            "motor_gasoline": [], 
            "natural_gas": [], 
            "biomass": []
        }
        self.energy_conservation = {
            "electricity": 0,
            "diesel_oil": 0,
            "motor_gasoline": 0, 
            "natural_gas": 0, 
            "biomass": 0
        }

        self.initialize_measure()
        self.calculate_energy_cost_per_year()

        #calculate energy savings during period of analysis
        
        #with taxes
        self.savings_per_year_taxable.insert(0, self.energy_savings_with_taxes["electricity"][0]*self.energy_conservation["electricity"]+ self.energy_savings_with_taxes["diesel_oil"][0]*self.energy_conservation["diesel_oil"]+ self.energy_savings_with_taxes["motor_gasoline"][0]*self.energy_conservation["motor_gasoline"] + self.energy_savings_with_taxes["natural_gas"][0]*self.energy_conservation["natural_gas"] + self.energy_savings_with_taxes["biomass"][0]*self.energy_conservation["biomass"])
        
        #without taxes
        self.savings_per_year_nontaxable.insert(0, self.energy_savings_without_taxes["electricity"][0]*self.energy_conservation["electricity"]+ self.energy_savings_without_taxes["diesel_oil"][0]*self.energy_conservation["diesel_oil"]+ self.energy_savings_without_taxes["motor_gasoline"][0]*self.energy_conservation["motor_gasoline"] + self.energy_savings_without_taxes["natural_gas"][0]*self.energy_conservation["natural_gas"] + self.energy_savings_without_taxes["biomass"][0]*self.energy_conservation["biomass"])

        self.savings_calculation_per_year()
       

    def calculate_energy_cost_per_year(self):
        for year in range(1, analysis_period):
            #calculate energy costs during analysis period, based on growth rate of each energy genre
            #with taxes
            self.energy_savings_with_taxes["electricity"][year] = self.energy_savings_with_taxes["electricity"][year-1]*cost_growth_rate["electricity"]
            self.energy_savings_with_taxes["diesel_oil"][year] = self.energy_savings_with_taxes["diesel_oil"][year-1]*cost_growth_rate["diesel_oil"]
            self.energy_savings_with_taxes["motor_gasoline"][year] = self.energy_savings_with_taxes["motor_gasoline"][year-1]*cost_growth_rate["motor_gasoline"]
            self.energy_savings_with_taxes["natural_gas"][year] = self.energy_savings_with_taxes["natural_gas"][year-1]*cost_growth_rate["natural_gas"]
            self.energy_savings_with_taxes["biomass"][year] = self.energy_savings_with_taxes["biomass"][year-1]*cost_growth_rate["biomass"]

            #without taxes
            self.energy_savings_without_taxes["electricity"][year] = self.energy_savings_without_taxes["electricity"][year-1]*cost_growth_rate["electricity"]
            self.energy_savings_without_taxes["diesel_oil"][year] = self.energy_savings_without_taxes["diesel_oil"][year-1]*cost_growth_rate["diesel_oil"]
            self.energy_savings_without_taxes["motor_gasoline"][year] = self.energy_savings_without_taxes["motor_gasoline"][year-1]*cost_growth_rate["motor_gasoline"]
            self.energy_savings_without_taxes["natural_gas"][year] = self.energy_savings_without_taxes["natural_gas"][year-1]*cost_growth_rate["natural_gas"]
            self.energy_savings_without_taxes["biomass"][year] = self.energy_savings_without_taxes["biomass"][year-1]*cost_growth_rate["biomass"]



    def initialize_measure(self):
        self.calculate_specs()
        self.calculate_savings_wt()
        self.calculate_savings_t()
    
    def savings_calculation_per_year(self):
        for year in range(1, analysis_period):
            #with taxes
            self.savings_per_year_taxable[year] = self.energy_savings_with_taxes["electricity"][year]*self.energy_conservation["electricity"]+ self.energy_savings_with_taxes["diesel_oil"][year]*self.energy_conservation["diesel_oil"]+ self.energy_savings_with_taxes["motor_gasoline"][year]*self.energy_conservation["motor_gasoline"] + self.energy_savings_with_taxes["natural_gas"][year]*self.energy_conservation["natural_gas"] + self.energy_savings_with_taxes["biomass"][year]*self.energy_conservation["biomass"]
            
            #without taxes
            self.savings_per_year_nontaxable[year] = self.energy_savings_without_taxes["electricity"][year]*self.energy_conservation["electricity"]+ self.energy_savings_without_taxes["diesel_oil"][year]*self.energy_conservation["diesel_oil"]+ self.energy_savings_without_taxes["motor_gasoline"][year]*self.energy_conservation["motor_gasoline"] + self.energy_savings_without_taxes["natural_gas"][year]*self.energy_conservation["natural_gas"] + self.energy_savings_without_taxes["biomass"][year]*self.energy_conservation["biomass"]


    def calculate_specs(self):
        try:
            cursor2 = conn.cursor('cursor_backup', cursor_factory=psycopg2.extras.DictCursor)
            cursor2.execute('SELECT * FROM energy_measure LIMIT 1000')

            for row in cursor2:
                if row[0] == self.name:
                    self.lifetime = 25
                    self.cost = row[4]
                    self.energy_conservation["electricity"] = row[6]
                    self.energy_conservation["diesel_oil"] = row[7]
                    self.energy_conservation["motor_gasoline"] = row[8]
                    self.energy_conservation["natural_gas"] = row[9]
                    self.energy_conservation["biomas"] = row[10]
                    break
        except (Exception, psycopg2.Error) as error :
            print ("Error while connecting to PostgreSQL", error)
        finally:
            #closing database connection cursor.
            if(conn):
                cursor2.close()

    def calculate_savings_wt(self):
        print("ok")
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
    

# db libs
import psycopg2
from psycopg2 import Error
import sys
import pprint
import psycopg2.extras

import decimal


conn_string = "host='localhost' dbname='energy_db' user='postgres' password='45452119'"
# get a connection with energy db
conn = psycopg2.connect(conn_string)

class Measure():   
    def __init__(self, name):
        self.name = name
        self.cost = 0
        self.lifetime = 0 
        self.externalities = []
        self.energy_conservation = {
            "electricity": 0,
            "diesel_oil": 0,
            "motor_gasoline": 0, 
            "natural_gas": 0, 
            "biomass": 0
        }
        
        #initialize an energy measure with its specs
        self.initialize_measure()
      
        #calculate benefit externalities during analysis period, store in a list
        self.calculate_externalities()

    def calculate_externalities(self):
        for year in range(25):
            self.externalities.insert(year, decimal.Decimal(2.11))

    def initialize_measure(self):
        self.calculate_specs() 
    
    def calculate_specs(self):
        #get data from energy measure table of energy db
        try:
            cursor2 = conn.cursor('cursor_backup', cursor_factory=psycopg2.extras.DictCursor)
            cursor2.execute('SELECT * FROM energy_measure LIMIT 1000')
            for row in cursor2:
                if row[0] == self.name:
                    self.lifetime = 20
                    self.cost = row[4]
                    self.energy_conservation["electricity"] = row[6]
                    self.energy_conservation["diesel_oil"] = row[7]
                    self.energy_conservation["motor_gasoline"] = row[8]
                    self.energy_conservation["natural_gas"] = row[9]
                    self.energy_conservation["biomass"] = row[10]
                    #print(self.energy_conservation["electricity"])
                    #print(self.energy_conservation["diesel_oil"])
                    #print(self.energy_conservation["motor_gasoline"])
                    #print(self.energy_conservation["natural_gas"])
                    #print(self.energy_conservation["biomas"])
                    break
        except (Exception, psycopg2.Error) as error :
            print ("Error while connecting to PostgreSQL", error)
        finally:
            #closing database connection cursor.
            if(conn):
                cursor2.close()

    #and some methods to access objects of the class for general purpose 
    def get_cost(self):
       return self.cost
    
    def get_lifetime(self):
       return self.lifetime
    
    def get_externalities(self):
       return self.externalities
    
    def get_energy_conservation(self):
       return self.energy_conservation
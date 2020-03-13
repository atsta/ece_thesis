# db libs
import psycopg2
from psycopg2 import Error
import sys
import pprint
import psycopg2.extras

conn_string = "host='localhost' dbname='energy_db' user='athina' password='45452119'"
# get a connection with energy db
conn = psycopg2.connect(conn_string)


class Measure():
    """Class of Energy Measure.
    """
    def __init__(self, name, article):
        """
        Args:
            name (str): name of the examined measure.
            article (int): number of the article based on which the 
            energy conservation will be calculated. Possible values={3,7}.
        """
        self.name = name 
        self.article = article


        self.specs = {
            'name': "",
            'cost': 0.0,
            'lifetime': 0,
            'type': "",
            'category': ""
        }

        self.energy_conservation = {
        "electricity": 0.0,
        "diesel_oil": 0.0,
        "motor_gasoline": 0.0, 
        "natural_gas": 0.0, 
        "biomass": 0.0
        }

        self.energy_price_without_taxes = {
            "electricity": 0.0,
            "diesel_oil": 0.0,
            "motor_gasoline": 0.0, 
            "natural_gas": 0.0, 
            "biomass": 0.0
        }

        self.energy_price_with_taxes = {
            "electricity": 0.0,
            "diesel_oil": 0.0,
            "motor_gasoline": 0.0, 
            "natural_gas": 0.0, 
            "biomass": 0.0
        }

        self.energy_price_growth_rate = {
            "electricity": 0.0,
            "diesel_oil": 0.0,
            "motor_gasoline": 0.0, 
            "natural_gas": 0.0, 
            "biomass": 0.0
        }

        self.specs['name'] = self.name

        self.get_specs()
        self.get_conservation()
        self.get_prices()

    def get_specs(self):
        try: 
            cursor1 = conn.cursor('cursor_backup', cursor_factory=psycopg2.extras.DictCursor)
            cursor1.execute('SELECT * FROM app2_measure LIMIT 2000')
            for row in cursor1:
                if(row[0].strip() == self.name):
                    self.specs['cost'] = row[1]
                    self.specs['lifetime'] = row[2]
                    self.specs['type'] = row[5]
                    self.specs['category'] = row[4]
                    break

        except (Exception, psycopg2.Error) as error :
                    print ("Error while connecting to PostgreSQL", error)
        finally:
            #closing database connection cursor.
            if(conn):
                cursor1.close()

    def get_conservation(self):
        try: 
            cursor1 = conn.cursor('cursor_backup', cursor_factory=psycopg2.extras.DictCursor)
            cursor1.execute('SELECT * FROM app2_energy_conservation LIMIT 2000')
            for row in cursor1:
                if(row[0].strip() == self.name):
                    if self.article == 3:
                        self.energy_conservation['electricity'] = row[1]
                        self.energy_conservation['diesel_oil'] = row[2]
                        self.energy_conservation['motor_gasoline'] = row[3]
                        self.energy_conservation['natural_gas'] = row[4]
                        self.energy_conservation['biomass'] = row[5]
                    else: 
                        self.energy_conservation['electricity'] = row[6]
                        self.energy_conservation['diesel_oil'] = row[7]
                        self.energy_conservation['motor_gasoline'] = row[8]
                        self.energy_conservation['natural_gas'] = row[9]
                        self.energy_conservation['biomass'] = row[10]
                    break

        except (Exception, psycopg2.Error) as error :
                    print ("Error while connecting to PostgreSQL", error)
        finally:
            #closing database connection cursor.
            if(conn):
                cursor1.close()
    
    def get_prices(self):
        try: 
            cursor1 = conn.cursor('cursor_backup', cursor_factory=psycopg2.extras.DictCursor)
            cursor1.execute('SELECT * FROM energy_cost LIMIT 800')
            for row in cursor1:
                if self.specs["category"] == 'household':
                    if row[0].strip() == 'Biomass hh':
                        self.energy_price_with_taxes['biomass'] = row[1]
                        self.energy_price_without_taxes['biomass'] = row[2]
                        self.energy_price_growth_rate['biomass'] = row[3]
                    if row[0].strip() == 'Diesel oil hh':
                        self.energy_price_with_taxes['diesel_oil'] = row[1]
                        self.energy_price_without_taxes['diesel_oil'] = row[2]
                        self.energy_price_growth_rate['diesel_oil'] = row[3]
                    if row[0].strip() == 'Electricity hh':
                        self.energy_price_with_taxes['electricity'] = row[1]
                        self.energy_price_without_taxes['electricity'] = row[2]
                        self.energy_price_growth_rate['electricity'] = row[3]
                    if row[0].strip() == 'Natural gas hh':
                        self.energy_price_with_taxes['natural_gas'] = row[1]
                        self.energy_price_without_taxes['natural_gas'] = row[2]
                        self.energy_price_growth_rate['natural_gas'] = row[3]
                    if row[0].strip() == 'Motor Gasoline':
                        self.energy_price_with_taxes['motor_gasoline'] = row[1]
                        self.energy_price_without_taxes['motor_gasoline'] = row[2]
                        self.energy_price_growth_rate['motor_gasoline'] = row[3]
                elif "transport" in self.specs["category"]:
                    if row[0].strip() == 'Diesel oil transport':
                        self.energy_price_with_taxes['diesel_oil'] = row[1]
                        self.energy_price_without_taxes['diesel_oil'] = row[2]
                        self.energy_price_growth_rate['diesel_oil'] = row[3]
                    if row[0].strip() == 'Motor Gasoline':
                        self.energy_price_with_taxes['motor_gasoline'] = row[1]
                        self.energy_price_without_taxes['motor_gasoline'] = row[2]
                        self.energy_price_growth_rate['motor_gasoline'] = row[3]
                else: 
                    if row[0].strip() == 'Biomass hh':
                        self.energy_price_with_taxes['biomass'] = row[1]
                        self.energy_price_without_taxes['biomass'] = row[2]
                        self.energy_price_growth_rate['biomass'] = row[3]
                    if row[0].strip() == 'Diesel oil tertiary':
                        self.energy_price_with_taxes['diesel_oil'] = row[1]
                        self.energy_price_without_taxes['diesel_oil'] = row[2]
                        self.energy_price_growth_rate['diesel_oil'] = row[3]
                    if row[0].strip() == 'Electricity tertiary':
                        self.energy_price_with_taxes['electricity'] = row[1]
                        self.energy_price_without_taxes['electricity'] = row[2]
                        self.energy_price_growth_rate['electricity'] = row[3]
                    if row[0].strip() == 'Natural gas tertiary':
                        self.energy_price_with_taxes['natural_gas'] = row[1]
                        self.energy_price_without_taxes['natural_gas'] = row[2]
                        self.energy_price_growth_rate['natural_gas'] = row[3]
                    if row[0].strip() == 'Motor Gasoline':
                        self.energy_price_with_taxes['motor_gasoline'] = row[1]
                        self.energy_price_without_taxes['motor_gasoline'] = row[2]
                        self.energy_price_growth_rate['motor_gasoline'] = row[3]

        except (Exception, psycopg2.Error) as error :
                    print ("Error while connecting to PostgreSQL", error)
        finally:
            #closing database connection cursor.
            if(conn):
                cursor1.close()
    
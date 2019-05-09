import energy_measure
import social_investment_analysis
import financial_investment_analysis
import investment_analysis_perspective
from financial_mechanisms import loan
from actors import esco


import decimal 

def main():
    #select actors 
    #select measures 
    #check social 
    #check financial 
    #check esco 
    #check every other perspective
    #check for subsidy
    #return cost and whatever for each actor

    """
    analysis = input('Select analysis: ')
    input_measure = input('Select a measure: ')
    measure = energy_measure.Measure(input_measure)
    if analysis.strip() == 'Social':
        print("Social analysis for measure %s" % (input_measure))
        #print(measure.get_cost())
        scba = social_investment_analysis.Social(measure.get_cost(), measure.get_lifetime(), measure.get_externalities(), measure.get_energy_conservation())

    elif analysis.strip() == 'Financial': 
        print("Financial analysis for measure %s" % (input_measure))
        fcba = financial_investment_analysis.Financial(measure.get_cost(), measure.get_lifetime(), measure.get_externalities(), measure.get_energy_conservation())
        
    else: 
        analysis = input('Select analysis: ')
    """
    #analysis from business perspective
    #persp = investment_analysis_perspective.Perspective(measure.get_cost(), measure.get_lifetime(), measure.get_externalities(), measure.get_energy_conservation(), decimal.Decimal(0.1), decimal.Decimal(0.4))
    """
    externalities = []
    for i in range(0, 25):
        externalities.insert(i, 0)

    energy_conservation = {
            "electricity": 0,
            "diesel_oil": 42.0,
            "motor_gasoline": 0, 
            "natural_gas": 65.0, 
            "biomass": 0
        }

    persp = investment_analysis_perspective.Perspective(33800, 20, externalities, energy_conservation, decimal.Decimal(0.1), decimal.Decimal(0.4))
    """
    #check loan 
    #oroi_daneiou = loan.Terms(decimal.Decimal(0.5), 41912, decimal.Decimal(0.4))
    #epistrofi_daneiou = loan.Return()
   
    esco_loan = True
   
    fund_take_over_rate = float(input("Pososto analipsis kostous: "))
    #kostos esco = poso diamoirasmou*initial cost
    esco_cba = esco.Esco(fund_take_over_rate*41912, 8, 0.7, esco_loan)   


if __name__ == "__main__":
    main()
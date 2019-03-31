import energy_measure
import social_investment_analysis
import financial_investment_analysis
import investment_analysis_perspective

def main():
    analysis = input('Select analysis: ')
    input_measure = input('Select a measure: ')
    measure = energy_measure.Measure(input_measure)
    if analysis.strip() == 'Social':
        print("Social analysis for measure %s" % (input_measure))
        scba = social_investment_analysis.Social(measure.get_cost(), measure.get_lifetime(), measure.get_externalities(), measure.get_energy_conservation())

    elif analysis.strip() == 'Finacial': 
        print("Financial analysis for measure %s" % (input_measure))
        fcba = financial_investment_analysis.Financial(measure.get_cost(), measure.get_lifetime(), measure.get_externalities(), measure.get_energy_conservation())
        
    else: 
        analysis = input('Select analysis: ')
    
    #analysis from business perspective
    persp = investment_analysis_perspective.Perspective(measure.get_cost(), measure.get_lifetime(), measure.get_externalities(), measure.get_energy_conservation(), 0.1, 0.4)
        
   

if __name__ == "__main__":
    main()
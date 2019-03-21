import energy_measure

def main():
    input_measure = input('Select a measure: ')
    print("Analysis for measure %s" % (input_measure))
    measure = energy_measure.Measure(input_measure)

if __name__ == "__main__":
    main()
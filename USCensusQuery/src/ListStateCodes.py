import CensusDicts


if __name__ == '__main__':
    states = sorted(CensusDicts.us_state_codes.keys())
    for state in states:
        print('{}: {}'.format(state, CensusDicts.us_state_codes[state]))
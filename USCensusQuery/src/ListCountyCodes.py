import argparse

import Census
import CensusDicts
import Names


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('state_code', type=str,
                        help="The state code (note this is a string and may have a leading 0)")
    args = parser.parse_args()

    state_codes = CensusDicts.us_state_codes

    if args.state_code not in state_codes:
        print("Invalid state code (You can check code with ListStateCodes.py)")
        exit(1)

    census = Census.Census(Names.get_census_key())
    county_dict = census.get_county_dict(args.state_code)

    for code, county in sorted(county_dict.iteritems(), key=lambda (k, v): (v, k)):
        print(code + ': ' + county)


if __name__ == '__main__':
    main()

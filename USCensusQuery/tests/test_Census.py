import json
import unittest
import urllib2
from random import shuffle

from TestDicts import mecklenburg_county_codes
from context import src
from src import Census, GetDemographics
from src import Names
KEY = Names.get_census_key()

class Test_Census(unittest.TestCase):
    state_code = '37'
    county_code = '119'

    code_dict = {'B01001_001E': 'population',
                 'B06011_001E': 'median_income',
                 'B01001_002E': 'male_population',
                 'B01001_026E': 'female_population'}

    '''
    Randomized test to ensure that the Census API will return codes in the same order they were listed
    in the API call.
    '''

    def test_response_order(self):
        codes = Test_Census.code_dict.keys()
        shuffle(codes)

        code_string = ','.join(codes)
        url = 'https://api.census.gov/data/2013/acs5?get={}&for=county:119&in=state:37&key={}'.format(code_string, KEY)
        response = urllib2.urlopen(url)
        json_resp = json.load(response)
        result_codes = [item.encode('utf8') for item in json_resp[0]]
        self.assertEqual(codes + ['state', 'county'], result_codes)

    def test_census_single_tract(self):
        census = Census.Census(KEY)
        year = 2013
        dataset = 'acs5'
        result = census.get(Test_Census.code_dict, self.state_code, self.county_code, year, dataset)

        expected = {"000100":
            {
                'population': 3869,
                'median_income': 59102,
                'male_population': 2273,
                'female_population': 1596
            }
        }
        for tract in expected:
            self.assertDictEqual(expected[tract], result[tract])

    def test_census_single_tract_bg(self):
        census = Census.Census(KEY)
        year = 2013
        dataset = 'acs5'
        result = census.get(Test_Census.code_dict, self.state_code, self.county_code, year, dataset, bg=True)

        expected = {
            "000100.1":
                {
                    'population': 706,
                    'median_income': None,
                    'male_population': 491,
                    'female_population': 215
                },
            "000100.2":
                {
                    'population': 1311,
                    'median_income': None,
                    'male_population': 637,
                    'female_population': 674
                },
            "000100.3":
                {
                    'population': 708,
                    'median_income': None,
                    'male_population': 445,
                    'female_population': 263
                },
            "000100.4":
                {
                    'population': 313,
                    'median_income': None,
                    'male_population': 207,
                    'female_population': 106
                },
            "000100.5":
                {
                    'population': 831,
                    'median_income': None,
                    'male_population': 493,
                    'female_population': 338
                },
        }
        for bg in expected:
            self.assertDictEqual(expected[bg], result[bg])

    def test_census_multiple_tracts(self):
        census = Census.Census(KEY)
        year = 2013
        dataset = 'acs5'
        result = census.get(Test_Census.code_dict, self.state_code, self.county_code, year, dataset)

        expected = \
            {"000100":
                {
                    'population': 3869,
                    'median_income': 59102,
                    'male_population': 2273,
                    'female_population': 1596
                },
                "000300":
                    {
                        'population': 445,
                        'median_income': 35888,
                        'male_population': 188,
                        'female_population': 257
                    },
                "000400":
                    {
                        'population': 2089,
                        'median_income': 55231,
                        'male_population': 1307,
                        'female_population': 782
                    }
            }
        for tract in expected:
            self.assertDictEqual(expected[tract], result[tract])

    def test_census_multiple_bg(self):
        census = Census.Census(KEY)
        tracts = ['000400', '000600', '000700']
        shuffle(tracts)
        year = 2013
        dataset = 'acs5'
        result = census.get(Test_Census.code_dict, self.state_code, self.county_code, year, dataset, bg=True)

        expected = {
            "000400.1":
                {
                    'population': 1111,
                    'median_income': None,
                    'male_population': 723,
                    'female_population': 388
                },
            "000400.2":
                {
                    'population': 978,
                    'median_income': None,
                    'male_population': 584,
                    'female_population': 394
                },
            "000600.1":
                {
                    'population': 921,
                    'median_income': None,
                    'male_population': 399,
                    'female_population': 522
                },
            "000600.2":
                {
                    'population': 1665,
                    'median_income': None,
                    'male_population': 798,
                    'female_population': 867
                },
            "000700.1":
                {
                    'population': 770,
                    'median_income': None,
                    'male_population': 329,
                    'female_population': 441
                },
        }
        for bg in expected:
            self.assertDictEqual(expected[bg], result[bg])

    def test_census_all_tracts_in_dict(self):
        census = Census.Census(KEY)
        # Mecklenburg County, NC
        year = 2013
        dataset = 'acs5'
        result = census.get(Test_Census.code_dict, self.state_code, self.county_code, year, dataset)
        self.assertEqual(len(result), 233)

    def test_census_all_bgs_in_dict(self):
        census = Census.Census(KEY)
        # Mecklenburg County, NC
        year = 2013
        dataset = 'acs5'
        result = census.get(Test_Census.code_dict, self.state_code, self.county_code, year, dataset, bg=True)
        self.assertEqual(len(result), 555)

    def test_get_county_dict(self):
        state_code = '37'
        census = Census.Census(KEY)
        result = census.get_county_dict(state_code)
        self.assertDictEqual(result, mecklenburg_county_codes)


if __name__ == '__main__':
    unittest.main()
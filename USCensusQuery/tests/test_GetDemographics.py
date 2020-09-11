import json
import random
import unittest
import urllib2
from itertools import izip
from os.path import dirname

from context import src
from src import Census
from src import CensusDicts
from src import CodeDicts
from src import GetDemographics
from src import Names

KEY = Names.get_census_key()
cur_path = dirname(__file__)


class TestCodeLabels(unittest.TestCase):
    code_dict1 = {'B01001_001E': 'pop',
                  'B06011_001E': 'medinc',
                  'B01001_002E': 'mpop',
                  'B01001_026E': 'fpop'}

    # Note, we no longer use these codes in the actual app, but they still serve to demonstrate that
    # dictionary values are correct.
    code_dict2 = {'B25034_004E': 'b1990',
                  'B25034_009E': 'b1940',
                  'B25034_010E': 'b1930',
                  'B25034_005E': 'b1980'}

    combined_dict = {}
    combined_dict.update(code_dict1)
    combined_dict.update(code_dict2)

    def test_get_data_tract(self):
        state_code = '37'
        county_code = '119'
        year = '2013'
        data = GetDemographics.get_demographic_set(TestCodeLabels.code_dict1, year, state_code, county_code)
        self.assertEqual(len(data), 233)  # 233 tracts in Mecklenburg, NC
        self.assertEqual(len(data['001702']), 4)  # 4 demographics

        # each year in each tract should have the exact list of labels from the code dictionary
        for tract in data:
            expected = sorted(TestCodeLabels.code_dict1.values())
            result = sorted(data[tract].keys())
            self.assertListEqual(expected, result)

    def test_get_data_bg(self):
        state_code = '37'
        county_code = '119'
        years = '2013'
        data = GetDemographics.get_demographic_set(TestCodeLabels.code_dict1, years, state_code, county_code, bg=True)
        self.assertEqual(len(data), 555)  # 555 block groups in Mecklenburg, NC

        # each tract should have the exact list of labels from the code dictionary
        for tract in data:
            expected = sorted(TestCodeLabels.code_dict1.values())
            result = sorted(data[tract].keys())
            self.assertListEqual(expected, result)

    def test_get_all_data_tract(self):
        state_code = '37'
        county_code = '119'
        year = '2013'
        code_dicts = {'t1': TestCodeLabels.code_dict1, 't2': TestCodeLabels.code_dict2}
        all_labels = [label for nst in code_dicts.itervalues() for label in nst.itervalues()]
        all_data = GetDemographics.get_all_demographics(code_dicts, year, state_code, county_code)
        self.assertEqual(len(all_data), 233)  # still 233 tracts
        for dct in all_data.itervalues():
            self.assertEqual(len(dct), 8)  # 4 demographics in each dictionary

        # each year in each tract should have the exact list of labels from the code dictionary
        for tract in all_data:
            self.assertSetEqual(set(all_labels), set(all_data[tract].keys()))

    def test_get_all_data_bg(self):
        state_code = '37'
        county_code = '119'
        year = '2013'
        code_dicts = {'t1': TestCodeLabels.code_dict1, 't2': TestCodeLabels.code_dict2}
        all_labels = [label for nst in code_dicts.itervalues() for label in nst.itervalues()]
        all_data = GetDemographics.get_all_demographics(code_dicts, year, state_code, county_code, bg=True)
        self.assertEqual(len(all_data), 555)  # 555 block groups
        for dct in all_data.itervalues():
            self.assertEqual(len(dct), 8)  # 4 demographics in each dictionary

        # each tract should have the exact list of labels from the code dictionary
        for tract in all_data:
            self.assertSetEqual(set(all_labels), set(all_data[tract].keys()))


class TestDataCorrectness(unittest.TestCase):

    def test_dataframe_tract(self):
        state_code = '37'
        county_code = '119'
        rand_year = random.randint(2010, 2016)
        bg = False
        new_df = GetDemographics.create_demographic_df(state_code, county_code, rand_year, bg=bg)

        # Another check to make sure the same values are returned from a new API call
        dataset = 'acs5' if int(rand_year) < 2016 else 'acs/acs5'
        rand_rec = new_df.sample(n=1, axis=0)
        rand_tract = rand_rec['TRACTCE'].values[0].replace('"', '')  # Strip quotes
        label_dct = CodeDicts.get_flattened_label_dict()
        labels, codes = label_dct.keys(), label_dct.values()

        codes_str = ','.join(codes)
        url = 'https://api.census.gov/data/{}/{}?get={}&for=tract:{}&in=state:{}%20county:{}&key={}' \
            .format(rand_year, dataset, codes_str, rand_tract, state_code, county_code, KEY)
        response = ''
        try:
            response = urllib2.urlopen(url)
        except urllib2.HTTPError as e:
            print('Census API call failed because: ')
            print(e.reason)
            print(e.read())
        data = json.load(response)[1]

        for label, val in izip(labels, data):
            exp_val = new_df.loc[new_df['TRACTCE'] == '"' + rand_tract + '"', label].values[0]
            val = int(val) if val else 0
            self.assertEquals(exp_val, val)

    def test_dataframe_bg(self):
        state_code = '37'
        county_code = '119'
        rand_year = random.randint(2010, 2016)
        bg = True
        new_df = GetDemographics.create_demographic_df(state_code, county_code, rand_year, bg=bg)

        # Another check to make sure the same values are returned from a new API call
        dataset = 'acs5' if int(rand_year) < 2016 else 'acs/acs5'
        rand_rec = new_df.sample(n=1, axis=0)
        rand_tract = rand_rec[Names.SF_CENSUS_COL_TRACT].values[0].replace('"', '')  # Strip quotes
        rand_bg = rand_rec[Names.SF_CENSUS_COL_BG].values[0].replace('"', '')  # Strip quotes
        label_dct = CodeDicts.get_flattened_label_dict()
        labels, codes = label_dct.keys(), label_dct.values()

        codes_str = ','.join(codes)
        url = 'https://api.census.gov/data/{}/{}?get={}&for=block%20group:{}&in=state:{}%20county:{}%20tract:{}&key={}' \
            .format(rand_year, dataset, codes_str, rand_bg, state_code, county_code, rand_tract, KEY)
        response = ''
        try:
            response = urllib2.urlopen(url)
        except urllib2.HTTPError as e:
            print('Census API call failed because: ')
            print(e.reason)
            print(e.read())
            raise e

        try:
            data = json.load(response)[1]
        except ValueError as e:
            print "URL failed: " + url
            raise e

        for label, val in izip(labels, data):
            exp_val = new_df.loc[(new_df[Names.SF_CENSUS_COL_TRACT] == '"' + rand_tract + '"')
                                 & (new_df[Names.SF_CENSUS_COL_BG] == '"' + rand_bg + '"'), label] \
                .values[0]
            val = int(val) if val else 0
            self.assertEquals(exp_val, val)

    def test_random_area(self):
        bg = random.choice([True, False])
        rand_state = random.choice(CensusDicts.us_state_codes.keys())
        census = Census.Census(KEY)
        county_code_dict = census.get_county_dict(rand_state)
        rand_county = random.choice(county_code_dict.keys())
        years = [str(i) for i in range(2010, 2017)]
        rand_year = random.choice(years)

        rand_gdf = GetDemographics.create_demographic_df(state_code=rand_state, county_code=rand_county, year=rand_year,
                                                         bg=bg)
        rand_rec = rand_gdf.sample(n=1, axis=0)
        rand_tract = rand_rec[Names.SF_CENSUS_COL_TRACT].values[0].replace('"', '')
        rand_bg = rand_rec[Names.SF_CENSUS_COL_BG].values[0].replace('"', '') if bg else None

        dataset = 'acs5' if int(rand_year) < 2016 else 'acs/acs5'

        # Get parallel lists of codes and their labels
        codes, labels = zip(*[(k, v) for k, v in CodeDicts.get_flattened_code_dict().iteritems()])

        codes_str = ','.join(codes)

        level_str = 'block%20group' if bg else 'tract'
        # Example call:
        # https://api.census.gov/data/2013/acs5?get=NAME,B01001_001E&for=block%20group:0&in=state:06%20county:061%20tract:990000&key=YOUR_KEY_GOES_HERE
        if bg:
            url = 'https://api.census.gov/data/{}/{}?get={}&for={}:{}&in=state:{}%20county:{}%20tract:{}&key={}' \
                .format(rand_year, dataset, codes_str, level_str, rand_bg, rand_state, rand_county, rand_tract, KEY)

        else:
            url = 'https://api.census.gov/data/{}/{}?get={}&for={}:{}&in=state:{}%20county:{}&key={}' \
                .format(rand_year, dataset, codes_str, level_str, rand_tract, rand_state, rand_county, KEY)
        try:
            response = urllib2.urlopen(url)
        except urllib2.HTTPError as e:
            print('Census API call failed because: ')
            print(e.reason)
            print(e.read())
            raise e
        try:
            data = json.load(response)[1]
        except ValueError as e:
            print("Failed to load JSON.")
            print("State: ".format(rand_state))
            print("County: ".format(rand_county))
            print("Tract: ".format(rand_tract))
            if bg:
                print("Block group: ".format(rand_bg))
            print("Year: ".format(rand_year))


        # data is an array returned by the Census API
        # label is a parallel array that describes the value in data array
        for label, val in izip(labels, data):
            exp_val = rand_gdf.loc[(rand_gdf[Names.SF_CENSUS_COL_TRACT] == '"' + rand_tract + '"')
                                   & (rand_gdf[Names.SF_CENSUS_COL_BG] == '"' + rand_bg + '"'), label].values[0] \
                if bg else rand_gdf.loc[rand_gdf[Names.SF_CENSUS_COL_TRACT] == '"' + rand_tract + '"', label].values[0]
            val = int(val) if val else 0
            self.assertEquals(exp_val, val)


if __name__ == '__main__':
    unittest.main()
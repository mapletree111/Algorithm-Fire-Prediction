from os.path import join

SF_TYPE_COUNT = 'CountSF'
SF_TYPE_CENSUS = 'CensusSF'
SF_TYPE_DEMOGRAPHIC = 'DemographicSF'
SF_TYPE_TAZ = 'TazSF'
SF_TYPE_ZONING = 'ZoningSF'

MATFolder = 'MATFiles'
MATFilename = "SuperMAT_Clipped.xlsx"

ZoningFilename = 'Zoning_Merged_Clipped.shp'

SF_ZONE_COL = 'Zone'

SF_CENSUS_COL_TRACT = 'TRACTCE'
SF_CENSUS_COL_COUNTY = 'COUNTYFP'
SF_CENSUS_COL_BG = 'BLKGRPCE'
SF_CENSUS_COL_LAT = 'INTPTLAT'
SF_CENSUS_COL_LONG = 'INTPTLON'

SF_TAZ_COL_TRACT = 'TRACT10'
SF_TAZ_COL_BG = 'TRCTBLKGRP'
SF_TAZ_COL_TAZ = 'TAZ'
SF_TAZ_COL_LAT = 'CENTLAT'
SF_TAZ_COL_LONG = 'CENTLONG'

INC_LOG_LAT_LABEL = 'Latitude'
INC_LOG_LONG_LABEL = 'Longitude'
INC_LOG_NATURE_LABEL = 'Cause2_TGK'
INC_LOG_DATE_LABEL = 'DispatchDate'

SF_INTERSECT = 'intersect'
SF_CLIP = 'clip'

# Proportion of shape left in shapefile
SF_PROP = 'prop'

from Census import Census
from CensusDicts import us_state_codes


def get_census_key():
    key_path = join('..', 'key_file')
    with open(key_path, 'r') as keyfile:
        key = keyfile.readline().rstrip()
    return key


def get_location(state_code, county_code):
    census = Census(get_census_key())
    state = us_state_codes[state_code]
    county = census.get_county_dict(state_code)[county_code]
    return county, state


def get_censusSF(state_code, level):
    n = 'tl_2017_{}_{}'.format(state_code, level)
    return join('..', SF_TYPE_CENSUS, n, n + '.shp')

def get_census_test_sf():
    return join('TestCensus', 'TestCensus.shp')

def get_folder(state_code, county_code, year, sf_type):
    county, state = get_location(county_code, state_code)
    return join('..', sf_type, state, county, year)


def get_inc_log_folder(state_code, city_name):
    state = us_state_codes[state_code]
    pth = join('..', 'IncData', state, city_name, 'Yearly')
    return pth


def gen_demographic_file_name(state_code, county_code, level):
    return "{}_{}_demographics_{}".format(state_code, county_code, level)


def get_response_zone_shapefile(state_code, city_name):
    return join('..', 'ResponseSF', us_state_codes[state_code], city_name, 'Response Zones.shp')


def get_taz_shapefile(state_code, county_code, year):
    county, state = get_location(state_code=state_code, county_code=county_code)
    return join('..', 'TazSF', state, county, year, 'TazPopStreetMetrics2.shp')


def get_zoning_shapefile(state_code, county_code, year):
    county, state = get_location(state_code=state_code, county_code=county_code)
    return join('..', SF_TYPE_ZONING, state, county, year, ZoningFilename)


def get_super_mat(state_code, city_name):
    state = us_state_codes[state_code]
    return join('..', MATFolder, state, city_name, MATFilename)


def get_test_super_mat():
    return join('TestSuperMAT', 'TestSuperMAT.xlsx')


def get_test_super_mat_taz():
    return join('TestSuperMAT', 'test_taz_clip.shp')


def get_test_zone():
    return join('TestZoning', 'zonetest.shp')


def get_test_zone_census():
    return join('TestZoning', 'census_test.shp')


def quote_column(df, column):
    df[column] = df[column].astype(int).astype(str).apply('"{}"'.format)
    return df

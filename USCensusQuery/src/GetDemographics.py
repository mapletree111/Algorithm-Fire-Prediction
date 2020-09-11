import geopandas as gpd
import pandas as pd

import CodeDicts
import Names
from Census import Census


def get_demographic_set(code_dict, year, state_code, county_code, bg=False):
    """
    Creates a Census object and calls its get method with the appropriate
    code_dict.
    Assembles the data into mapped_data, which is a nested dictionary in the form:

    :param code_dict: The dictionary relating labels to Census codes
    :param year: The year of demographics to retrieve
    :param state_code: Census state code
    :param county_code: Census county code
    :param bg: True if data at block group level, False if tract level
    :return: A dictionary in the form:

    {tract:
        {label:
        }
    }
    """
    key = Names.get_census_key()
    census = Census(key)
    dataset = 'acs/acs5' if int(year) >= 2016 else 'acs5'
    data = census.get(code_dict, state_code, county_code, year, dataset, bg)

    return data


def get_all_demographics(all_code_dicts, year, state_code, county_code, bg=False):
    """
    :param all_code_dicts: A dict of {code:label} dictionaries
    :param year: The year of demographics to retrieve
    :param state_code: Census state code
    :param county_code: Census county code
    :param bg: True if data at block group level, False if tract level
    :return: A dict of dictionaries of all tracts with all demographics for each tract in the form:
    {tract:
        {demogrpahic_label:
        }
    }
    """

    # Keep track of number of API calls for front-end messages
    curr = 1
    total = len(all_code_dicts)

    # Store all returned dictionaries in a list
    all_data = []
    for dct in all_code_dicts:
        print("Obtaining data set {}/{}...".format(curr, total))
        data = get_demographic_set(all_code_dicts[dct], year, state_code, county_code, bg)
        curr += 1
        all_data.append(data)
    dct = {}

    # Consolidate all demographics from list into one dictionary
    for d in all_data:
        for tract, d2 in d.iteritems():
            if tract not in dct:
                dct[tract] = {}
            for label, value in d2.iteritems():
                dct[tract][label] = value
    return dct


def create_demographic_df(state_code, county_code, year, bg=False):
    """
    :param state_code: Census state code
    :param county_code: Census county code
    :param year: The year of demographics to retrieve
    :param bg: True if data at block group level, False if tract level
    :return: A GeoDataFrame that includes Census demographics
    """
    all_code_dicts = CodeDicts.get_all_code_dicts()
    demographics = get_all_demographics(all_code_dicts, year, state_code, county_code, bg=bg)
    level = 'bg' if bg else 'tract'
    census_sf = Names.get_censusSF(state_code, level)

    # Create dataframe froom Census state shapefile
    geo_df = gpd.read_file(census_sf)
    new_idx_col = Names.SF_CENSUS_COL_BG if bg else Names.SF_CENSUS_COL_TRACT

    # Only consider the subset of records for given county
    geo_df = geo_df.loc[geo_df[Names.SF_CENSUS_COL_COUNTY] == county_code]

    # Put dictionary of demographics in its own dataframe, then merge them on tract
    dem_df = pd.DataFrame.from_dict(demographics, orient='index')
    if bg:
        # First need to put index (tract.bg) into a non-index column
        dem_df['combined'] = dem_df.index
        # Split the tract and block group and put them into their own columns.
        dem_df = dem_df.join(dem_df['combined'].str.split('.', 1, expand=True).rename(
            columns={0: Names.SF_CENSUS_COL_TRACT, 1: Names.SF_CENSUS_COL_BG}))
        merge_cols = [Names.SF_CENSUS_COL_TRACT, Names.SF_CENSUS_COL_BG]
        combined_gdf = geo_df.merge(right=dem_df, how='inner', left_on=merge_cols, right_on=merge_cols)
        combined_gdf = Names.quote_column(combined_gdf, Names.SF_CENSUS_COL_BG)
    else:
        combined_gdf = geo_df.merge(right=dem_df, how='inner', left_on=new_idx_col, right_index=True)

    # Need this to maintain leading 0's when we write to a csv file
    combined_gdf[Names.SF_CENSUS_COL_TRACT] = combined_gdf[Names.SF_CENSUS_COL_TRACT].apply('"{}"'.format)

    # Set tract as index for the dataframe
    combined_gdf.set_index(new_idx_col, drop=False, inplace=True)
    combined_gdf.fillna(0, inplace=True)

    return combined_gdf

import CodeDicts
import Names
from TazCodeList import taz_to_sum, taz_to_avg, taz_no_mod


def get_interp_lat_long(taz_gdf, lat_col_name, long_col_name):
    """
    TAZ shapefiles do not have a lat/long centroid, but we need this for
    GWR.
    :param taz_gdf: GeoDataFrame of TAZ shapefile
    :param lat_col_name: Name of the latitude column
    :param long_col_name: Name of the longitude column
    :return: The TAZ gdf with two new columns, giving the lat/long of the centroid
    """
    taz_gdf['centroid'] = taz_gdf.centroid
    taz_gdf[long_col_name] = taz_gdf.centroid.apply(func=lambda pt: pt.x)
    taz_gdf[lat_col_name] = taz_gdf.centroid.apply(func=lambda pt: pt.y)
    return taz_gdf


def merge_taz_to_census(census_gdf, taz_gdf, census_level_lbl, taz_level_lbl):
    """
    Reaggregate TAZ data into Census shapes.
    :param census_gdf: Census GeoDataFrame
    :param taz_gdf: TAZ GeoDataFrame
    :param census_level_lbl: Name of the column indicating a unique label for each Census shape
    :param taz_level_lbl: Name of the column indicating a unique label for each TAZ
    :return: A gdf with TAZ data reaggregated into Census shapes (tract or block groups)
    """

    # Get a dataframe with a subset of the taz columns
    print ("Merging TAZ and Census data")
    sub_df_cols = ['TAZ', taz_level_lbl] + taz_to_sum + taz_to_avg + taz_no_mod
    sub_gdf = taz_gdf.reindex(columns=sub_df_cols)
    # Group by TAZ and sum values in each unique TAZ
    sub_gdf_by_census_shp = sub_gdf.groupby(taz_level_lbl)[taz_to_sum].sum().reset_index()

    # The tract in the taz file includes state and county code before the tract
    # Strip the state/county prefix and add quotes (to prevent removal of any leading 0s)
    sub_gdf_by_census_shp.loc[:, taz_level_lbl] = \
        sub_gdf_by_census_shp.loc[:, taz_level_lbl].apply(func=lambda x: '"' + x[5:] + '"')

    # Left join because Census has already been processed and is more likely to exclude
    # useless shapes.
    combined_gdf = census_gdf.merge(right=sub_gdf_by_census_shp, how='left', left_on=census_level_lbl,
                                    right_on=taz_level_lbl)
    return combined_gdf


def merge_census_to_taz(census_gdf, taz_gdf, census_level_lbl, taz_level_lbl):
    """
    Reaggregate Census data into TAZ shapes.
    :param census_gdf: Census GeoDataFrame
    :param taz_gdf: TAZ GeoDataFrame
    :param census_level_lbl: Name of the column indicating a unique label for each Census shape
    :param taz_level_lbl: Name of the column indicating a unique label for each TAZ
    :return: A gdf with Census data reaggregated into TAZ shapes
    """
    print ("Merging TAZ and Census data")
    # TAZ does not have lat/long of centroids. Add this info for GWR analysis.
    lat_col_name = Names.SF_TAZ_COL_LAT
    long_col_name = Names.SF_TAZ_COL_LONG
    taz_gdf = get_interp_lat_long(taz_gdf, lat_col_name=lat_col_name, long_col_name=long_col_name)

    # Get a dataframe with a subset of the taz columns
    sub_df_cols = ['TAZ', taz_level_lbl, lat_col_name, long_col_name] + taz_to_sum + taz_to_avg + taz_no_mod
    geo_col = taz_gdf.loc[:, 'geometry']
    sub_gdf = taz_gdf.reindex(columns=sub_df_cols)

    # The 'tract' column in the taz file includes state and county code before the tract
    # NOTE: A TAZ can be made up of different census shapes.
    # In Charlotte, NC, TAZs are subdivisions of block groups.
    # However, this may not be the case in other cities.
    sub_gdf.loc[:, taz_level_lbl] = \
        sub_gdf.loc[:, taz_level_lbl].apply(func=lambda x: '"' + x[5:] + '"')

    # Left join because Census is more likely to exclude useless shapes.
    combined_gdf = sub_gdf.merge(right=census_gdf, how='left', left_on=taz_level_lbl,
                                 right_on=census_level_lbl)
    combined_gdf.loc[:, 'geometry'] = geo_col

    # -------  Divide population by number of TAZ within tracts
    # NOTE: It might be better to assign populations as a proportion of area, but neither will be perfect

    # Get all census population labels in the TAZ
    census_pop_labels = CodeDicts.get_pop_labels()
    census_pop_labels = filter(lambda x: x in combined_gdf.columns.values, census_pop_labels)

    # Count the number of TAZ to divide by
    combined_gdf['numblks'] = combined_gdf[taz_level_lbl].groupby(combined_gdf[taz_level_lbl]).transform('count')

    # Divide each column of Census population by the number of TAZ within the Census shape
    combined_gdf.loc[:, census_pop_labels] = \
        combined_gdf.loc[:, census_pop_labels].divide(combined_gdf.loc[:, 'numblks'], axis='rows')
    combined_gdf.drop(columns='numblks', inplace=True)
    combined_gdf = Names.quote_column(combined_gdf, Names.SF_TAZ_COL_TAZ)

    return combined_gdf

import geopandas as gpd

import Names


def find_taz_of_addr(base_gdf, mat_df):
    """
    Find the TAZ of each address within the Master Address Table
    :param base_gdf: The TAZ GDF
    :param mat_df: The master address table as a DataFrame
    :return: A GeoDataframe with each address merged with its associated TAZ
    """

    print "Merging address and shapefile data."
    mat_df['geometry'] = mat_df.apply(lambda x: gpd.geoseries.Point((float(x.longitude), float(x.latitude))), axis=1)
    mat_gdf = gpd.GeoDataFrame(mat_df, geometry='geometry')
    mat_gdf.crs = base_gdf.crs
    merged = gpd.sjoin(mat_gdf, base_gdf, how='inner', op='within')
    merged.drop(['geometry'], axis=1, inplace=True)
    merged = Names.quote_column(df=merged, column=Names.SF_TAZ_COL_TAZ)
    return merged

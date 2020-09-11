from __future__ import division


def get_densities(gdf, target_columns, area_column, drop=False):
    """
    Returns a GeoDataFrame with densities given by each target_column divided by the designated area_column.
    :param gdf: A GeoDataFrame
    :param target_columns: A list of columns for which to find densities
    :param drop: True if the columns used for feature extraction should be dropped after calculations.
    Defaults to False
    :return: GeoDataFrame Population / Unit of area
    """
    for col_label in target_columns:
        new_label = col_label[:9] + '%'
        gdf[new_label] = gdf[col_label] / gdf[area_column]

    if drop:
        gdf.drop(columns=target_columns, inplace=True)

    return gdf

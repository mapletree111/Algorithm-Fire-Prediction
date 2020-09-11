from __future__ import division

import pandas as pd

import Names


def append_zone_proportions(base_gdf, zone_gdf, base_shp_col):
    """
    Add columns indentifying the proportion of each zone in zone_gdf contained in each base shape.

    :param base_gdf: The GeoDataFrame containing the data and shapes of interest
    :param zone_gdf: The GeoDataFrame containing the zoning data
    :param base_shp_col: The base_gdf's column name that identifies unique shapes (e.g "TAZ", "TRACTCE")
    :return: A GeoDataFrame with zone proportion columns appended
    """
    print('Finding zone proportions of each {}. This will take several minutes...'.format(base_shp_col))
    zone_type_col = Names.SF_ZONE_COL
    zone_areas = {}
    for _, base_rec in base_gdf.iterrows():
        curr_shape = base_rec[base_shp_col]
        zone_areas[curr_shape] = {}
        base_shp = base_rec.geometry
        for _, z_rec in zone_gdf.iterrows():
            z_shp = z_rec.geometry
            z_type = z_rec[zone_type_col]
            if not z_shp.is_valid:
                # This 'cleans' the geometry if it is invalid (intersects itself)
                z_shp = z_shp.buffer(0)
            if base_shp.intersects(z_shp):
                inter = z_shp.intersection(base_shp)
                inter_area = inter.area
                base_shp_area = base_shp.area
                if z_type not in zone_areas[curr_shape]:
                    zone_areas[curr_shape][z_type] = inter_area / base_shp_area
                else:
                    zone_areas[curr_shape][z_type] += inter_area / base_shp_area

    zone_df = pd.DataFrame.from_dict(zone_areas, orient='index')
    zone_df.fillna(0, inplace=True)  # Fill non-represented zone areas with 0
    # prepend a Z_ to zone columns
    zone_df.rename({old: 'Z_' + old for old in zone_df.columns.values.tolist()})

    base_gdf = base_gdf.merge(zone_df, left_on=[base_shp_col], right_index=True)

    return base_gdf

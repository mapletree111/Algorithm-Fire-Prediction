from __future__ import division

from os.path import isfile

import geopandas as gpd

import Names


def intersect_shapefile_helper(base_gdf, resp_area_gdf):
    """
    Helper function for intersect_shapefile
    :param base_gdf: The GeoDataFrame containing the data
    :param resp_area_gdf: The GeoDataFrame containing the response area
    :return: A GeoDataFrame containing data only for shapes that intersect the response area.
    """
    result = []
    for _, base_rec in base_gdf.iterrows():
        for _, resp_rec in resp_area_gdf.iterrows():
            resp_shp = resp_rec.geometry
            if base_rec.geometry.intersects(resp_shp):
                result.append(base_rec)
    result = gpd.GeoDataFrame(result)
    result.crs = base_gdf.crs
    return result


def intersect_shapefile(base_gdf, resp_area_fpath):
    """
    Intersect the shapes of a GeoDataFrame with a response area
    :param base_gdf: The GeoDataFrame containing the data
    :param resp_area_fpath: The path to a shapefile of the response area
    :return: A GeoDataFrame containing data only for shapes that intersect the response area.
    """
    if not isfile(resp_area_fpath):
        print "No response area shapefile at " + resp_area_fpath
        print 'Exiting...'
        exit(1)

    resp_area_sf = gpd.read_file(resp_area_fpath)
    return intersect_shapefile_helper(base_gdf, resp_area_sf)


def clip_shapefile_helper(base_gdf, resp_area_gdf, pop_columns):
    """
    Helper function for clip_shapefile()
    :param base_gdf: The GeoDataFrame containing the data
    :param resp_area_gdf: The GeoDataFrame containing the response area
    :return: A GeoDataFrame containing data for shapes clipped against the response area.
    """
    resp_area_gdf.crs = base_gdf.crs
    result = []  # Result holds an array of records that will become the new GeoDataFrame
    for _, base_rec in base_gdf.iterrows():
        for _, resp_rec in resp_area_gdf.iterrows():
            resp_shp = resp_rec.geometry

            if not resp_shp.is_valid:
                # This 'cleans' the geometry if it is invalid (intersects itself)
                resp_shp = resp_shp.buffer(0)

            if base_rec.geometry.contains(resp_shp) or base_rec.geometry.within(resp_shp):
                base_rec[Names.SF_PROP] = 1
                result.append(base_rec)

            # Note: This can almost certainly be optimized by getting all proportions,
            # eliminating all shapes with 0%, then multiplying by proportion column-wise
            elif base_rec.geometry.intersects(resp_shp):
                new_rec = base_rec
                new_geo = base_rec.geometry.intersection(resp_shp)
                proportion = new_geo.area / base_rec.geometry.area
                if proportion > 0:
                    new_rec[Names.SF_PROP] = proportion
                    for column in pop_columns:
                        if column in new_rec:
                            new_rec[column] = float(new_rec[column]) * proportion
                    new_rec.geometry = new_geo
                    result.append(new_rec)

    result = gpd.GeoDataFrame(result)
    result.crs = base_gdf.crs

    return result


def clip_shapefile(base_gdf, resp_area_fpath, pop_columns):
    """
    Clips a GeoDataFrame against a response area.
    Performs areal interpolation by multiplying population features by the
    proportion of area left in shapes.

    NOTE: All data should be added to shapefile before clipping to ensure proper
    areal interpolation.

    :param base_gdf: The GeoDataFrame containing the data
    :param resp_area_fpath: The path to the response area shapefile
    :return: A GeoDataFrame containing data for shapes clipped against the response area.
    """

    print "Clipping shapefile"
    if not isfile(resp_area_fpath):
        print "No response area shapefile at " + resp_area_fpath
        print 'Exiting...'
        exit(1)

    resp_area_gdf = gpd.read_file(resp_area_fpath)
    return clip_shapefile_helper(base_gdf, resp_area_gdf, pop_columns)

from itertools import izip
from os import listdir
from os.path import isdir
from os.path import join
from time import time

import geopandas as gpd
import pandas as pd

import Names

LAT_LABEL = Names.INC_LOG_LAT_LABEL
LONG_LABEL = Names.INC_LOG_LONG_LABEL
NATURE_LABEL = Names.INC_LOG_NATURE_LABEL
DATE_LABEL = Names.INC_LOG_DATE_LABEL

'''
Generate a dictionary mapping points (as a tuple) to the incident type.

Params: 
    inc_file: path to csv file with one year's worth of incident data. 

Returns:
    A tuple of parallel lists:
    pts =        [pt0,   pt1,   pt2, ...]
    call_types = [type0, type1, type2, ...]
'''


def get_call_data(inc_file):
    """
    :param inc_file: Path to csv file with one year's worth of incident data.
    :return: A tuple of parallel lists:
            pts =        [pt0,   pt1,   pt2, ...]
            call_types = [type0, type1, type2, ...]
    """
    df = pd.read_csv(inc_file)

    # Get list of Points
    longs = df[LONG_LABEL].tolist()
    lats = df[LAT_LABEL].tolist()
    pts = [gpd.geoseries.Point(float(lng), float(lat)) for lng, lat in izip(longs, lats)]

    # Get list of nature codes
    call_types = df[NATURE_LABEL].fillna(value='none').tolist()  # If no incident type given

    return pts, call_types


def count_points_in_shapes(geo_df, base_shape, pts, inc_types):
    """
    Counts the number of points corresponding to incident types in a given shape.
    This currently counts the points contained in each polygon, which does not include points
    on the boundary of multiple polygons.

    IMPORTANT NOTE: If incidents occur on tract/bg boundaries, they will not be counted as contained within any
    geometry. The unused points will be shown in the program output.

    If we use gpd.geometry.contains(), points that are sufficiently close to boundaries will not get counted at all.
    See:
        - http://toblerity.org/shapely/manual.html#object.contains
        - http://toblerity.org/shapely/manual.html#object.intersects

    Interesting notes:
    - The results of contains() without replacement match the 'count points in polygons' feature of QGIS
    - The results of intersect with replacement results in close approximation to what the analogous feature
      in ArcGIS produces. Counts for each polygon are typically close, but appear to be always less than or equal
      to what ArcGIS produces.

    :param geo_df: Source GeoDataFrame
    :param base_shape: The column describing the shapes in which to count the points
    :param pts: A list of geopandas.geoseries.Points
    :param inc_types: a list of inc_types
        NOTE: pts and inc_types are parallel lists where the point at pts[n] corresponds
        to the inc_type in inc_types[n]
    :return: A dictionary in the form:
                {tract :
                    {inc_type: count} }
    """
    pts_df = gpd.GeoDataFrame({'inc_types': inc_types}, geometry=pts)
    pts_df.crs = geo_df.crs
    point_df = gpd.sjoin(geo_df, pts_df, how='inner', op='contains')

    # Todo: compare right join to see what calls weren't joined
    # cmp_df = gpd.sjoin(geo_df, pts_df, how='right', op='contains')
    # print geo_df.head()
    # count_df = geo_df.groupby([base_shape, 'inc_types'])[base_shape].count().reset_index(name="count").pivot(index=base_shape, columns='inc_types', values='count')
    # print geo_df.groupby([base_shape,'inc_types']).size().reset_index(name="count")

    count_df = pd.crosstab(point_df[base_shape], point_df['inc_types']).rename_axis(None,
                                                                                    axis=1).reset_index().set_index(
        base_shape)
    # Merge with left-join so shapes are kept even if no points occur in them
    # merged_gdf = geo_df.merge(right=count_df, how='left', left_on=base_shape,
    #                                right_on=base_shape)

    count_dict = count_df.to_dict(orient='index')

    return count_dict


def average_counts(count_dict, year, all_inc_types, num_yrs=5):
    """
    Averages the counts of incidents over num_yrs. Note default is 5 years, since we have been primarily using
    Census ACS 5 data.

    NOTE: this function modifies count_dict in place for memory efficiency

    :param count_dict: A dictionary in the form:
            { Tract:
             { Year:
               { IncidentType:
               }
             }
            }
    :param year: The year to average for
    :param all_inc_types: A set of all incident types present in records
    :param num_yrs: Number of prior years to average over
    :return: A dictionary of the same form as count_dict, but with all counts averaged over num_yrs
    """
    avg_dict = {}
    years = [str(i) for i in range(int(year) - 4, int(year) + 1)]
    for rec in count_dict:
        avg_dict[rec] = {}
        for yr in years:
            for inc_type in all_inc_types:
                avg_count = (count_dict[rec][yr][inc_type] / float(num_yrs)) \
                    if yr in count_dict[rec] and inc_type in count_dict[rec][yr] \
                    else 0
                if year not in avg_dict[rec]:
                    avg_dict[rec][year] = {}
                if inc_type not in avg_dict[rec][year]:
                    avg_dict[rec][year][inc_type] = avg_count
                else:
                    avg_dict[rec][year][inc_type] += avg_count
    return avg_dict


def get_all_counts(geo_df, base_shape, log_folder, years):
    """
    Obtains all incident counts from a folder of incident files (MS Excel format),
    and count all points in each of the shapes in the shapefile.
    :param geo_df: A GeoDataFrame
    :param base_shape: The column name of the shapes in which to count points
    :param log_folder: Folder in which incident logs are stored
    :param years: Years for which to collect incident data
    :return: A dictionary in the form:
            { RecordNumber:
                { Year:
                    { IncidentType:
                    }
                }
            }
    """
    years_left = set(years)
    all_counts = {}
    all_inc_types = set([])

    if years_left:
        yearly_inc_dict = {}
        for year in years_left:
            for f in listdir(log_folder):
                if str(year) in f and '.csv' in f:
                    if year in yearly_inc_dict:
                        print("Error: More than one inc file for {}".format(year))
                        print ("Exiting...")
                        exit(1)
                    yearly_inc_dict[year] = join(log_folder, f)

        invalid_years = []
        for year in years_left:
            if year not in yearly_inc_dict.keys():
                invalid_years.append(year)
        print invalid_years
        if invalid_years:
            print "Call logs for the following years not found: "
            print invalid_years
            print "Exiting..."
            exit(1)

        for year, inc_file in yearly_inc_dict.iteritems():
            pts, inc_types = get_call_data(inc_file)
            all_inc_types.update(inc_types)
            print "Getting incident data for {}".format(year)
            start_time = time()
            count_dict = count_points_in_shapes(geo_df=geo_df, base_shape=base_shape, pts=pts, inc_types=inc_types)
            print "Incident data for {} took {} seconds".format(year, time() - start_time)
            all_counts[year] = count_dict

    # Modify count dictionary to so it's keyed by record, rather than year
    all_counts_by_rec = {}
    for year in all_counts:
        for shp in all_counts[year]:
            if shp not in all_counts_by_rec.keys():
                all_counts_by_rec[shp] = {}
            if year not in all_counts_by_rec[shp].keys():
                all_counts_by_rec[shp][year] = {}
            all_counts_by_rec[shp][year].update(all_counts[year][shp])

    return all_counts_by_rec, all_inc_types


def generate_count_gdf(geo_df, base_shape, all_counts):
    """
    A helper function for generating count GeoDataFrame
    :param geo_df: A GeoDataFrame
    :param base_shape: The column name of the shapes in which to count points
    :param all_counts: A dictionary in the form:
     { RecordNumber:
                { Year:
                    { IncidentType:
                    }
                }
            }
    :return: A GeoDataFrame with all incident counts for the year.
    """

    # Take the year out of the nested dict
    all_counts = {k: v2 for k, v1 in all_counts.iteritems() for v1, v2 in all_counts[k].iteritems()}

    count_df = pd.DataFrame.from_dict(all_counts, orient='index')  # Create DataFrame of counts
    count_df.fillna(value=0, inplace=True)  # Replace NaN's with 0's
    count_df.sort_index(axis=1, inplace=True)  # Sort columns
    geo_df = geo_df.merge(right=count_df, how='left', left_on=base_shape, right_index=True)  # Join on tract
    geo_df.fillna(0, inplace=True)
    return geo_df


def get_count_gdf(geo_df, base_shape, state_code, city, year, avg=False):
    """
    Add incident count data to a GeoDataFrame.
    :param geo_df: The GeoDataFrame
    :param base_shape: The column name of the shape in which to count points.
    :param state_code: Census state code
    :param city: (String) City name (for finding incident logs)
    :param year: The year. If avg=True, this will be the last year over which to average
    :param avg: True if an average (past 5 years) is desired; False will return incident data
    for year specified in 'year' only.
    :return: A GeoDataFrame
    """
    inc_folder = Names.get_inc_log_folder(state_code, city)
    if not isdir(inc_folder):
        print 'Incident data not found at ' + inc_folder
        print 'Exiting...'
        exit(1)

    # Years is a list of the 5 years to average over, or the single year if avg is not indicated
    years = set([str(i) for i in range(int(year) - 4, int(year) + 1)] if avg else [str(year)])
    all_counts, all_inc_types = get_all_counts(geo_df=geo_df, base_shape=base_shape, log_folder=inc_folder, years=years)

    if avg:
        all_counts = average_counts(all_counts, year, all_inc_types)

    geo_df = generate_count_gdf(geo_df=geo_df, base_shape=base_shape, all_counts=all_counts)

    return geo_df

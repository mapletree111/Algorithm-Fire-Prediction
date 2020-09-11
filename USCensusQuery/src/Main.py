import argparse

import geopandas as gpd

import CodeDicts
import CombineFeatures
import ExtractFeatures
import GetDemographics
import GetIncidentCounts
import GetTazData
import GetTrimmedSF
import GetZoningData
import Names
import TazCodeList
import GetNeighborData

def get_taz_gdf(state_code, county_code, year):
    return gpd.read_file(Names.get_taz_shapefile(state_code=state_code, county_code=county_code, year=year))


def create_shapefile(state_code, county_code, year, avg=True, level='tract', zone=False, points=None, taz=True,
                     clip=None, intersect=None, nocheck=False, outname='out'):

    all_population_columns = []  # Keep a list of all population columns for areal interpolation

    bg = (level == 'bg')
    base_shape = Names.SF_CENSUS_COL_BG if bg else Names.SF_CENSUS_COL_TRACT

    if level != 'bg' and level != 'tract':
        print "Invalid Census level"
        exit(1)

    if avg and not points:
        print "Cannot average incidents without counting incidents!"
        exit(1)

    county, state = Names.get_location(state_code, county_code)
    msg = 'You have selected to create a shapefile for {}, {} for {} with the following properties:\n'. \
        format(county, state, year)
    msg += 'Demographics for {} in {}, {}\n'.format(level, county, state)
    if points:
        if avg:
            msg += "Averaged "
        else:
            msg += "Yearly "
        msg += "incident counts\n"
    if taz:
        msg += "Taz data\n"
    if clip:
        msg += "Clipped against {}'s response zone\n".format(clip)
    if intersect:
        msg += "Intersected against {}'s response zone\n".format(intersect)
    if zone:
        msg += "With zoning proportions of each shape\n"
    msg += "Saving as shapefile: {}".format(outname)
    r = ''
    print msg

    while not nocheck and r != 'y':
        r = raw_input("Is this correct? (y/n): ")
        if r == 'n':
            print "Exiting..."
            exit(1)

    gdf = GetDemographics.create_demographic_df(state_code=state_code, county_code=county_code, year=year, bg=bg)
    GetNeighborData.get_neighbor_data(census_gdf=gdf, target_columns=['bldavg', 'medinc'])
    all_population_columns.extend(CodeDicts.get_pop_labels())

    if taz:
        taz_gdf = get_taz_gdf(state_code, county_code, year)
        gdf = GetTazData.merge_census_to_taz(census_gdf=gdf, taz_gdf=taz_gdf, census_level_lbl=base_shape,
                                             taz_level_lbl=Names.SF_TAZ_COL_TRACT)

        base_shape = Names.SF_TAZ_COL_TAZ
        all_population_columns.extend(TazCodeList.taz_to_sum)

        # Get employment and population density
        density_cols = ['TPE_TOTEMP', 'TPE_POP']
        area_column = 'TPE_AREA_L'
        gdf = ExtractFeatures.get_densities(gdf=gdf, target_columns=density_cols, area_column=area_column,
                                            drop=False)

    # NOTE: population values are interpolated during clipping. Make sure all population features are added
    # before clipping!
    if clip:
        resp_area_fpath = Names.get_response_zone_shapefile(state_code, clip)
        gdf = GetTrimmedSF.clip_shapefile(gdf, resp_area_fpath, all_population_columns)

    if intersect:
        resp_area_fpath = Names.get_response_zone_shapefile(state_code, intersect)
        gdf = GetTrimmedSF.intersect_shapefile(gdf, resp_area_fpath)

    if points:
        gdf = GetIncidentCounts.get_count_gdf(geo_df=gdf, base_shape=base_shape, state_code=state_code, city=points,
                                              year=year, avg=False)

    if zone:
        zone_gdf = gpd.read_file(Names.get_zoning_shapefile(state_code=state_code, county_code=county_code, year=year))
        gdf = GetZoningData.append_zone_proportions(base_gdf=gdf, zone_gdf=zone_gdf, base_shp_col=base_shape)

        zones_to_combine = \
            {
                'RESIDENTIAL': ['SINGLE FAMILY', 'MULTI-FAMILY'],
                'COMMERCIAL': ['OFFICE', 'BUSINESS', 'MIXED USE']
            }

        gdf = CombineFeatures.sum_features(gdf, zones_to_combine)

    print("Creating shapefile as {}".format(outname))
    gdf.to_file(outname, driver='ESRI Shapefile')
    gdf.drop(['geometry'], axis=1, inplace=True)
    gdf.to_csv(outname + '.csv')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('state_code', type=str,
                        help="The state code (note this is a string and may have a leading 0)")
    parser.add_argument('county_code', type=str,
                        help="The county code (note this is a string and may have a leading 0)")
    parser.add_argument('year', type=str,
                        help="Specify year of data to collect")
    parser.add_argument("-n", "--nocheck", action="store_true",
                        help="Do not ask for confirmation before generating shapefile")
    parser.add_argument("-o", "--output", type=str,
                        help="Specify name of output shapefile (Defaults to 'out')")
    parser.add_argument("-p", "--points", type=str,
                        help="Count incidents from city (response zone) in IncData folder")
    parser.add_argument("-a", "--average", action="store_true",
                        help="Average incident counts over 5 years")
    parser.add_argument("-t", "--taz", action="store_true",
                        help="Combine data from TAZ shapefile")
    parser.add_argument("-z", "--zone", action="store_true",
                        help="Add dominant zone feature")
    parser.add_argument('-l', '--level', type=str,
                        help="Define Census level: 'bg' for block groups, 'tract' for tracts. Defaults to tract.")
    trim_type = parser.add_mutually_exclusive_group(required=False)
    trim_type.add_argument("-c", "--clip", type=str,
                           help="Create a clip against the specified city (response zone)")
    trim_type.add_argument("-i", "--intersect", type=str,
                           help="Create an intersection against the specified city (response zone)")

    args = parser.parse_args()

    county_code = args.county_code
    state_code = args.state_code
    year = args.year
    points = args.points
    avg = args.average
    zone = args.zone
    level = args.level if args.level else 'tract'
    clip = args.clip
    intersect = args.intersect
    nocheck = args.nocheck
    outname = 'out' if not args.output else args.output
    taz = args.taz

    # ---------------- Helpful for testing: ----------------
    # county_code = '119'
    # state_code = '37'
    # year = '2015'
    # points = True
    # avg = True
    # level = 'tract'
    # clip = 'Charlotte'
    # intersect = None
    # check = False
    # outname= '37_119_2015_avg'
    # taz = False

    create_shapefile(state_code=state_code, county_code=county_code, year=year, avg=avg, level=level, points=points,
                     taz=taz,
                     zone=zone, clip=clip, intersect=intersect, nocheck=nocheck, outname=outname)


if __name__ == '__main__':
    main()

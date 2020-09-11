import numpy as np
import pandas as pd
from sklearn.neighbors import NearestNeighbors

import Names


def get_tract_neighbors(gdf, num_neighbors):
    latlongs = gdf[[Names.SF_CENSUS_COL_TRACT, Names.SF_CENSUS_COL_LAT, Names.SF_CENSUS_COL_LONG]] \
        .reset_index(drop=True).set_index(Names.SF_CENSUS_COL_TRACT)

    neighbors = NearestNeighbors(n_neighbors=num_neighbors,
                                 algorithm='ball_tree', metric='haversine').fit(latlongs)

    k_nbrs = neighbors.kneighbors(latlongs, num_neighbors, return_distance=False)
    neighbor_cols = ['n' + str(i) for i in range(num_neighbors)]
    neighbors_df = pd.DataFrame(k_nbrs, index=latlongs.index, columns=neighbor_cols)

    # The closest neighbor ('n0') to a tract is the tract itself.
    # We use it here to map the index of the df (0, 1, 2, ...) to the actual tract numbers
    shape_index_map = neighbors_df['n0'].to_dict()
    shape_index_map = {v: k for k, v in shape_index_map.iteritems()}
    neighbors_df[neighbor_cols] = neighbors_df[neighbor_cols].applymap(lambda x: shape_index_map[x])

    neighbors_df.drop(['n0'], axis=1, inplace=True)

    return neighbors_df


def get_neighbor_data_helper(census_gdf, neighbor_df, target_col):
    # Add a column to indicate whether this value is interpolated
    intpt_col = "Itpt_" + target_col
    # Fiona does not allow shapefiles to have bool columns
    census_gdf[intpt_col] = ((census_gdf['totpop'] != 0) & (census_gdf[target_col] == 0)).astype(int)

    while True:
        # Get the shapes that have nonzero populations and zero target values (e.g. median income, avg building age)

        # Must check conditions on each loop because values will be added
        nonzero_pops = census_gdf[(census_gdf['totpop'] != 0)]
        shapes_to_fix = nonzero_pops[nonzero_pops[target_col] == 0]

        # Exit loop if there are no more cells to
        if shapes_to_fix.empty:
            break

        # Get the df of neighbors of the shapes to fix
        to_fix_nbr_df = neighbor_df.loc[shapes_to_fix['TRACTCE']]

        # Create a dictionary that maps a tract dict of its neighbors
        to_fix_nbr_dict = to_fix_nbr_df.to_dict(orient='index')


        # Convert the dictionary to map a tract to a list of neighboring tracts
        # in ascending order of distance
        to_fix_nbr_dict = {k: [v2 for _, v2 in sorted(v.iteritems(), key=lambda (k, v): (k, v))]
                           for k, v in to_fix_nbr_dict.iteritems()}



        for tract in to_fix_nbr_dict:
            nearest = []
            for neighbor in to_fix_nbr_dict[tract]:
                # Get the value of the neighbor's target column
                nearest.append(census_gdf.loc[census_gdf['TRACTCE'] == neighbor][target_col].iat[0])
            # Take the three nearest with nonzero values
            nearest = [n for n in nearest if n > 0][:3]
            census_gdf.at[census_gdf['TRACTCE'] == tract, target_col] = np.average(nearest) if len(nearest) > 0 else 0


def get_neighbor_data(census_gdf, target_columns):
    neighbor_df = get_tract_neighbors(census_gdf, num_neighbors=5)
    for c in target_columns:
        get_neighbor_data_helper(census_gdf, neighbor_df, target_col=c)


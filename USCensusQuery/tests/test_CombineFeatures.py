import unittest
from os.path import dirname

import geopandas as gpd
import pandas as pd

from context import src
from src import CombineFeatures
from src import GetZoningData
from src import Names

KEY = Names.get_census_key()
cur_path = dirname(__file__)


class TestSumColumns(unittest.TestCase):
    def test1(self):
        LABELS = [str(i) for i in range(4)]
        A = [1, 2, 3, 4]
        B = [3, 4, 5, 6]
        C = [8, 9, 10, 11]
        D = [12, 13, 14, 15]
        E = [16, 17, 18, 19]

        df = pd.DataFrame({'LABELS': LABELS, 'A': A, 'B': B, 'C': C, 'D': D, 'E': E})
        new_cols = {'F': ['A', 'B'], 'G': ['C', 'D', 'E']}

        df = CombineFeatures.sum_features(df, new_cols)
        expected_F = [a + b for a, b in zip(A, B)]
        expected_G = [c + d + e for c, d, e in zip(C, D, E)]

        # Make sure values summed correctly
        self.assertListEqual(expected_F, df['F'].tolist())
        self.assertListEqual(expected_G, df['G'].tolist())

        # Make sure old columns are dropped
        self.assertSetEqual(set(['LABELS', 'F', 'G']), set(df.columns.values.tolist()))

    def test_integrated(self):

        # TODO: test zone has different zone labels from one we're using now!!

        zones_to_combine = \
            {
                'RESIDENTIAL': ['SINGLE FAMILY', 'MULTI-FAMILY'],
                'COMMERCIAL': ['OFFICE', 'BUSINESS', 'MIXED USE'],
                'TRANSIT': ['TRANSIT-ORIENTED', 'TRANSIT ORIENTED']
            }
        census_gdf = gpd.read_file(Names.get_test_zone_census())
        zoning_gdf = gpd.read_file(Names.get_test_zone())
        base_shp_col = Names.SF_CENSUS_COL_TRACT
        combined_gdf = GetZoningData.append_zone_proportions(base_gdf=census_gdf, zone_gdf=zoning_gdf, base_shp_col=base_shp_col)

        combined_gdf = CombineFeatures.sum_features(combined_gdf, zones_to_combine)


if __name__ == '__main__':
    unittest.main()
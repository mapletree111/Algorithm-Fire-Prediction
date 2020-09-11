import unittest
import pandas as pd
import geopandas as gpd

from context import src
from src import GetSuperMAT
from src import Names


class TestGetSuperMat(unittest.TestCase):
    def test_integrated(self):

        mat_df = pd.read_excel(Names.get_test_super_mat())
        base_gdf = gpd.read_file(Names.get_test_super_mat_taz())

        new_mat_df = GetSuperMAT.find_taz_of_addr(base_gdf=base_gdf, mat_df=mat_df)

        exp_addrs = {
        # Out of response zone:
        # u'509 CLAIRVIEW LN':  '"11088"',
        # u'100 3RD ST': '"10996"',
        # u'100 ABINGDON CR': '"10988"',
        # u'100 ALDEN LN': '"10989"',

        u'8901 WALDEN RIDGE DR': '"10951"',
        # Very close lat/long
        u'1244 W Morehead St': '"10041"',
        u'1240 W Morehead St': '"10041"',
        # Same lat/long
        u'5124 N Sharon Amity Rd': '"10482"',
        u'5200 N Sharon Amity Rd': '"10482"'
        }

        res_addrs = {row['address']: row['TAZ'] for _, row in new_mat_df.iterrows()}

        self.assertDictEqual(exp_addrs, res_addrs)


if __name__ == '__main__':
    unittest.main()
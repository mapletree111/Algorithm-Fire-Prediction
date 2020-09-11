import unittest
from os.path import join

import geopandas as gpd

from context import src
from src import GetTazData
from src import Names

test_files_path = join('TestShpFile', 'TazTest')


class Test_Combine_Taz(unittest.TestCase):

    # TODO: Figure out how to get quotes around tract consistently
    def test_add_taz_to_tract(self):
        census_file = join(test_files_path, 'census_test.shp')
        taz_file = join(test_files_path, 'taz_test.shp')
        census_gdf = gpd.read_file(census_file)
        taz_gdf = gpd.read_file(taz_file)

        census_tlbl = 'TRACTCE'
        taz_tlbl = 'TRACT10'

        combined_gdf = GetTazData.merge_taz_to_census(census_gdf=census_gdf, taz_gdf=taz_gdf,
                                                      census_level_lbl=census_tlbl, taz_level_lbl=taz_tlbl)
        combined_gdf = combined_gdf.set_index(census_tlbl)

        # Should return 3 tracts
        self.assertEquals(combined_gdf.shape[0], 3)

        self.assertEquals(combined_gdf.loc['"000100"', 'TPE_POP'], 6572)
        self.assertEquals(combined_gdf.loc['"000300"', 'TPE_POP'], 407)
        self.assertEquals(combined_gdf.loc['"000400"', 'TPE_POP'], 4480)

        self.assertEquals(combined_gdf.loc['"000100"', 'pov'], 378)
        self.assertEquals(combined_gdf.loc['"000300"', 'pov'], 144)
        self.assertEquals(combined_gdf.loc['"000400"', 'pov'], 374)

    def test_add_tract_to_taz(self):
        census_file = join(test_files_path, 'census_test.shp')
        taz_file = join(test_files_path, 'taz_test.shp')
        census_gdf = gpd.read_file(census_file)
        taz_gdf = gpd.read_file(taz_file)

        census_tlbl = 'TRACTCE'
        taz_tlbl = 'TRACT10'

        combined_gdf = GetTazData.merge_census_to_taz(census_gdf=census_gdf, taz_gdf=taz_gdf,
                                                      census_level_lbl=census_tlbl, taz_level_lbl=taz_tlbl)
        combined_gdf = combined_gdf.set_index(census_tlbl)

        # Check that all 'TPE_POP' values are the same for each taz zone
        self.assertListEqual(combined_gdf.loc[:, 'TPE_POP'].tolist(), taz_gdf.loc[:, 'TPE_POP'].tolist())

        print combined_gdf
        print census_gdf
        # Check that the demographic population is divided among blocks column from
        for i in range(14):
            self.assertEquals(combined_gdf.loc['"000100"', 'pov'][i], 378.0 / 14)
        for i in range(3):
            self.assertEquals(combined_gdf.loc['"000300"', 'pov'][i], 144.0 / 3)
        for i in range(4):
            self.assertEquals(combined_gdf.loc['"000400"', 'pov'][i], 374.0 / 4)

        # Check that the demographic population is divided among blocks column from
        for i in range(14):
            self.assertEquals(combined_gdf.loc['"000100"', 'bldavg'][i], 2002)
        for i in range(3):
            self.assertEquals(combined_gdf.loc['"000300"', 'bldavg'][i], 1994)
        for i in range(4):
            self.assertEquals(combined_gdf.loc['"000400"', 'bldavg'][i], 2004)


if __name__ == '__main__':
    unittest.main()
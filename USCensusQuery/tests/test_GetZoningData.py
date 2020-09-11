import unittest
from os.path import join

import geopandas as gpd

from context import src
from src import GetZoningData
from src import Names

test_files_path = join('TestShpFile', 'TazTest')


class TestGetZoningData(unittest.TestCase):
    def test_integrated(self):
        census_gdf = gpd.read_file(Names.get_test_zone_census())
        zoning_gdf = gpd.read_file(Names.get_test_zone())
        base_shp_col = Names.SF_CENSUS_COL_TRACT
        combined_gdf = GetZoningData.append_zone_proportions(base_gdf=census_gdf, zone_gdf=zoning_gdf, base_shp_col=base_shp_col)

        # Make sure all zones from zoning file are in combined_gdf
        all_zones = zoning_gdf['Zone'].unique().tolist()
        self.assertTrue(set(all_zones).issubset(set(combined_gdf.columns.values.tolist())))

        max_zones = {
            '"000100"': 'UPTOWN MIXED USE',
            # Tract 000300 is close. Confirmed "BUSINESS" occupies largest total area in QGIS/Excel
            '"000300"': 'BUSINESS',
            '"000400"': 'HEAVY INDUSTRIAL'
        }

        for _, rec in combined_gdf.iterrows():
            base_shape = rec[base_shp_col]
            zone_srs = rec[all_zones].astype('float64')
            # Make sure maximum zones remain correct
            self.assertEqual(max_zones[base_shape], zone_srs.idxmax())
            # Make sure proportions add up to close to 1
            self.assertAlmostEqual(zone_srs.sum(), 1, places=1)


if __name__ == '__main__':
    unittest.main()
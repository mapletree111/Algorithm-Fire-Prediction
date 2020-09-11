from __future__ import division

import unittest
from os.path import join

import geopandas as gpd

from context import src
from src import ExtractFeatures


class TestGetPopulationDensity(unittest.TestCase):
    test_files_path = join('TestShpFile', 'TazTest')
    taz_file = join(test_files_path, 'taz_test.shp')

    def test_pop_density_no_drop(self):
        taz_gdf = gpd.read_file(self.taz_file)
        pop_columns = ['TPE_TOTEMP', 'TPE_POP']
        area_column = 'TPE_AREA_L'
        taz_gdf = ExtractFeatures.get_densities(taz_gdf, pop_columns, area_column, drop=False)

        for _, rec in taz_gdf.iterrows():
            for col in pop_columns:
                mod_col = col[:9] + '%'
                self.assertAlmostEqual(rec[col] / rec[area_column], rec[mod_col])

    def test_pop_density_drop(self):
        taz_gdf = gpd.read_file(self.taz_file)
        pop_columns = ['TPE_TOTEMP', 'TPE_POP']
        area_column = 'TPE_AREA_L'
        taz_gdf = ExtractFeatures.get_densities(taz_gdf, pop_columns, area_column, drop=True)
        new_cols = [x[:9] + '%' for x in pop_columns]

        # Area and density columns in final gdf
        self.assertTrue(set(new_cols + [area_column]).issubset(set(taz_gdf.columns.values.tolist())))
        # Initial population columns not in final gdf
        self.assertFalse(set(pop_columns).issubset(set(taz_gdf.columns.values.tolist())))


if __name__ == '__main__':
    unittest.main()
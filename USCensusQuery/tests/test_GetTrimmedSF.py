import unittest
from os.path import join

import geopandas as gpd
from shapely.geometry import Polygon


from context import src
from src import GetTrimmedSF

test_files_path = join('TestShpFile', 'TazTest')


class Test_Get_Trimmed_SF(unittest.TestCase):
    base_p0 = Polygon([(3, 1), (3, 2), (4, 2), (4, 1)])
    base_p1 = Polygon([(1, 1), (1, 3), (3, 3), (3, 1)])
    base_p2 = Polygon([(3, 2), (3, 4), (5, 4), (5, 2)])
    base_p3 = Polygon([(1, 3), (1, 4), (2, 4), (2, 3)])
    base_p4 = Polygon([(1, 6), (1, 8), (4, 8), (4, 6)])

    clip_p1 = Polygon([(2, 1), (2, 3), (4, 3), (4, 1)])
    base_srs = gpd.GeoSeries([base_p0, base_p1, base_p2, base_p3, base_p4])
    clip_srs = gpd.GeoSeries([clip_p1])

    pop_columns = {'total_pop': [300, 2000, 1000, 500, 20], 'pov': [30, 200, 100, 50, 1]}
    np_columns = {'bldavg': [1944, 1999, 2009, 1968, 1992], 'medinc': [21000, 28000, 31000, 24000, 15000]}
    all_cols = {}
    all_cols.update(pop_columns)
    all_cols.update(np_columns)
    all_cols.update({'geometry': base_srs})
    base_gdf = gpd.GeoDataFrame(all_cols)

    clip_gdf = gpd.GeoDataFrame({'geometry': clip_srs})

    def test_clip(self):
        clipped_gdf = GetTrimmedSF.clip_shapefile_helper(base_gdf=self.base_gdf, resp_area_gdf=self.clip_gdf,
                                                         pop_columns=self.pop_columns.keys())

        # Non-population values should not be altered
        # p3, p4 will not be in the end result
        self.assertListEqual(clipped_gdf.medinc.tolist(), self.all_cols['medinc'][:-2])
        self.assertListEqual(clipped_gdf.bldavg.tolist(), self.all_cols['bldavg'][:-2])

        for x in self.pop_columns:
            self.assertEqual(clipped_gdf[x][0], self.all_cols[x][0])
            self.assertEqual(clipped_gdf[x][2], self.all_cols[x][2] / 4)
            self.assertEqual(clipped_gdf[x][2], self.all_cols[x][2] / 4)

    def test_intersect(self):
        intersected_gdf = GetTrimmedSF.intersect_shapefile_helper(base_gdf=self.base_gdf, resp_area_gdf=self.clip_gdf)

        # No values should not be altered
        # p4 will not be in the end result
        for x in self.all_cols:
            if x != 'geometry':
                self.assertListEqual(intersected_gdf[x].tolist(), self.all_cols[x][:-1])


if __name__ == '__main__':
    unittest.main()
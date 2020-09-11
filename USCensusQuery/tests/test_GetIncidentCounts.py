import unittest
from itertools import izip
from os.path import join

import geopandas as gpd

from context import src
from src import GetIncidentCounts


class TestGetIncidentCounts(unittest.TestCase):
    test_2006_fp = join('TestIncFiles', 'test_2006.csv')

    def test_get_call_data(self):
        pts, call_types = GetIncidentCounts.get_call_data(self.test_2006_fp)

        exp_pts = [
            (-80.93953700, 35.23977900),
            (-80.88772400, 35.21648000),
            (-80.90232300, 35.27923800),
            (-80.86900700, 35.20734900),
            (-80.91755900, 35.20787200),
        ]

        exp_calls = [
            u'611 Dispatched & canceled en route',
            u'321 EMS call, excluding vehicle accident with inju',
            u'531 Smoke or odor removal',
            u'321 EMS call, excluding vehicle accident with inju',
            u'321 EMS call, excluding vehicle accident with inju'
        ]
        pts = [(pt.x, pt.y) for pt in pts]
        for pt, exp_pt in izip(pts, exp_pts):
            self.assertAlmostEqual(pt[0], exp_pt[0], delta=0.0000001)
            self.assertAlmostEqual(pt[1], exp_pt[1], delta=0.0000001)

        self.assertListEqual(call_types, exp_calls)


class TestAverageCounts(unittest.TestCase):
    def test_avg_counts1(self):
        count_dict = \
            {0: {'2016':
                {
                    315: 5,
                    316: 35,
                    317: 65
                },
                '2015':
                    {
                        315: 10,
                        316: 40,
                        317: 70
                    },
                '2014':
                    {
                        315: 15,
                        316: 45,
                        317: 75
                    },
                '2013':
                    {
                        315: 20,
                        316: 50,
                        317: 80
                    },
                '2012':
                    {
                        315: 25,
                        316: 55,
                        317: 85,
                        318: 5
                    },
            }
            }

        year = '2016'
        all_inc_types = {315, 316, 317, 318}
        avg_counts = GetIncidentCounts.average_counts(count_dict, year, all_inc_types)
        exp_dict = \
            {0:
                {'2016':
                    {
                        315: 15,
                        316: 45,
                        317: 75,
                        318: 1
                    }
                }
            }
        self.assertDictEqual(avg_counts, exp_dict)


class TestDataFrame(unittest.TestCase):
    def test_generated_df_integrated(self):
        test_file = join('TestShpFile', 'MecklenburgCounty_NC_tract', 'MecklenburgCounty_NC_tract.shp')
        dem_gdf = gpd.read_file(test_file)
        exp_rec_nums_2006 = [207, 99, 44, 41, 35]
        exp_inc_types_2006 = ['611 Dispatched & canceled en route',
                              '321 EMS call, excluding vehicle accident with inju',
                              '531 Smoke or odor removal',
                              '321 EMS call, excluding vehicle accident with inju',
                              '321 EMS call, excluding vehicle accident with inju'
                              ]

        years = ['2006']
        base_shape = 'TRACTCE'
        all_counts, all_inc_types = GetIncidentCounts.get_all_counts(geo_df=dem_gdf, base_shape=base_shape,
                                                                     log_folder='TestIncFiles', years=years)
        geo_df = GetIncidentCounts.generate_count_gdf(geo_df=dem_gdf, base_shape=base_shape, all_counts=all_counts)

        self.assertSetEqual(all_inc_types, set(exp_inc_types_2006))
        for rn, it in izip(exp_rec_nums_2006, exp_inc_types_2006):
            val = geo_df.loc[rn, it]
            self.assertEqual(val, 1)


if __name__ == '__main__':
    unittest.main()
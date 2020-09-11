import unittest

import geopandas as gpd

from src import GetNeighborData
from src import Names


class TestGetNeighborData(unittest.TestCase):
    def test_get_call_data(self):
        gdf = gpd.read_file(Names.get_census_test_sf())

        GetNeighborData.get_neighbor_data(gdf, ['bldavg', 'medinc'])

        gdf.to_file('test_out')

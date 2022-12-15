import sys
import pytest
import unittest
from unittest.mock import Mock
from devtools_testutils import AzureTestCase
from azure.core.credentials import AzureKeyCredential
from azure.maps.search.models import StructuredAddress
from azure.maps.search import MapsSearchClient
from azure.maps.search._shared import converter

# cSpell:disable
class AzureMapsSearchClientUnitTest(AzureTestCase):

    def test_fuzzy_search_invalid_top(self):
        client = MapsSearchClient(
            credential=Mock(AzureKeyCredential)
        )
        with pytest.raises(TypeError):
            client.search_point_of_interest_category(StructuredAddress())

    def test_search_structured_address(self):
        client = MapsSearchClient(
            credential=Mock(AzureKeyCredential)
        )
        with pytest.raises(TypeError):
             client.search_structured_address(StructuredAddress())

class TestConverter(unittest.TestCase):

    def test_geo_interface_to_geojson(self):
        data_input= {
            'type': 'Polygon',
            'coordinates': ((
                (-122.43576049804686, 37.7524152343544),
                (-122.43301391601562, 37.70660472542312),
                (-122.36434936523438, 37.712059855877314),
                (-122.43576049804686, 37.7524152343544)
            ),)}

        data_output = {
            'type': 'Polygon',
            'coordinates': [[
                [-122.43576049804686, 37.7524152343544],
                [-122.43301391601562, 37.70660472542312],
                [-122.36434936523438, 37.712059855877314],
                [-122.43576049804686, 37.7524152343544]]
            ]}

        g_json = converter.geo_interface_to_geojson(data_input)
        self.assertEqual(g_json, data_output)

    def test_wkt_to_geo_interface(self):
        data_input= 'POLYGON ((30 10, 40 40, 20 40, 10 20, 30 10))'

        data_output = {
            'type': 'Polygon',
            'coordinates': [[
                (30, 10), (40, 40), (20, 40), (10, 20), (30, 10)
            ]]}

        g_interface = converter.wkt_to_geo_interface(data_input)
        self.assertEqual(g_interface, data_output)

    def test_wkt_to_geojson(self):
        data_input= 'POLYGON ((30 10, 40 40, 20 40, 10 20, 30 10))'

        data_output = {
            'type': 'Polygon',
            'coordinates': [[
                [30, 10], [40, 40], [20, 40], [10, 20], [30, 10]
            ]]}

        g_json = converter.wkt_to_geojson(data_input)
        self.assertEqual(g_json, data_output)

    def test_parse_geometry_input_with_geo_json_obj(self):
        data_input= {
        'type': 'Polygon',
        'coordinates': [[
            [-122.43576049804686, 37.7524152343544],
            [-122.43301391601562, 37.70660472542312],
            [-122.36434936523438, 37.712059855877314],
            [-122.43576049804686, 37.7524152343544]
        ]]}

        data_output = {'geometry': {'type': 'Polygon',
            'coordinates': [[
                [-122.43576049804686, 37.7524152343544],
                [-122.43301391601562, 37.70660472542312],
                [-122.36434936523438, 37.712059855877314],
                [-122.43576049804686, 37.7524152343544]
            ]]}}

        g_obj = converter.parse_geometry_input(data_input)
        self.assertEqual(g_obj, data_output)

if __name__ == "__main__" :
    testArgs = [ "-v" , "-s" ] if len(sys.argv) == 1 else sys.argv[1:]
    #testArgs = [ "-s" , "-n" , "auto" , "--dist=loadscope" ] if len(sys.argv) == 1 else sys.argv[1:]
    #pytest-xdist: -n auto --dist=loadscope
    #pytest-parallel: --tests-per-worker auto
    #print( "testArgs={}".format(testArgs) )

    pytest.main(args=testArgs)

    print("main() Leave")
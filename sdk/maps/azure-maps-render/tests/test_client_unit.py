import sys
import pytest
from unittest.mock import Mock
from devtools_testutils import AzureTestCase
from azure.core.credentials import AzureKeyCredential
from azure.maps.render import MapsRenderClient
from azure.maps.render.models import LatLon, TilesetID, BoundingBox


# cSpell:disable
def create_mock_client():
    return MapsRenderClient(
        credential=Mock(AzureKeyCredential)
    )

class AzureMapsRenderClientUnitTest(AzureTestCase):

    def test_get_map_tile_invalid_index_y(self):
        client = create_mock_client()
        with pytest.raises(TypeError):
            client.get_map_tile(
                tileset_id=TilesetID.MICROSOFT_BASE,
                tile_index_z=6,
                tile_index_x=9,
                tile_index_y="two",
                tile_size="512"
            )

    def test_get_map_tileset_invalid_tileset_id(self):
        client = create_mock_client()
        with pytest.raises(TypeError):
            client.get_map_tileset()

    def test_get_map_attribution_invalid_zoom(self):
        client = create_mock_client()
        with pytest.raises(TypeError):
            client.get_map_attribution(
                tileset_id=TilesetID.MICROSOFT_BASE,
                zoom="six",
                bounds=BoundingBox(bottom_left=(LatLon(42.982261, 24.980233)), top_right=(LatLon(56.526017, 1.355233)))
            )

    def test_get_copyright_from_bounding_box_invalid_LatLon(self):
        client = create_mock_client()
        with pytest.raises(TypeError):
            client.get_copyright_from_bounding_box(
                bounding_box=BoundingBox(bottom_left=LatLon("random"), top_right=LatLon(52.41072,4.84239))
            )

    def test_get_copyright_for_tile_invalid_index_x(self):
        client = create_mock_client()
        with pytest.raises(TypeError):
            client.get_copyright_for_tile(
                tile_index_z=6,
                tile_index_x="nine",
                tile_index_y="two"
            )

if __name__ == "__main__" :
    testArgs = [ "-v" , "-s" ] if len(sys.argv) == 1 else sys.argv[1:]
    #testArgs = [ "-s" , "-n" , "auto" , "--dist=loadscope" ] if len(sys.argv) == 1 else sys.argv[1:]
    #pytest-xdist: -n auto --dist=loadscope
    #pytest-parallel: --tests-per-worker auto
    #print( "testArgs={}".format(testArgs) )

    pytest.main(args=testArgs)

    print("main() Leave")
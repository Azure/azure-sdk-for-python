import sys
import pytest
try:
    from unittest.mock import Mock
except ImportError:  # python < 3.3
    from mock import Mock  # type: ignore

from devtools_testutils import AzureTestCase
from azure.core.pipeline.transport import HttpTransport, HttpResponse
from azure.core.credentials import AzureKeyCredential
from azure.maps.render import MapsRenderClient
from azure.maps.render.models import LatLon, TilesetID, BoundingBox


# cSpell:disable
class MockTransport(HttpTransport):
    def __init__(self, status_code, body, **kwargs):
        self.status_code = status_code
        self.body = body.encode("utf-8-sig") if body != None else None
        self.kwargs = kwargs
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
    def close(self):
        pass
    def open(self):
        pass
    def send(self, request, **kwargs):  # type: (PipelineRequest, Any) -> PipelineResponse
        response = HttpResponse(request, None)
        response.status_code = self.status_code
        response.headers["content-type"] = "application/json"
        response.body = lambda: self.body
        for key, val in self.kwargs.items():
            setattr(response, key, val)
        return response

def create_mock_client(status_code=0, body=None, **kwargs):
    return MapsRenderClient(credential= Mock(AzureKeyCredential),
                        transport=MockTransport(status_code, body, **kwargs))

class AzureMapsRenderClientUnitTest(AzureTestCase):
    def __init__(self, *args, **kwargs):
        super(AzureMapsRenderClientUnitTest, self).__init__(*args, **kwargs)

    def setUp(self):
        super(AzureMapsRenderClientUnitTest, self).setUp()

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
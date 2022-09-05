import sys
import pytest

from devtools_testutils import AzureTestCase
from azure_devtools.scenario_tests import RecordingProcessor
from azure.core.credentials import AzureKeyCredential
from azure.maps.render import MapsRenderClient
from azure.maps.render.models import TilesetID, BoundingBox


# cSpell:disable
class HeaderReplacer(RecordingProcessor):
    def __init__(self):
        self.headers = []

    def register_header(self, header_name, new_val):
        self.headers.append((header_name, new_val))

    def process_request(self, request):
        for header_name, new_val in self.headers:
            for key in request.headers.keys():
                if key.lower() == header_name.lower():
                    request.headers[key] = new_val
                    break
        return request


# cSpell:disable
class AzureMapsRenderClientE2ETest(AzureTestCase):
    def __init__(self, *args, **kwargs):
        super(AzureMapsRenderClientE2ETest, self).__init__(*args, **kwargs)
        header_replacer = HeaderReplacer()
        header_replacer.register_header("subscription-key", "<RealSubscriptionKey>")
        header_replacer.register_header("x-ms-client-id", "<RealClientId>")
        self.recording_processors.append(header_replacer)

    def setUp(self):
        super(AzureMapsRenderClientE2ETest, self).setUp()
        self.client = MapsRenderClient(
            client_id=self.get_settings_value('CLIENT_ID'),
            credential=AzureKeyCredential(self.get_settings_value('SUBSCRIPTION_KEY')),
        )
        assert self.client is not None

    @pytest.mark.live_test_only
    def test_get_map_tile(self):
        result = self.client.get_map_tile(
            tileset_id=TilesetID.MICROSOFT_BASE,
            tile_index_z=6,
            tile_index_x=9,
            tile_index_y=22,
            tile_size="512"
        )
        import types
        assert isinstance(result, types.GeneratorType)


    @pytest.mark.live_test_only
    def test_get_map_tileset(self):
        result = self.client.get_map_tileset(tileset_id=TilesetID.MICROSOFT_BASE)
        assert result.name == "microsoft.base"
        assert "TomTom" in result.attribution
        assert len(result.tiles) > 0


    @pytest.mark.live_test_only
    def test_get_map_attribution(self):
        result = self.client.get_map_attribution(
            tileset_id=TilesetID.MICROSOFT_BASE,
            zoom=6,
            bounds=BoundingBox(south=42.982261, west=24.980233, north=56.526017, east=1.355233)
        )
        assert len(result.copyrights) > 0


    @pytest.mark.live_test_only
    def test_get_copyright_from_bounding_box(self):
        result = self.client.get_copyright_from_bounding_box(
            bounding_box=BoundingBox(south=42.982261, west=24.980233, north=56.526017, east=1.355233)
        )
        assert len(result.general_copyrights) > 0
        copyrights = result.general_copyrights[0]
        assert "TomTom" in copyrights
        assert len(result.regions) > 0


    @pytest.mark.live_test_only
    def test_get_copyright_for_tile(self):
        result = self.client.get_copyright_for_tile(tile_index_z=6, tile_index_x=9, tile_index_y=22)
        assert len(result.general_copyrights) > 0
        copyrights = result.general_copyrights[0]
        assert "TomTom" in copyrights


    @pytest.mark.live_test_only
    def test_get_copyright_caption(self):
        result = self.client.get_copyright_caption()
        assert result.copyrights_caption is not None
        assert "TomTom" in result.copyrights_caption


    @pytest.mark.live_test_only
    def test_get_copyright_for_world(self):
        result = self.client.get_copyright_for_world()
        assert len(result.general_copyrights) > 0
        copyrights = result.general_copyrights[0]
        assert "TomTom" in copyrights
        assert len(result.regions) > 0


if __name__ == "__main__" :
    testArgs = [ "-v" , "-s" ] if len(sys.argv) == 1 else sys.argv[1:]
    #testArgs = [ "-s" , "-n" , "auto" , "--dist=loadscope" ] if len(sys.argv) == 1 else sys.argv[1:]
    #pytest-xdist: -n auto --dist=loadscope
    #pytest-parallel: --tests-per-worker auto
    #print( "testArgs={}".format(testArgs) )

    pytest.main(args=testArgs)

    print("main() Leave")

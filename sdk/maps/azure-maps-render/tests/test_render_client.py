# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import os
from azure.core.credentials import AzureKeyCredential
from azure.maps.render import MapsRenderClient
from devtools_testutils import AzureRecordedTestCase, recorded_by_proxy
from render_preparer import MapsRenderPreparer
from azure.maps.render.models import TilesetID, BoundingBox

class TestMapsRenderClient(AzureRecordedTestCase):
    def setup_method(self, method):
        self.client = MapsRenderClient(
            credential=AzureKeyCredential(os.environ.get('AZURE_SUBSCRIPTION_KEY', "AzureMapsSubscriptionKey"))
        )
        assert self.client is not None

    @MapsRenderPreparer()
    @recorded_by_proxy
    def test_get_map_tile(self):
        result = self.client.get_map_tile(
            tileset_id=TilesetID.MICROSOFT_BASE,
            z=6,
            x=9,
            y=22,
            tile_size="512"
        )

        import types
        assert isinstance(result, types.GeneratorType)

    @MapsRenderPreparer()
    @recorded_by_proxy
    def test_get_map_tileset(self):
        result = self.client.get_map_tileset(tileset_id=TilesetID.MICROSOFT_BASE)
        assert result.name == "microsoft.base"
        assert "TomTom" in result.map_attribution
        assert len(result.tiles_endpoints) > 0

    @MapsRenderPreparer()
    @recorded_by_proxy
    def test_get_map_attribution(self):
        result = self.client.get_map_attribution(
            tileset_id=TilesetID.MICROSOFT_BASE,
            zoom=6,
            bounds=BoundingBox(south=42.982261, west=24.980233, north=56.526017, east=1.355233)
        )
        assert len(result.copyrights) > 0

    @MapsRenderPreparer()
    @recorded_by_proxy
    def test_get_copyright_from_bounding_box(self):
        result = self.client.get_copyright_from_bounding_box(
            bounding_box=BoundingBox(south=42.982261, west=24.980233, north=56.526017, east=1.355233)
        )
        assert len(result.general_copyrights) > 0
        copyrights = result.general_copyrights[0]
        assert "TomTom" in copyrights
        assert len(result.regions) > 0

    @MapsRenderPreparer()
    @recorded_by_proxy
    def test_get_copyright_for_tile(self):
        result = self.client.get_copyright_for_tile(z=6, x=9, y=22)
        assert len(result.general_copyrights) > 0
        copyrights = result.general_copyrights[0]
        assert "TomTom" in copyrights

    @MapsRenderPreparer()
    @recorded_by_proxy
    def test_get_copyright_caption(self):
        result = self.client.get_copyright_caption()
        assert result.copyrights_caption is not None
        assert "TomTom" in result.copyrights_caption

    @MapsRenderPreparer()
    @recorded_by_proxy
    def test_get_copyright_for_world(self):
        result = self.client.get_copyright_for_world()
        assert len(result.general_copyrights) > 0
        copyrights = result.general_copyrights[0]
        assert "TomTom" in copyrights
        assert len(result.regions) > 0

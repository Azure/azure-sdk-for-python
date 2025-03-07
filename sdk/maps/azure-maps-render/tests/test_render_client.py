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
from azure.maps.render import TilesetID


class TestMapsRenderClient(AzureRecordedTestCase):
    def setup_method(self, method):
        self.client = MapsRenderClient(
            credential=AzureKeyCredential(os.getenv("AZURE_SUBSCRIPTION_KEY", "AzureSubscriptionKey"))
        )
        assert self.client is not None

    @MapsRenderPreparer()
    @recorded_by_proxy
    def test_get_map_tile(self):
        result = self.client.get_map_tile(tileset_id=TilesetID.MICROSOFT_BASE, z=6, x=9, y=22, tile_size="512")

        import types

        assert isinstance(result, types.GeneratorType)

    @MapsRenderPreparer()
    @recorded_by_proxy
    def test_get_map_tileset(self):
        result = self.client.get_map_tileset(tileset_id=TilesetID.MICROSOFT_BASE)
        assert result.get("name", False) and (
            result["name"] == "microsoft.base" or result["name"] == "microsoft.core.vector"
        )
        assert len(result.get("tiles", [])) > 0

    @MapsRenderPreparer()
    @recorded_by_proxy
    def test_get_map_attribution(self):
        result = self.client.get_map_attribution(
            tileset_id=TilesetID.MICROSOFT_BASE,
            zoom=6,
            bounds=[42.982261, 24.980233, 56.526017, 1.355233],
        )
        assert len(result.get("copyrights", [])) > 0
        assert "TomTom" in result["copyrights"][0] or "TomTom" in result["copyrights"][1]

    @MapsRenderPreparer()
    @recorded_by_proxy
    def test_get_copyright_from_bounding_box(self):
        result = self.client.get_copyright_from_bounding_box(
            south_west=[42.982261, 24.980233],
            north_east=[56.526017, 1.355233],
        )
        assert len(result.get("regions", [])) > 0
        assert len(result.get("generalCopyrights", [])) > 0
        copyrights = result["generalCopyrights"][0]
        assert "TomTom" in copyrights

    @MapsRenderPreparer()
    @recorded_by_proxy
    def test_get_copyright_for_tile(self):
        result = self.client.get_copyright_for_tile(z=6, x=9, y=22)
        assert len(result.get("generalCopyrights", [])) > 0
        copyrights = result["generalCopyrights"][0]
        assert "TomTom" in copyrights

    @MapsRenderPreparer()
    @recorded_by_proxy
    def test_get_copyright_caption(self):
        result = self.client.get_copyright_caption()
        assert result["copyrightsCaption"] is not None
        assert "TomTom" in result["copyrightsCaption"]

    @MapsRenderPreparer()
    @recorded_by_proxy
    def test_get_copyright_for_world(self):
        result = self.client.get_copyright_for_world()
        assert result is not None
        assert len(result.get("regions", [])) > 0
        assert len(result["regions"][0].get("copyrights", [])) > 0

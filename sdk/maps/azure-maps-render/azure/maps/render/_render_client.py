# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

# pylint: disable=unused-import,ungrouped-imports, R0904, C0302
from typing import TYPE_CHECKING, overload, Union, Any, List, Optional, Iterator
from azure.core.tracing.decorator import distributed_trace
from azure.core.exceptions import HttpResponseError
from azure.core.credentials import AzureKeyCredential

from ._base_client import MapsRenderClientBase
from ._generated.models import (
    TilesetID
)
from .models import (
    LatLon,
    BoundingBox
)
if TYPE_CHECKING:
    from azure.core.credentials import TokenCredential
    from azure.core.polling import LROPoller

if TYPE_CHECKING:
    from azure.core.credentials import TokenCredential

class MapsRenderClient(MapsRenderClientBase):
    """Azure Maps Render REST APIs.

    :param credential: Credential needed for the client to connect to Azure.
    :type credential: ~azure.core.credentials.TokenCredential or ~azure.core.credentials.AzureKeyCredential
    :keyword api_version:
            The API version of the service to use for requests. It defaults to the latest service version.
            Setting to an older version may result in reduced feature compatibility.
    :paramtype api_version: str
    """
    def __init__(
        self,
        credential, # type: Union[AzureKeyCredential, TokenCredential]
        **kwargs  # type: Any
    ):
        # type: (...) -> None

        super().__init__(
            credential=credential, **kwargs
        )

    @distributed_trace
    def get_map_tile(
        self,
        tileset_id,  # type: Union[str, TilesetID]
        tile_index_z, # type: int
        tile_index_x, # type: int
        tile_index_y, # type: int
        **kwargs  # type: Any
    ):
        # type: (...) -> Iterator[bytes]
        """The Get Map Tiles API allows users to request map tiles in vector or raster formats typically
        to be integrated into a map control or SDK. Some example tiles that can be requested are Azure
        Maps road tiles, real-time  Weather Radar tiles. By default, Azure Maps uses vector tiles for its web map
        control (Web SDK) and Android SDK.

        :param tileset_id:
            A tileset is a collection of raster or vector data broken up into a
            uniform grid of square tiles at preset zoom levels. Every tileset has a **tilesetId** to use
            when making requests.
        :type tileset_id:
            str or ~azure.maps.render.models.TilesetID
        :param tile_index_z:
            Zoom level for the desired tile.
        :type tile_index_z: int
        :param tile_index_x:
            X coordinate of the tile on zoom grid.
        :type tile_index_x: int
        :param tile_index_y:
            Y coordinate of the tile on zoom grid.
        :type tile_index_y: int
        :keyword time_stamp:
            The desired date and time of the requested tile.
        :paramtype time_stamp: ~datetime.datetime
        :keyword tile_size:
            The size of the returned map tile in pixels. Default is 256.
        :paramtype tile_size: ~azure.maps.render.models.MapTileSize
        :keyword language:
            Language in which search results should be returned.
        :paramtype language: str
        :keyword localized_map_view:
            The View parameter (also called the "user region" parameter)
            allows you to show the correct maps for a certain country/region for geopolitically disputed
            regions.
        :paramtype localized_map_view: str or ~azure.maps.render.models.LocalizedMapView
        :return:
            Iterator of the response bytes
        :rtype: Iterator[bytes]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

        return self._render_client.get_map_tile(
            tileset_id=tileset_id,
            z=tile_index_z,
            x=tile_index_x,
            y=tile_index_y,
            **kwargs
        )


    @distributed_trace
    def get_map_tileset(
        self,
        tileset_id,  # type: Union[str, TilesetID]
        **kwargs # type: Any
    ):
        # type: (...) -> models.MapTileset
        """The Get Map Tileset API allows users to request metadata for a tileset.

        :param tileset_id:
            A tileset is a collection of raster or vector data broken up into a
            uniform grid of square tiles at preset zoom levels. Every tileset has a **tilesetId** to use
            when making requests.
        :type tileset_id:
            str or ~azure.maps.render.models.TilesetID
        :return: MapTileset
        :rtype: ~azure.maps.render.models.MapTileset
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        return self._render_client.get_map_tileset(
            tileset_id=tileset_id,
            **kwargs
        )


    @distributed_trace
    def get_map_attribution(
        self,
        tileset_id,  # type: Union[str, "models.TilesetID"]
        zoom, #type: int
        bounds, # type: BoundingBox
        **kwargs # type: Any
    ):
        # type: (...) -> models.MapAttribution
        """The Get Map Attribution API allows users to request map copyright attribution information for a
        section of a tileset.

        :param tileset_id:
            A tileset is a collection of raster or vector data broken up into a
            uniform grid of square tiles at preset zoom levels. Every tileset has a **tilesetId** to use
            when making requests.
        :type tileset_id: str or ~azure.maps.render.models.TilesetID
        :param zoom:
            Zoom level for the desired map attribution.
        :type zoom: int
        :param bounds:
            The string that represents the rectangular area of a bounding box. The bounds
            parameter is defined by the 4 bounding box coordinates, with WGS84 longitude and latitude of
            the southwest corner which is "bottom_left" followed by
            WGS84 longitude and latitude of the northeast corner which is "top_right".
        :type bounds: BoundingBox
        :return: MapAttribution
        :rtype: ~azure.maps.render.models.MapAttribution
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        bounds=[
            bounds.bottom_left.lat,
            bounds.bottom_left.lon,
            bounds.top_right.lat,
            bounds.top_right.lon
        ]

        return self._render_client.get_map_attribution(
            tileset_id=tileset_id,
            zoom=zoom,
            bounds=bounds,
            **kwargs
        )

    @distributed_trace
    def get_map_state_tile(
        self,
        stateset_id,  # type: str
        tile_index_z, # type: int
        tile_index_x, # type: int
        tile_index_y, # type: int
        **kwargs  # type: Any
    ):
        # type: (...) -> Iterator[bytes]
        """Fetches state tiles in vector format typically to be integrated into indoor maps module of map
        control or SDK.

        :param tile_index_z:
            Zoom level for the desired tile.
        :type tile_index_z: int
        :param tile_index_x:
            X coordinate of the tile on zoom grid.
        :type tile_index_x: int
        :param tile_index_y:
            Y coordinate of the tile on zoom grid.
        :type tile_index_y: int
        :param stateset_id:
            The stateset id.
        :type stateset_id: str
        :return: Iterator of the response bytes
        :rtype: Iterator[bytes]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

        return self._render_client.get_map_state_tile(
            stateset_id=stateset_id,
            z=tile_index_z,
            x=tile_index_x,
            y=tile_index_y,
            **kwargs
        )


    @distributed_trace
    def get_copyright_caption(
        self,
        **kwargs  # type: Any
    ):
        # type: (...) -> "models.CopyrightCaption"
        """Copyrights API is designed to serve copyright information for Render Tile
        service. In addition to basic copyright for the whole map, API is serving
        specific groups of copyrights for some countries.

        As an alternative to copyrights for map request, one can receive captions
        for displaying the map provider information on the map.

        :return: Get Copyright Caption Result
        :rtype: ~azure.maps.render.models.CopyrightCaption
        :raises: ~azure.core.exceptions.HttpResponseError
        """

        return self._render_client.get_copyright_caption(
            **kwargs
        )

    @distributed_trace
    def get_map_static_image(
        self,
        img_format, # type Union[str, "models.RasterTileFormat"]
        **kwargs  # type: Any
    ):
        # type: (...) -> Iterator[bytes]
        """ The static image service renders a user-defined, rectangular image containing a map section
        using a zoom level from 0 to 20. The static image service renders a user-defined, rectangular
        image containing a map section using a zoom level from 0 to 20. The supported resolution range
        for the map image is from 1x1 to 8192x8192. If you are deciding when to use the static image
        service over the map tile service, you may want to consider how you would like to interact with
        the rendered map. If the map contents will be relatively unchanging, a static map is a good
        choice. If you want to support a lot of zooming, panning and changing of the map content, the
        map tile service would be a better choice.

        :param img_format:
            Desired format of the response. Possible value: png. "png" Default value is "png".
        :type img_format: str or ~azure.maps.render.models.RasterTileFormat
        :keyword layer:
            Map layer requested.
        :paramtype layer: str or ~azure.maps.render.models.StaticMapLayer
        :keyword style:
            Map style to be returned.
        :paramtype style: str or ~azure.maps.render.models.MapImageStyle
        :keyword zoom:
            Desired zoom level of the map.
        :paramtype zoom: int
        :keyword center:
            Coordinates of the center point.
        :paramtype center: BoundingBox
        :keyword bounding_box_private:
            Bounding box.
        :paramtype bounding_box_private: BoundingBox
        :keyword height:
            Height of the resulting image in pixels. Range is 1 to 8192.
        :paramtype height: int
        :keyword width:
            Width of the resulting image in pixels. Range is 1 to 8192. Default is 512.
        :paramtype width: int
        :keyword language:
            Language in which search results should be returned.
        :paramtype language: str
        :keyword localized_map_view:
            The View parameter (also called the "user region" parameter)
            allows you to show the correct maps for a certain country/region for geopolitically disputed
            regions.
        :paramtype localized_map_view: str or ~azure.maps.render.models.LocalizedMapView
        :keyword pins:
            Pushpin style and instances. Use this parameter to optionally add pushpins to the image.
        :paramtype pins: list[str]
        :keyword path:
            Path style and locations. Use this parameter to optionally add lines, polygons
            or circles to the image.
        :paramtype path: list[str]
        :return: Iterator of the response bytes
        :rtype: Iterator[bytes]
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        return self._render_client.get_map_static_image(
            format=img_format,
            **kwargs
        )

    @distributed_trace
    def get_copyright_from_bounding_box(
        self,
        bounding_box, #type: BoundingBox
        **kwargs  # type: Any
    ):
        # type: (...) -> "models.Copyright"
        """Returns copyright information for a given bounding box. Bounding-box requests should specify
        the minimum and maximum longitude and latitude (EPSG-3857) coordinates.

        :param bounding_box:
            Position of the south_west and north_east as boundingbox type.
        :type: BoundingBox
        :keyword include_text:
            True or False to exclude textual data from response. Only images and
            country names will be in response.
        :paramtype include_text: bool
        :return: Copyright result
        :rtype: ~azure.maps.render.models.Copyright
        :raises ~azure.core.exceptions.HttpResponseError:
        """

        _include_text=kwargs.pop("include_text", True)

        return self._render_client.get_copyright_from_bounding_box(
            south_west=(bounding_box.bottom_left.lat,bounding_box.bottom_left.lon),
            north_east=(bounding_box.top_right.lat,bounding_box.top_right.lon),
            include_text= "yes" if _include_text else "no",
            **kwargs
        )

    @distributed_trace
    def get_copyright_for_tile(
        self,
        tile_index_z, # type: int
        tile_index_x, # type: int
        tile_index_y, # type: int
        **kwargs  # type: Any
    ):
        # type: (...) -> "models.Copyright"
        """Copyrights API is designed to serve copyright information for Render Tile  service. In addition
        to basic copyright for the whole map, API is serving  specific groups of copyrights for some
        countries.
        Returns the copyright information for a given tile. To obtain the copyright information for a
        particular tile, the request should specify the tile's zoom level and x and y coordinates (see:
        Zoom Levels and Tile Grid).

        :param tile_index_z:
            Zoom level for the desired tile.
        :type tile_index_z: int
        :param tile_index_x:
            X coordinate of the tile on zoom grid.
        :type tile_index_x: int
        :param tile_index_y:
            Y coordinate of the tile on zoom grid.
        :type tile_index_y: int
        :keyword include_text:
            True or False to exclude textual data from response. Only images and
            country names will be in response.
        :paramtype include_text: bool
        :return: Copyright result
        :rtype: ~azure.maps.render.models.Copyright
        :raises ~azure.core.exceptions.HttpResponseError:
        """

        _include_text=kwargs.pop("include_text", True)

        return self._render_client.get_copyright_for_tile(
            z=tile_index_z,
            x=tile_index_x,
            y=tile_index_y,
            include_text= "yes" if _include_text else "no",
            **kwargs
        )

    @distributed_trace
    def get_copyright_for_world(
        self,
        **kwargs  # type: Any
    ):
        # type: (...) -> "models.Copyright"
        """Copyrights API is designed to serve copyright information for Render Tile  service. In addition
        to basic copyright for the whole map, API is serving  specific groups of copyrights for some
        countries.
        Returns the copyright information for the world. To obtain the default copyright information
        for the whole world, do not specify a tile or bounding box.

        :keyword include_text:
            True or False to exclude textual data from response. Only images and
            country names will be in response.
        :paramtype include_text: bool
        :return: Copyright result
        :rtype: ~azure.maps.render.models.Copyright
        :raises ~azure.core.exceptions.HttpResponseError:
        """

        _include_text=kwargs.pop("include_text", True)

        return self._render_client.get_copyright_for_world(
            include_text= "yes" if _include_text else "no",
            **kwargs
        )

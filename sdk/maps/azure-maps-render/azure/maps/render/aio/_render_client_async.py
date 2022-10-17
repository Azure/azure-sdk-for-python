# ---------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# ---------------------------------------------------------------------

# pylint: disable=unused-import,ungrouped-imports, R0904, C0302
from typing import AsyncIterator, Any, Union, Tuple, List
from azure.core.tracing.decorator_async import distributed_trace_async
from azure.core.exceptions import HttpResponseError
from azure.core.credentials import AzureKeyCredential
from azure.core.credentials_async import AsyncTokenCredential

from ._base_client_async import AsyncMapsRenderClientBase

from ..models import (
    LatLon,
    BoundingBox,
    TilesetID,
    Copyright,
    MapTileset,
    MapAttribution,
    CopyrightCaption,
    RasterTileFormat,
    ImagePushpinStyle,
    ImagePathStyle
)


# By default, use the latest supported API version
class MapsRenderClient(AsyncMapsRenderClientBase):
    """Azure Maps Render REST APIs.

    :param credential: Credential needed for the client to connect to Azure.
    :type credential: ~azure.core.credentials.AsyncTokenCredential or ~azure.core.credentials.AzureKeyCredential
    :keyword api_version:
            The API version of the service to use for requests. It defaults to the latest service version.
            Setting to an older version may result in reduced feature compatibility.
    :paramtype api_version: str

    .. admonition:: Example:

        .. literalinclude:: ../samples/async_samples/sample_authentication_async.py
            :start-after: [START create_maps_render_service_client_with_key_async]
            :end-before: [END create_maps_render_service_client_with_key_async]
            :language: python
            :dedent: 4
            :caption: Creating the MapsRenderClient with an subscription key.
        .. literalinclude:: ../samples/async_samples/sample_authentication_async.py
            :start-after: [START create_maps_render_service_client_with_aad_async]
            :end-before: [END create_maps_render_service_client_with_aad_async]
            :language: python
            :dedent: 4
            :caption: Creating the MapsRenderClient with a token credential.
    """
    def __init__(
        self,
        credential: Union[AzureKeyCredential, AsyncTokenCredential],
        **kwargs: Any
    ) -> None:
        super().__init__(
            credential=credential, **kwargs
        )

    @distributed_trace_async
    async def get_map_tile(
        self,
        tileset_id: Union[str, TilesetID],
        z: int,
        x: int,
        y: int,
        **kwargs: Any
    ) -> AsyncIterator[bytes]:
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
        :param z:
            Zoom level for the desired tile.
        :type z: int
        :param x:
            X coordinate of the tile on zoom grid.
        :type x: int
        :param y:
            Y coordinate of the tile on zoom grid.
        :type y: int
        :keyword time_stamp:
            The desired date and time of the requested tile.
        :paramtype time_stamp: ~datetime.datetime
        :keyword tile_size:
            The size of the returned map tile in pixels.
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
            AsyncIterator of the response bytes
        :rtype: AsyncIterator[bytes]
        :raises ~azure.core.exceptions.HttpResponseError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_get_map_tile_async.py
                :start-after: [START get_map_tile_async]
                :end-before: [END get_map_tile_async]
                :language: python
                :dedent: 4
                :caption: Return map tiles in vector or raster formats.
        """

        return await self._render_client.get_map_tile(
            tileset_id=tileset_id,
            z=z,
            x=x,
            y=y,
            **kwargs
        )


    @distributed_trace_async
    async def get_map_tileset(
        self,
        tileset_id: Union[str, TilesetID],
        **kwargs: Any
    ) -> MapTileset:
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

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_get_map_tileset_async.py
                :start-after: [START get_map_tileset_async]
                :end-before: [END get_map_tileset_async]
                :language: python
                :dedent: 4
                :caption: Return metadata for a tileset.
        """
        result = await self._render_client.get_map_tileset(
            tileset_id=tileset_id,
            **kwargs
        )

        return MapTileset(
            name = result.name,
            description = result.description,
            version = result.version,
            template = result.template,
            legend = result.legend,
            scheme = result.scheme,
            min_zoom = result.min_zoom,
            max_zoom = result.max_zoom,
            bounds = result.bounds,
            center = result.center,
            map_attribution=result.attribution,
            tilejson_version=result.tilejson,
            tiles_endpoints=result.tiles,
            grid_endpoints=result.grids,
            data_files=result.data
        )

    @distributed_trace_async
    async def get_map_attribution(
        self,
        tileset_id: Union[str, TilesetID],
        zoom: int,
        bounds: BoundingBox,
        **kwargs: Any
    ) -> MapAttribution:
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
            north(top), west(left), south(bottom), east(right)
            position of the bounding box as float.
            E.g. BoundingBox(west=37.553, south=-122.453, east=33.2, north=57)
        :type bounds: BoundingBox
        :return: MapAttribution
        :rtype: ~azure.maps.render.models.MapAttribution
        :raises ~azure.core.exceptions.HttpResponseError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_get_map_attribution_async.py
                :start-after: [START get_map_attribution_async]
                :end-before: [END get_map_attribution_async]
                :language: python
                :dedent: 4
                :caption: Return map copyright attribution information for a section of a tileset.
        """
        bounds=[
            bounds.south,
            bounds.west,
            bounds.north,
            bounds.east
        ]

        async_result = await self._render_client.get_map_attribution(
            tileset_id=tileset_id,
            zoom=zoom,
            bounds=bounds,
            **kwargs
        )
        return async_result

    @distributed_trace_async
    async def get_map_state_tile(
        self,
        stateset_id: str,
        z: int,
        x: int,
        y: int,
        **kwargs: Any
    ) -> AsyncIterator[bytes]:
        """Fetches state tiles in vector format typically to be integrated into indoor maps module of map
        control or SDK.

        :param z:
            Zoom level for the desired tile.
        :type z: int
        :param x:
            X coordinate of the tile on zoom grid.
        :type x: int
        :param y:
            Y coordinate of the tile on zoom grid.
        :type y: int
        :param stateset_id:
            The stateset id.
        :type stateset_id: str
        :return: AsyncIterator of the response bytes
        :rtype: AsyncIterator[bytes]
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        return await self._render_client.get_map_state_tile(
            stateset_id=stateset_id,
            z=z,
            x=x,
            y=y,
            **kwargs
        )


    @distributed_trace_async
    async def get_copyright_caption(
        self,
        **kwargs: Any
    ) -> CopyrightCaption:
        """Copyrights API is designed to serve copyright information for Render Tile
        service. In addition to basic copyright for the whole map, API is serving
        specific groups of copyrights for some countries.

        As an alternative to copyrights for map request, one can receive captions
        for displaying the map provider information on the map.

        :return: Get Copyright Caption Result
        :rtype: ~azure.maps.render.models.CopyrightCaption
        :raises: ~azure.core.exceptions.HttpResponseError

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_get_copyright_caption_async.py
                :start-after: [START get_copyright_caption_async]
                :end-before: [END get_copyright_caption_async]
                :language: python
                :dedent: 4
                :caption: Return serve copyright information for Render Tile service.
        """
        return await self._render_client.get_copyright_caption(
            **kwargs
        )

    @distributed_trace_async
    async def get_map_static_image(
        self,
        **kwargs: Any
    ) -> AsyncIterator[bytes]:
        """ The static image service renders a user-defined, rectangular image containing a map section
        using a zoom level from 0 to 20. The static image service renders a user-defined, rectangular
        image containing a map section using a zoom level from 0 to 20. The supported resolution range
        for the map image is from 1x1 to 8192x8192. If you are deciding when to use the static image
        service over the map tile service, you may want to consider how you would like to interact with
        the rendered map. If the map contents will be relatively unchanging, a static map is a good
        choice. If you want to support a lot of zooming, panning and changing of the map content, the
        map tile service would be a better choice.

        :keyword img_format:
            Desired format of the response. Possible value: png. "png" Default value is "png".
        :paramtype img_format: str or ~azure.maps.render.models.RasterTileFormat
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
        :paramtype center: LatLon or Tuple
        :keyword BoundingBox bounding_box_private:
            north(top), west(left), south(bottom), east(right)
            position of the bounding box as float.
            E.g. BoundingBox(west=37.553, south=-122.453, east=33.2, north=57)
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
        :paramtype pins:
            list[str] or ~azure.maps.render.models.ImagePushpinStyle
        :keyword path:
            Path style and locations. Use this parameter to optionally add lines, polygons
            or circles to the image.
        :paramtype path:
            list[str] or ~azure.maps.render.models.ImagePathStyle
        :return: AsyncIterator of the response bytes
        :rtype: AsyncIterator[bytes]
        :raises ~azure.core.exceptions.HttpResponseError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_get_map_static_image_async.py
                :start-after: [START get_map_static_image_async]
                :end-before: [END get_map_static_image_async]
                :language: python
                :dedent: 4
                :caption: Return static image service renders a user-defined,
                    rectangular image containing a map section using a zoom level from 0 to 20.
        """
        _pins=kwargs.pop("pins", None)
        if _pins is not None:
            if isinstance(_pins, ImagePushpinStyle):
                res=[
                    f"{ImagePushpinStyle.pushpin_positions or ''}|" \
                    f"{ImagePushpinStyle.label_anchor_shift_in_pixels or ''}|" \
                    f"{ImagePushpinStyle.label_color or ''}|{ImagePushpinStyle.pushpin_scale_ratio or ''}|" \
                    f"{ImagePushpinStyle.custom_pushpin_image_uri or ''}|" \
                    f"{ImagePushpinStyle.label_anchor_shift_in_pixels or ''}|" \
                    f"{ImagePushpinStyle.label_color or ''}|" \
                    f"{ImagePushpinStyle.label_scale_ratio or ''}|" \
                    f"{ImagePushpinStyle.rotation_in_degrees or ''}"
                ]
                _pins = list(filter(None, res))

        _path=kwargs.pop("path", None)
        if _path is not None:
            if isinstance(_path, ImagePathStyle):
                res=[
                    f"{ImagePathStyle.path_positions or ''}|" \
                    f"{ImagePathStyle.line_color or ''}|{ImagePathStyle.fill_color or ''}|" \
                    f"{ImagePathStyle.line_width_in_pixels or ''}|" \
                    f"{ImagePathStyle.circle_radius_in_meters or ''}|" \
                ]
                _path = list(filter(None, res))

        _center=kwargs.pop("center", None)
        if _center is not None:
            _center = [_center[0], _center[1]]

        _bbox = kwargs.pop("bounding_box_private", None)
        if _bbox is not None:
            _bbox = [_bbox.south, _bbox.west, _bbox.north, _bbox.east]

        return await self._render_client.get_map_static_image(
            format=kwargs.pop("img_format", "png"),
            center=_center,
            pins=_pins,
            path=_path,
            bounding_box_private=_bbox,
            **kwargs
        )

    @distributed_trace_async
    async def get_copyright_from_bounding_box(
        self,
        bounding_box: BoundingBox,
        **kwargs: Any
    ) -> Copyright:
        """Returns copyright information for a given bounding box. Bounding-box requests should specify
        the minimum and maximum longitude and latitude (EPSG-3857) coordinates.

        :param bounding_box:
            north(top), west(left), south(bottom), east(right)
            position of the bounding box as float.
            E.g. BoundingBox(west=37.553, south=-122.453, east=33.2, north=57)
        :type: BoundingBox
        :keyword include_text:
            True or False to exclude textual data from response. Only images and
            country names will be in response.
        :paramtype include_text: bool
        :return: Copyright result
        :rtype: ~azure.maps.render.models.Copyright
        :raises ~azure.core.exceptions.HttpResponseError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_get_copyright_from_bounding_box_async.py
                :start-after: [START get_copyright_from_bounding_box_async]
                :end-before: [END get_copyright_from_bounding_box_async]
                :language: python
                :dedent: 4
                :caption: Return copyright information for a given bounding box.
        """
        _include_text=kwargs.pop("include_text", True)

        return await self._render_client.get_copyright_from_bounding_box(
            include_text= "yes" if _include_text else "no",
            south_west=(bounding_box.south,bounding_box.west),
            north_east=(bounding_box.north,bounding_box.east),
            **kwargs
        )

    @distributed_trace_async
    async def get_copyright_for_tile(
        self,
        z: int,
        x: int,
        y: int,
        **kwargs: Any
    ) -> Copyright:
        """Copyrights API is designed to serve copyright information for Render Tile  service. In addition
        to basic copyright for the whole map, API is serving  specific groups of copyrights for some
        countries.
        Returns the copyright information for a given tile. To obtain the copyright information for a
        particular tile, the request should specify the tile's zoom level and x and y coordinates (see:
        Zoom Levels and Tile Grid).

        :param z:
            Zoom level for the desired tile.
        :type z: int
        :param x:
            X coordinate of the tile on zoom grid.
        :type x: int
        :param y:
            Y coordinate of the tile on zoom grid.
        :type y: int
        :keyword include_text:
            True or False to exclude textual data from response. Only images and
            country names will be in response.
        :paramtype include_text: bool
        :return: Copyright result
        :rtype: ~azure.maps.render.models.Copyright
        :raises ~azure.core.exceptions.HttpResponseError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_get_copyright_for_tile_async.py
                :start-after: [START get_copyright_for_tile_async]
                :end-before: [END get_copyright_for_tile_async]
                :language: python
                :dedent: 4
                :caption: Returns the copyright information for a given tile.
        """

        _include_text=kwargs.pop("include_text", True)

        return await self._render_client.get_copyright_for_tile(
            z=z,
            x=x,
            y=y,
            include_text= "yes" if _include_text else "no",
            **kwargs
        )

    @distributed_trace_async
    async def get_copyright_for_world(
        self,
        **kwargs: Any
    ) -> Copyright:
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

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_get_copyright_for_world_async.py
                :start-after: [START get_copyright_for_world_async]
                :end-before: [END get_copyright_for_world_async]
                :language: python
                :dedent: 4
                :caption: Returns the copyright information for the world.
        """
        _include_text=kwargs.pop("include_text", True)

        return await self._render_client.get_copyright_for_world(
            include_text= "yes" if _include_text else "no",
            **kwargs
        )

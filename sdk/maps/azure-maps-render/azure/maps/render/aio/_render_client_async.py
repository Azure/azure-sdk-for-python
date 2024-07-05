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
from .._generated.models import Copyright

from ..models import (
    LatLon,
    BoundingBox,
    TilesetID,
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
            *,
            tileset_id: str,
            z: int,
            x: int,
            y: int,
            time_stamp: Optional[datetime.datetime] = None,
            tile_size: Optional[str] = None,
            language: Optional[str] = None,
            localized_map_view: Optional[str] = None,
            **kwargs: Any
    ) -> Iterator[bytes]:
        """Use to request map tiles in vector or raster format.

        The ``Get Map Tiles`` API in an HTTP GET request that allows users to request map tiles in
        vector or raster formats typically to be integrated  into a map control or SDK. Some example
        tiles that can be requested are Azure Maps road tiles, real-time  Weather Radar tiles or the
        map tiles created using `Azure Maps Creator <https://aka.ms/amcreator>`_. By default,  Azure
        Maps uses vector tiles for its web map control (\\ `Web SDK
        </azure/azure-maps/about-azure-maps#web-sdk>`_\\ ) and `Android SDK
        </azure/azure-maps/about-azure-maps#android-sdk>`_.

        :keyword tileset_id: A tileset is a collection of raster or vector data broken up into a
         uniform grid of square tiles at preset  zoom levels. Every tileset has a **tilesetId** to use
         when making requests. The **tilesetId** for tilesets created using `Azure Maps Creator
         <https://aka.ms/amcreator>`_ are generated through the  `Tileset Create API
         <https://docs.microsoft.com/rest/api/maps-creator/tileset>`_. The ready-to-use tilesets
         supplied  by Azure Maps are listed below. For example, microsoft.base. Known values are:
         "microsoft.base", "microsoft.base.labels", "microsoft.base.hybrid", "microsoft.terra.main",
         "microsoft.base.road", "microsoft.base.darkgrey", "microsoft.base.labels.road",
         "microsoft.base.labels.darkgrey", "microsoft.base.hybrid.road",
         "microsoft.base.hybrid.darkgrey", "microsoft.imagery", "microsoft.weather.radar.main",
         "microsoft.weather.infrared.main", "microsoft.traffic.absolute",
         "microsoft.traffic.absolute.main", "microsoft.traffic.relative",
         "microsoft.traffic.relative.main", "microsoft.traffic.relative.dark",
         "microsoft.traffic.delay", "microsoft.traffic.delay.main", "microsoft.traffic.reduced.main",
         and "microsoft.traffic.incident". Required.
        :paramtype tileset_id: str
        :keyword z: Zoom level for the desired tile.

         Please see `Zoom Levels and Tile Grid
         <https://docs.microsoft.com/azure/location-based-services/zoom-levels-and-tile-grid>`_ for
         details. Required.
        :paramtype z: int
        :keyword x: X coordinate of the tile on zoom grid. Value must be in the range [0,

         Please see `Zoom Levels and Tile Grid
         <https://docs.microsoft.com/azure/location-based-services/zoom-levels-and-tile-grid>`_ for
         details. Required.
        :paramtype x: int
        :keyword y: Y coordinate of the tile on zoom grid. Value must be in the range [0,

         Please see `Zoom Levels and Tile Grid
         <https://docs.microsoft.com/azure/location-based-services/zoom-levels-and-tile-grid>`_ for
         details. Required.
        :paramtype y: int
        :keyword time_stamp: The desired date and time of the requested tile. This parameter must be
         specified in the standard date-time format (e.g. 2019-11-14T16:03:00-08:00), as defined by `ISO
         8601 <https://en.wikipedia.org/wiki/ISO_8601>`_. This parameter is only supported when
         tilesetId parameter is set to one of the values below.


         * microsoft.weather.infrared.main: We provide tiles up to 3 hours in the past. Tiles are
         available in 10-minute intervals. We round the timeStamp value to the nearest 10-minute time
         frame.
         * microsoft.weather.radar.main: We provide tiles up to 1.5 hours in the past and up to 2 hours
         in the future. Tiles are available in 5-minute intervals. We round the timeStamp value to the
         nearest 5-minute time frame. Default value is None.
        :paramtype time_stamp: ~datetime.datetime
        :keyword tile_size: The size of the returned map tile in pixels. Known values are: "256" and
         "512". Default value is None.
        :paramtype tile_size: str
        :keyword language: Language in which search results should be returned. Should be one of
         supported IETF language tags, case insensitive. When data in specified language is not
         available for a specific field, default language is used.

         Please refer to `Supported Languages
         <https://docs.microsoft.com/azure/azure-maps/supported-languages>`_ for details. Default value
         is None.
        :paramtype language: str
        :keyword localized_map_view: The View parameter (also called the "user region" parameter)
         allows you to show the correct maps for a certain country/region for geopolitically disputed
         regions. Different countries/regions have different views of such regions, and the View
         parameter allows your application to comply with the view required by the country/region your
         application will be serving. By default, the View parameter is set to “Unified” even if you
         haven’t defined it in  the request. It is your responsibility to determine the location of your
         users, and then set the View parameter correctly for that location. Alternatively, you have the
         option to set ‘View=Auto’, which will return the map data based on the IP  address of the
         request. The View parameter in Azure Maps must be used in compliance with applicable laws,
         including those  regarding mapping, of the country/region where maps, images and other data and
         third party content that you are authorized to  access via Azure Maps is made available.
         Example: view=IN.

         Please refer to `Supported Views <https://aka.ms/AzureMapsLocalizationViews>`_ for details and
         to see the available Views. Known values are: "AE", "AR", "BH", "IN", "IQ", "JO", "KW", "LB",
         "MA", "OM", "PK", "PS", "QA", "SA", "SY", "YE", "Auto", and "Unified". Default value is None.
        :paramtype localized_map_view: str
        :return: Iterator[bytes]
        :rtype: Iterator[bytes]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

        return await self._render_client.get_map_tile(
            tileset_id=tileset_id,
            z=z,
            x=x,
            y=y,
            time_stamp=time_stamp,
            tile_size=tile_size,
            language=language,
            localized_map_view=localized_map_view,
            **kwargs
        )

    @distributed_trace_async
    async def get_map_tileset(self, *, tileset_id: str, **kwargs: Any) -> JSON:
        """Use to get metadata for a tileset.

        The Get Map Tileset API allows users to request metadata for a tileset.

        :keyword tileset_id: A tileset is a collection of raster or vector data broken up into a
         uniform grid of square tiles at preset  zoom levels. Every tileset has a **tilesetId** to use
         when making requests. The **tilesetId** for tilesets created using `Azure Maps Creator
         <https://aka.ms/amcreator>`_ are generated through the  `Tileset Create API
         <https://docs.microsoft.com/rest/api/maps-creator/tileset>`_. The ready-to-use tilesets
         supplied  by Azure Maps are listed below. For example, microsoft.base. Known values are:
         "microsoft.base", "microsoft.base.labels", "microsoft.base.hybrid", "microsoft.terra.main",
         "microsoft.base.road", "microsoft.base.darkgrey", "microsoft.base.labels.road",
         "microsoft.base.labels.darkgrey", "microsoft.base.hybrid.road",
         "microsoft.base.hybrid.darkgrey", "microsoft.imagery", "microsoft.weather.radar.main",
         "microsoft.weather.infrared.main", "microsoft.traffic.absolute",
         "microsoft.traffic.absolute.main", "microsoft.traffic.relative",
         "microsoft.traffic.relative.main", "microsoft.traffic.relative.dark",
         "microsoft.traffic.delay", "microsoft.traffic.delay.main", "microsoft.traffic.reduced.main",
         and "microsoft.traffic.incident". Required.
        :paramtype tileset_id: str
        :return: JSON object
        :rtype: JSON
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        return await self._render_client.get_map_tileset(
            tileset_id=tileset_id,
            **kwargs
        )

    @distributed_trace_async
    async def get_map_attribution(self, *, tileset_id: str, zoom: int, bounds: List[float], **kwargs: Any) -> JSON:
        """Use to get map copyright attribution information.

        The ``Get Map Attribution`` API allows users to request map copyright attribution information
        for a section of a tileset.

        :keyword tileset_id: A tileset is a collection of raster or vector data broken up into a
         uniform grid of square tiles at preset  zoom levels. Every tileset has a **tilesetId** to use
         when making requests. The **tilesetId** for tilesets created using `Azure Maps Creator
         <https://aka.ms/amcreator>`_ are generated through the  `Tileset Create API
         <https://docs.microsoft.com/rest/api/maps-creator/tileset>`_. The ready-to-use tilesets
         supplied  by Azure Maps are listed below. For example, microsoft.base. Known values are:
         "microsoft.base", "microsoft.base.labels", "microsoft.base.hybrid", "microsoft.terra.main",
         "microsoft.base.road", "microsoft.base.darkgrey", "microsoft.base.labels.road",
         "microsoft.base.labels.darkgrey", "microsoft.base.hybrid.road",
         "microsoft.base.hybrid.darkgrey", "microsoft.imagery", "microsoft.weather.radar.main",
         "microsoft.weather.infrared.main", "microsoft.traffic.absolute",
         "microsoft.traffic.absolute.main", "microsoft.traffic.relative",
         "microsoft.traffic.relative.main", "microsoft.traffic.relative.dark",
         "microsoft.traffic.delay", "microsoft.traffic.delay.main", "microsoft.traffic.reduced.main",
         and "microsoft.traffic.incident". Required.
        :paramtype tileset_id: str
        :keyword zoom: Zoom level for the desired map attribution. Required.
        :paramtype zoom: int
        :keyword bounds: The string that represents the rectangular area of a bounding box. The bounds
         parameter is defined by the 4 bounding box coordinates, with WGS84 longitude and latitude of
         the southwest corner followed by  WGS84 longitude and latitude of the northeast corner. The
         string is presented in the following  format: ``[SouthwestCorner_Longitude,
         SouthwestCorner_Latitude, NortheastCorner_Longitude,  NortheastCorner_Latitude]``. Required.
        :paramtype bounds: list[float]
        :return: JSON object
        :rtype: JSON
        :raises ~azure.core.exceptions.HttpResponseError:
        """

        return await self._render_client.get_map_attribution(
            tileset_id=tileset_id,
            zoom=zoom,
            bounds=bounds,
            **kwargs
        )

    @distributed_trace_async
    async def get_map_state_tile(self, *, z: int, x: int, y: int, stateset_id: str, **kwargs: Any) -> Iterator[bytes]:
        """Use to get state tiles in vector format that can then be used to display feature state
        information in an indoor map.

        Fetches state tiles in vector format typically to be integrated into indoor maps module of map
        control or SDK. The map control will call this API after user turns on dynamic styling. For
        more information, see `Zoom Levels and Tile Grid
        </azure/location-based-services/zoom-levels-and-tile-grid>`_.

        :keyword z: Zoom level for the desired tile.

         Please see `Zoom Levels and Tile Grid
         <https://docs.microsoft.com/azure/location-based-services/zoom-levels-and-tile-grid>`_ for
         details. Required.
        :paramtype z: int
        :keyword x: X coordinate of the tile on zoom grid. Value must be in the range [0,

         Please see `Zoom Levels and Tile Grid
         <https://docs.microsoft.com/azure/location-based-services/zoom-levels-and-tile-grid>`_ for
         details. Required.
        :paramtype x: int
        :keyword y: Y coordinate of the tile on zoom grid. Value must be in the range [0,

         Please see `Zoom Levels and Tile Grid
         <https://docs.microsoft.com/azure/location-based-services/zoom-levels-and-tile-grid>`_ for
         details. Required.
        :paramtype y: int
        :keyword stateset_id: The stateset id. Required.
        :paramtype stateset_id: str
        :return: Iterator[bytes]
        :rtype: Iterator[bytes]
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
    async def get_copyright_caption(self, format: str = "json", **kwargs: Any) -> JSON:
        """Use to get copyright information to use when rendering a tile.

        The ``Get Copyright Caption`` API is an HTTP GET request designed to serve copyright
        information to be used with tiles requested from the Render service. In addition to a basic
        copyright for the whole map, it can serve specific groups of copyrights for some
        countries/regions.

        As an alternative to copyrights for map request, it can also return captions for displaying
        provider information on the map.

        :param format: Desired format of the response. Value can be either *json* or *xml*. Known
         values are: "json" and "xml". Default value is "json".
        :type format: str
        :return: JSON object
        :rtype: JSON
        :raises ~azure.core.exceptions.HttpResponseError:
        """

        return await self._render_client.get_copyright_caption(
            format=format,
            **kwargs
        )

    @distributed_trace_async
    async def get_map_static_image(
            self,
            *,
            tileset_id: Optional[str] = None,
            traffic_layer: Optional[str] = None,
            zoom: Optional[int] = None,
            center: Optional[List[float]] = None,
            bounding_box_private: Optional[List[float]] = None,
            height: Optional[int] = None,
            width: Optional[int] = None,
            language: Optional[str] = None,
            localized_map_view: Optional[str] = None,
            pins: Optional[List[str]] = None,
            path: Optional[List[str]] = None,
            **kwargs: Any
    ) -> Iterator[bytes]:
        """This rendering API produces static, rasterized map views of a user-defined area. It's suitable
        for lightweight web applications, when the desired user experience doesn't require interactive
        map controls, or when bandwidth is limited. This API is also useful for embedding maps in
        applications outside of the browser, in backend services, report generation, or desktop
        applications.

         This API includes parameters for basic data visualization:


        * Labeled pushpins in multiple styles.
        * Render circle, path, and polygon geometry types.

        *Note* : Either **center** or **bbox** parameter must be supplied to the API.

        :keyword tileset_id: Map style to be returned. Possible values are microsoft.base.road,
         microsoft.base.darkgrey, and microsoft.imagery.  Default value is set to be
         microsoft.base.road. For more information, see `Render TilesetId
         <https://learn.microsoft.com/en-us/rest/api/maps/render/get-map-tileset?view=rest-maps-2023-06-01&tabs=HTTP#tilesetid>`_.
         Known values are: "microsoft.base", "microsoft.base.labels", "microsoft.base.hybrid",
         "microsoft.terra.main", "microsoft.base.road", "microsoft.base.darkgrey",
         "microsoft.base.labels.road", "microsoft.base.labels.darkgrey", "microsoft.base.hybrid.road",
         "microsoft.base.hybrid.darkgrey", "microsoft.imagery", "microsoft.weather.radar.main",
         "microsoft.weather.infrared.main", "microsoft.traffic.absolute",
         "microsoft.traffic.absolute.main", "microsoft.traffic.relative",
         "microsoft.traffic.relative.main", "microsoft.traffic.relative.dark",
         "microsoft.traffic.delay", "microsoft.traffic.delay.main", "microsoft.traffic.reduced.main",
         and "microsoft.traffic.incident". Default value is None.
        :paramtype tileset_id: str
        :keyword traffic_layer: Optional Value, indicating no traffic flow overlaid on the image
         result. Possible values are microsoft.traffic.relative.main and none. Default value is none,
         indicating no traffic flow returned. If traffic related tilesetId is provided, will return map
         image with corresponding traffic layer. For more information, see `Render TilesetId
         <https://learn.microsoft.com/en-us/rest/api/maps/render/get-map-tileset?view=rest-maps-2023-06-01&tabs=HTTP#tilesetid>`_.
         Known values are: "microsoft.traffic.relative.main" and "none". Default value is None.
        :paramtype traffic_layer: str
        :keyword zoom: Desired zoom level of the map. Support zoom value range from 0-20 (inclusive)
         for tilesetId being microsoft.base.road or microsoft.base.darkgrey. Support zoom value range
         from 0-19 (inclusive) for tilesetId being microsoft.imagery. Default value is
         <https://docs.microsoft.com/azure/location-based-services/zoom-levels-and-tile-grid>`_. Default
         value is None.
        :paramtype zoom: int
        :keyword center: Coordinates of the center point in double. Format: 'lon,lat'. Longitude range:
         -180 to 180. Latitude range: -90 to 90.

         Note: Either center or bbox are required parameters. They are
         mutually exclusive. Default value is None.
        :paramtype center: list[float]
        :keyword bounding_box_private: A bounding box is defined by two latitudes and two longitudes
         that represent the four sides of a rectangular area on the Earth. Format : 'minLon, minLat,
         maxLon, maxLat' (in double).

         Note: Either bbox or center are required
         parameters. They are mutually exclusive. bbox shouldn’t be used with
         height or width.

         The maximum and minimum allowed ranges for Lat and Lon are defined for each zoom level
         in the table at the top of this page. Default value is None.
        :paramtype bounding_box_private: list[float]
        :keyword height: Height of the resulting image in pixels. Range from 80 to 1500. Default
         is 512. It shouldn’t be used with bbox. Default value is None.
        :paramtype height: int
        :keyword width: Width of the resulting image in pixels. Range from 80 to 2000. Default is 512.
         It should not be used with bbox. Default value is None.
        :paramtype width: int
        :keyword language: Language in which search results should be returned. Should be one of
         supported IETF language tags, case insensitive. When data in specified language is not
         available for a specific field, default language is used.

         Please refer to `Supported Languages
         <https://docs.microsoft.com/azure/azure-maps/supported-languages>`_ for details. Default value
         is None.
        :paramtype language: str
        :keyword localized_map_view: The View parameter (also called the "user region" parameter)
         allows you to show the correct maps for a certain country/region for geopolitically disputed
         regions. Different countries/regions have different views of such regions, and the View
         parameter allows your application to comply with the view required by the country/region your
         application will be serving. By default, the View parameter is set to “Unified” even if you
         haven’t defined it in  the request. It is your responsibility to determine the location of your
         users, and then set the View parameter correctly for that location. Alternatively, you have the
         option to set ‘View=Auto’, which will return the map data based on the IP  address of the
         request. The View parameter in Azure Maps must be used in compliance with applicable laws,
         including those  regarding mapping, of the country/region where maps, images and other data and
         third party content that you are authorized to  access via Azure Maps is made available.
         Example: view=IN.

         Please refer to `Supported Views <https://aka.ms/AzureMapsLocalizationViews>`_ for details and
         to see the available Views. Known values are: "AE", "AR", "BH", "IN", "IQ", "JO", "KW", "LB",
         "MA", "OM", "PK", "PS", "QA", "SA", "SY", "YE", "Auto", and "Unified". Default value is None.
        :paramtype localized_map_view: str
        :keyword pins: Pushpin style and instances. Use this parameter to optionally add pushpins to
         the image.
         The pushpin style describes the appearance of the pushpins, and the instances specify
         the coordinates of the pushpins (in double) and optional labels for each pin. (Be sure to
         properly URL-encode values of this
         parameter since it will contain reserved characters such as pipes and punctuation.)

         The Azure Maps account S0 SKU only supports a single instance of the pins parameter. Other
         SKUs
         allow multiple instances of the pins parameter to specify multiple pin styles.

         To render a pushpin at latitude 45°N and longitude 122°W using the default built-in pushpin
         style, add the
         querystring parameter

         ``pins=default||-122 45``

         Note that the longitude comes before the latitude.
         After URL encoding this will look like

         ``pins=default%7C%7C-122+45``

         All of the examples here show the pins
         parameter without URL encoding, for clarity.

         To render a pin at multiple locations, separate each location with a pipe character. For
         example, use

         ``pins=default||-122 45|-119.5 43.2|-121.67 47.12``

         The S0 Azure Maps account SKU only allows five pushpins. Other account SKUs do not have this
         limitation.

         Style Modifiers
         ^^^^^^^^^^^^^^^

         You can modify the appearance of the pins by adding style modifiers. These are added after the
         style but before
         the locations and labels. Style modifiers each have a two-letter name. These abbreviated names
         are used to help
         reduce the length of the URL.

         To change the color of the pushpin, use the 'co' style modifier and specify the color using
         the HTML/CSS RGB color
         format which is a six-digit hexadecimal number (the three-digit form is not supported). For
         example, to use
         a deep pink color which you would specify as #FF1493 in CSS, use

         ``pins=default|coFF1493||-122 45``

         Pushpin Labels
         ^^^^^^^^^^^^^^

         To add a label to the pins, put the label in single quotes just before the coordinates. Avoid
         using special character such as ``|`` or ``||`` in label. For example, to label
         three pins with the values '1', '2', and '3', use

         ``pins=default||'1'-122 45|'2'-119.5 43.2|'3'-121.67 47.12``

         There is a built-in pushpin style called 'none' that does not display a pushpin image. You can
         use this if
         you want to display labels without any pin image. For example,

         ``pins=none||'A'-122 45|'B'-119.5 43.2``

         To change the color of the pushpin labels, use the 'lc' label color style modifier. For
         example, to use pink
         pushpins with black labels, use

         ``pins=default|coFF1493|lc000000||-122 45``

         To change the size of the labels, use the 'ls' label size style modifier. The label size
         represents the approximate
         height of the label text in pixels. For example, to increase the label size to 12, use

         ``pins=default|ls12||'A'-122 45|'B'-119 43``

         The labels are centered at the pushpin 'label anchor.' The anchor location is predefined for
         built-in pushpins and
         is at the top center of custom pushpins (see below). To override the label anchor, using the
         'la' style modifier
         and provide X and Y pixel coordinates for the anchor. These coordinates are relative to the
         top left corner of the
         pushpin image. Positive X values move the anchor to the right, and positive Y values move the
         anchor down. For example,
         to position the label anchor 10 pixels right and 4 pixels above the top left corner of the
         pushpin image,
         use

         ``pins=default|la10 -4||'A'-122 45|'B'-119 43``

         Custom Pushpins
         ^^^^^^^^^^^^^^^

         To use a custom pushpin image, use the word 'custom' as the pin style name, and then specify a
         URL after the
         location and label information. The maximum allowed size for a customized label image is
         65,536 pixels. Use two pipe characters to indicate that you're done specifying locations and
         are
         starting the URL. For example,

         ``pins=custom||-122 45||http://contoso.com/pushpins/red.png``

         After URL encoding, this would look like

         ``pins=custom%7C%7C-122+45%7C%7Chttp%3A%2F%2Fcontoso.com%2Fpushpins%2Fred.png``

         By default, custom pushpin images are drawn centered at the pin coordinates. This usually
         isn't ideal as it obscures
         the location that you're trying to highlight. To override the anchor location of the pin
         image, use the 'an'
         style modifier. This uses the same format as the 'la' label anchor style modifier. For
         example, if your custom
         pin image has the tip of the pin at the top left corner of the image, you can set the anchor
         to that spot by
         using

         ``pins=custom|an0 0||-122 45||http://contoso.com/pushpins/red.png``

         Note: If you use the 'co' color modifier with a custom pushpin image, the specified color will
         replace the RGB
         channels of the pixels in the image but will leave the alpha (opacity) channel unchanged. This
         would usually
         only be done with a solid-color custom image.

         Scale, Rotation, and Opacity
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^

         You can make pushpins and their labels larger or smaller by using the 'sc' scale style
         modifier. This is a
         value greater than zero. A value of 1 is the standard scale. Values larger than 1 will make
         the pins larger, and
         values smaller than 1 will make them smaller. For example, to draw the pushpins 50% larger
         than normal, use

         ``pins=default|sc1.5||-122 45``

         You can rotate pushpins and their labels by using the 'ro' rotation style modifier. This is a
         number of degrees
         of clockwise rotation. Use a negative number to rotate counter-clockwise. For example, to
         rotate the pushpins
         90 degrees clockwise and double their size, use

         ``pins=default|ro90|sc2||-122 45``

         You can make pushpins and their labels partially transparent by specifying the 'al' alpha
         style modifier.
         This is a number between 0 and 1 indicating the opacity of the pushpins. Zero makes them
         completely transparent
         (and not visible) and 1 makes them completely opaque (which is the default). For example, to
         make pushpins
         and their labels only 67% opaque, use

         ``pins=default|al.67||-122 45``

         * X and Y coordinates can be anywhere within pin image or a margin around it.
           The margin size is the minimum of the pin width and height. Default value is None.
        :paramtype pins: list[str]
        :keyword path: Path style and locations (in double). Use this parameter to optionally add
         lines, polygons or circles to the image.
         The path style describes the appearance of the line and fill. (Be sure to properly URL-encode
         values of this
         parameter since it will contain reserved characters such as pipes and punctuation.)

         Path parameter is supported in Azure Maps account SKU starting with S1. Multiple instances of
         the path parameter
         allow to specify multiple geometries with their styles. Number of parameters per request is
         limited to 10 and
         number of locations is limited to 100 per path.

         To render a circle with radius 100 meters and center point at latitude 45°N and longitude
         122°W using the default style, add the
         querystring parameter

         ``path=ra100||-122 45``

         Note that the longitude comes before the latitude.
         After URL encoding this will look like

         ``path=ra100%7C%7C-122+45``

         All of the examples here show the path parameter without URL encoding, for clarity.

         To render a line, separate each location with a pipe character. For example, use

         ``path=||-122 45|-119.5 43.2|-121.67 47.12``

         A polygon is specified with a closed path, where the first and last points are equal. For
         example, use

         ``path=||-122 45|-119.5 43.2|-121.67 47.12|-122 45``

         Longitude value for locations of lines and polygons can be in the range from -360 to 360 to
         allow for rendering of geometries crossing the anti-meridian.


        :paramtype path: list[str]
        :return: Iterator[bytes]
        :rtype: Iterator[bytes]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

        return await self._render_client.get_map_static_image(
            tileset_id=tileset_id,
            traffic_layer=traffic_layer,
            zoom=zoom,
            center=center,
            bounding_box_private=bounding_box_private,
            height=height,
            width=width,
            language=language,
            localized_map_view=localized_map_view,
            pins=pins,
            path=path,
            **kwargs
        )

    @distributed_trace_async
    async def get_copyright_from_bounding_box(
            self,
            format: str = "json",
            *,
            south_west: List[float],
            north_east: List[float],
            include_text: Optional[str] = None,
            **kwargs: Any
    ) -> JSON:
        """Use to get copyright information for the specified bounding box.

        Returns copyright information for a given bounding box. Bounding-box requests should specify
        the minimum and maximum longitude and latitude (EPSG-3857) coordinates.

        :param format: Desired format of the response. Value can be either *json* or *xml*. Known
         values are: "json" and "xml". Default value is "json".
        :type format: str
        :keyword south_west: Minimum coordinates (south-west point) of bounding box in latitude
         longitude coordinate system. E.g. 52.41064,4.84228. Required.
        :paramtype south_west: list[float]
        :keyword north_east: Maximum coordinates (north-east point) of bounding box in latitude
         longitude coordinate system. E.g. 52.41064,4.84228. Required.
        :paramtype north_east: list[float]
        :keyword include_text: Yes/no value to exclude textual data from response. Only images and
         country/region names will be in response. Known values are: "yes" and "no". Default value is
         None.
        :paramtype include_text: str
        :return: JSON object
        :rtype: JSON
        :raises ~azure.core.exceptions.HttpResponseError:
        """

        return self._render_client.get_copyright_from_bounding_box(
            format,
            south_west=south_west,
            north_east=north_east,
            include_text=include_text,
            **kwargs
        )

    @distributed_trace_async
    async def get_copyright_for_tile(
            self, format: str = "json", *, z: int, x: int, y: int, include_text: Optional[str] = None, **kwargs: Any
    ) -> JSON:
        """Use to get copyright information.

        To obtain the copyright information for a particular tile, the request should specify the
        tile's zoom level and x and y coordinates. For more information, see `Zoom Levels and Tile Grid
        </azure/azure-maps/zoom-levels-and-tile-grid>`_.

        Copyrights API is designed to serve copyright information for Render service. In addition to
        basic copyright for the whole map, API is serving specific groups of copyrights for some
        countries/regions.

        :param format: Desired format of the response. Value can be either *json* or *xml*. Known
         values are: "json" and "xml". Default value is "json".
        :type format: str
        :keyword z: Zoom level for the desired tile.

         Please see `Zoom Levels and Tile Grid
         <https://docs.microsoft.com/azure/location-based-services/zoom-levels-and-tile-grid>`_ for
         details. Required.
        :paramtype z: int
        :keyword x: X coordinate of the tile on zoom grid. Value must be in the range [0,

         Please see `Zoom Levels and Tile Grid
         <https://docs.microsoft.com/azure/location-based-services/zoom-levels-and-tile-grid>`_ for
         details. Required.
        :paramtype x: int
        :keyword y: Y coordinate of the tile on zoom grid. Value must be in the range [0,

         Please see `Zoom Levels and Tile Grid
         <https://docs.microsoft.com/azure/location-based-services/zoom-levels-and-tile-grid>`_ for
         details. Required.
        :paramtype y: int
        :keyword include_text: Yes/no value to exclude textual data from response. Only images and
         country/region names will be in response. Known values are: "yes" and "no". Default value is
         None.
        :paramtype include_text: str
        :return: JSON object
        :rtype: JSON
        :raises ~azure.core.exceptions.HttpResponseError:
        """

        return await self._render_client.get_copyright_for_tile(
            format,
            z=z,
            x=x,
            y=y,
            include_text=include_text,
            **kwargs
        )

    @distributed_trace_async
    async def get_copyright_for_world(
            self, format: str = "json", *, include_text: Optional[str] = None, **kwargs: Any
    ) -> JSON:
        """Use to get copyright information for for the world.

        Returns the copyright information for the world. To obtain the default copyright information
        for the whole world, don't specify a tile or bounding box.

        Copyrights API is designed to serve copyright information for Render service. In addition to
        basic copyright for the whole map, API is serving specific groups of copyrights for some
        countries/regions.

        :param format: Desired format of the response. Value can be either *json* or *xml*. Known
         values are: "json" and "xml". Default value is "json".
        :type format: str
        :keyword include_text: Yes/no value to exclude textual data from response. Only images and
         country/region names will be in response. Known values are: "yes" and "no". Default value is
         None.
        :paramtype include_text: str
        :return: JSON object
        :rtype: JSON
        :raises ~azure.core.exceptions.HttpResponseError:
        """

        _include_text=kwargs.pop("include_text", True)

        return await self._render_client.get_copyright_for_world(
            format,
            include_text=include_text,
            **kwargs
        )

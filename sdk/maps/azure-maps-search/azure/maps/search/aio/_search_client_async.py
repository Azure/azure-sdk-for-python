# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

# pylint: disable=unused-import,ungrouped-imports, R0904, C0302
from typing import Union, Any, IO, List, Optional

from azure.maps.search.models import *
from azure.core.credentials import AzureKeyCredential, TokenCredential
from azure.core.tracing.decorator_async import distributed_trace_async

from ._base_client_async import AsyncMapsSearchClientBase

import azure.maps.search._generated.models as _models

class MapsSearchClient(AsyncMapsSearchClientBase):

    @distributed_trace_async
    async def get_geocoding(
            self,
            *,
            top: int = 5,
            query: Optional[str] = None,
            address_line: Optional[str] = None,
            country_region: Optional[str] = None,
            bounding_box: Optional[BoundingBox] = None,
            localized_map_view: Optional[str] = None,
            coordinates: Optional[LatLon] = None,
            admin_district: Optional[str] = None,
            admin_district2: Optional[str] = None,
            admin_district3: Optional[str] = None,
            locality: Optional[str] = None,
            postal_code: Optional[str] = None,
            **kwargs: Any
    ) -> GeocodingResponse:
        """Use to get latitude and longitude coordinates of a street address or name of a place.

        The ``Get Geocoding`` API is an HTTP ``GET`` request that returns the latitude and longitude
        coordinates of the location being searched.

        In many cases, the complete search service might be too much, for instance if you are only
        interested in traditional geocoding. Search can also be accessed for address look up
        exclusively. The geocoding is performed by hitting the geocoding endpoint with just the address
        or partial address in question. The geocoding search index will be queried for everything above
        the street level data. No Point of Interest (POIs) will be returned. Note that the geocoder is
        very tolerant of typos and incomplete addresses. It will also handle everything from exact
        street addresses or street or intersections as well as higher level geographies such as city
        centers, counties and states. The response also returns detailed address properties such as
        street, postal code, municipality, and country/region information.

        :keyword top: Maximum number of responses that will be returned. Default: 5, minimum: 1 and
         maximum: 20. Default value is 5.
        :paramtype top: int
        :keyword query: A string that contains information about a location, such as an address or
         landmark name. Default value is None.
        :paramtype query: str
        :keyword address_line: The official street line of an address relative to the area, as
         specified by the locality, or postalCode, properties. Typical use of this element would be to
         provide a street address or any official address.

         **If query is given, should not use this parameter.**. Default value is None.
        :paramtype address_line: str
        :keyword country_region: Signal for the geocoding result to an `ISO 3166-1 Alpha-2
         region/country code <https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2>`_ that is specified e.g.
         FR./

         **If query is given, should not use this parameter.**. Default value is None.
        :paramtype country_region: str
        :keyword bounding_box: A rectangular area on the earth defined as a bounding box object. The sides of
         the rectangles are defined by longitude and latitude values. When you specify this parameter,
         the geographical area is taken into account when computing the results of a location query.

         Example: BoundingBox(west=37.553, south=-122.453, east=33.2, north=57). Default value is None.
        :paramtype bounding_box: BoundingBox
        :keyword localized_map_view: A string that represents an `ISO 3166-1 Alpha-2 region/country code
         <https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2>`_. This will alter Geopolitical disputed
         borders and labels to align with the specified user region. By default, the View parameter is
         set to “Auto” even if you haven’t defined it in the request.

         Please refer to `Supported Views <https://aka.ms/AzureMapsLocalizationViews>`_ for details and
         to see the available Views. Default value is None.
        :paramtype localized_map_view: str or ~azure.maps.search.models.LocalizedMapView
        :keyword coordinates: A point on the earth specified as a longitude and latitude. When you
         specify this parameter, the user’s location is taken into account and the results returned may
         be more relevant to the user. Example: LatLon(lat, lon). Default value is None.
        :paramtype coordinates: LatLon
        :keyword admin_district: The country subdivision portion of an address, such as WA.

         **If query is given, should not use this parameter.**. Default value is None.
        :paramtype admin_district: str
        :keyword admin_district2: The county for the structured address, such as King.

         **If query is given, should not use this parameter.**. Default value is None.
        :paramtype admin_district2: str
        :keyword admin_district3: The named area for the structured address.

         **If query is given, should not use this parameter.**. Default value is None.
        :paramtype admin_district3: str
        :keyword locality: The locality portion of an address, such as Seattle.

         **If query is given, should not use this parameter.**. Default value is None.
        :paramtype locality: str
        :keyword postal_code: The postal code portion of an address.

         **If query is given, should not use this parameter.**. Default value is None.
        :paramtype postal_code: str
        :return: GeocodingResponse
        :rtype: ~azure.maps.search.models.GeocodingResponse
        :raises ~azure.core.exceptions.HttpResponseError:
        """

        result = await self._search_client.get_geocoding(
            top=top,
            query=query,
            address_line=address_line,
            country_region=country_region,
            bbox=bounding_box and [bounding_box.west, bounding_box.south, bounding_box.east, bounding_box.north] or None,
            view=localized_map_view,
            coordinates=coordinates and [coordinates.lon, coordinates.lat] or None,
            admin_district=admin_district,
            admin_district2=admin_district2,
            admin_district3=admin_district3,
            locality=locality,
            postal_code=postal_code,
            **kwargs,
        )
        return result

    @distributed_trace_async
    async def get_geocoding_batch(
        self,
        geocoding_batch_request_body: Union[GeocodingBatchRequestBody, IO[bytes]],
        **kwargs: Any
    ) -> GeocodingBatchResponse:
        """Use to send a batch of queries to the `Geocoding </rest/api/maps/search/get-geocoding>`_ API in
        a single request.

        The ``Get Geocoding Batch`` API is an HTTP ``POST`` request that sends batches of up to **100**
        queries to the `Geocoding </rest/api/maps/search/get-geocoding>`_ API in a single request.

        Submit Synchronous Batch Request
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

        The Synchronous API is recommended for lightweight batch requests. When the service receives a
        request, it will respond as soon as the batch items are calculated and there will be no
        possibility to retrieve the results later. The Synchronous API will return a timeout error (a
        408 response) if the request takes longer than 60 seconds. The number of batch items is limited
        to **100** for this API.

        POST Body for Batch Request
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^

        To send the *geocoding* queries you will use a ``POST`` request where the request body will
        contain the ``batchItems`` array in ``json`` format and the ``Content-Type`` header will be set
        to ``application/json``. Here's a sample request body containing 2 *geocoding* queries:

        A *geocoding* batchItem object can accept any of the supported *geocoding* `URI parameters
        </rest/api/maps/search/get-geocoding#uri-parameters>`__.

        The batch should contain at least **1** query.

        Batch Response Model
        ^^^^^^^^^^^^^^^^^^^^

        The batch response contains a ``summary`` component that indicates the ``totalRequests`` that
        were part of the original batch request and ``successfulRequests`` i.e. queries which were
        executed successfully. The batch response also includes a ``batchItems`` array which contains a
        response for each and every query in the batch request. The ``batchItems`` will contain the
        results in the exact same order the original queries were sent in the batch request. Each item
        is of one of the following types:

        * ``GeocodingResponse`` - If the query completed successfully.

        * ``Error`` - If the query failed. The response will contain a ``code`` and a ``message`` in this case.

        :param geocoding_batch_request_body: The list of address geocoding queries/requests to process.
         The list can contain a max of 100 queries and must contain at least 1 query. Is either a
         GeocodingBatchRequestBody type or a IO[bytes] type. Required.
        :type geocoding_batch_request_body: ~azure.maps.search.models.GeocodingBatchRequestBody or
         IO[bytes]
        :return: GeocodingBatchResponse
        :rtype: ~azure.maps.search.models.GeocodingBatchResponse
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        generated_batch_items = []
        for batch_item in geocoding_batch_request_body.batch_items:
            bounding_box = batch_item.bounding_box
            coordinates = batch_item.coordinates
            generated_batch_items.append(_models.GeocodingBatchRequestItem(
                optional_id=batch_item.optional_id,
                top=batch_item.top,
                query=batch_item.query,
                address_line=batch_item.address_line,
                country_region=batch_item.country_region,
                bbox=bounding_box and [bounding_box.west, bounding_box.south, bounding_box.east, bounding_box.north] or None,
                view=batch_item.localized_map_view,
                coordinates=coordinates and [coordinates.lon, coordinates.lat] or None,
                admin_district=batch_item.admin_district,
                admin_district2=batch_item.admin_district2,
                admin_district3=batch_item.admin_district3,
                locality=batch_item.locality,
                postal_code=batch_item.postal_code,
            ))
        result = await self._search_client.get_geocoding_batch(
            geocoding_batch_request_body=_models.GeocodingBatchRequestBody(
                batch_items=generated_batch_items,
            ),
            **kwargs
        )
        return result

    @distributed_trace_async
    async def get_reverse_geocoding(
            self,
            *,
            coordinates: LatLon,
            result_types: Optional[List[Union[str, ReverseGeocodingResultTypeEnum]]] = None,
            localized_map_view: Optional[str] = None,
            **kwargs: Any
    ) -> GeocodingResponse:
        """Use to get a street address and location info from latitude and longitude coordinates.

        The ``Get Reverse Geocoding`` API is an HTTP ``GET`` request used to translate a coordinate
        (example: 37.786505, -122.3862) into a human understandable street address. Useful in tracking
        applications where you receive a GPS feed from the device or asset and wish to know the address
        associated with the coordinates. This endpoint will return address information for a given
        coordinate.

        :keyword coordinates: The coordinates of the location that you want to reverse geocode.
         Example: LatLon(lat, lon). Required.
        :paramtype coordinates: LatLon
        :keyword result_types: Specify entity types that you want in the response. Only the types you
         specify will be returned. If the point cannot be mapped to the entity types you specify, no
         location information is returned in the response.
         Default value is all possible entities.
         A comma separated list of entity types selected from the following options.


         * Address
         * Neighborhood
         * PopulatedPlace
         * Postcode1
         * AdminDivision1
         * AdminDivision2
         * CountryRegion

         These entity types are ordered from the most specific entity to the least specific entity.
         When entities of more than one entity type are found, only the most specific entity is
         returned. For example, if you specify Address and AdminDistrict1 as entity types and entities
         were found for both types, only the Address entity information is returned in the response.
         Default value is None.
        :paramtype result_types: list[str or ~azure.maps.search.models.ReverseGeocodingResultTypeEnum]
        :keyword localized_map_view: A string that represents an `ISO 3166-1 Alpha-2 region/country code
         <https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2>`_. This will alter Geopolitical disputed
         borders and labels to align with the specified user region. By default, the View parameter is
         set to “Auto” even if you haven’t defined it in the request.

         Please refer to `Supported Views <https://aka.ms/AzureMapsLocalizationViews>`_ for details and
         to see the available Views. Default value is None.
        :paramtype localized_map_view: str or ~azure.maps.search.models.LocalizedMapView
        :return: GeocodingResponse
        :rtype: ~azure.maps.search.models.GeocodingResponse
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        result = await self._search_client.get_reverse_geocoding(
            coordinates=coordinates and [coordinates.lon, coordinates.lat] or None,
            result_types=result_types,
            view=localized_map_view,
            **kwargs
        )
        return result

    @distributed_trace_async
    async def get_reverse_geocoding_batch(
            self,
            reverse_geocoding_batch_request_body: Union[ReverseGeocodingBatchRequestBody, IO[bytes]],
            **kwargs: Any
    ) -> GeocodingBatchResponse:
        """Use to send a batch of queries to the `Reverse Geocoding
        </rest/api/maps/search/get-reverse-geocoding>`_ API in a single request.

        The ``Get Reverse Geocoding Batch`` API is an HTTP ``POST`` request that sends batches of up to
        **100** queries to `Reverse Geocoding </rest/api/maps/search/get-reverse-geocoding>`_ API using
        a single request.

        Submit Synchronous Batch Request
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

        The Synchronous API is recommended for lightweight batch requests. When the service receives a
        request, it will respond as soon as the batch items are calculated and there will be no
        possibility to retrieve the results later. The Synchronous API will return a timeout error (a
        408 response) if the request takes longer than 60 seconds. The number of batch items is limited
        to **100** for this API.

        POST Body for Batch Request
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^

        To send the *reverse geocoding* queries you will use a ``POST`` request where the request body
        will contain the ``batchItems`` array in ``json`` format and the ``Content-Type`` header will
        be set to ``application/json``. Here's a sample request body containing 2 *reverse geocoding*
        queries:

        A *reverse geocoding* batchItem object can accept any of the supported *reverse geocoding* `URI
        parameters </rest/api/maps/search/get-reverse-geocoding#uri-parameters>`__.

        The batch should contain at least **1** query.

        Batch Response Model
        ^^^^^^^^^^^^^^^^^^^^

        The batch response contains a ``summary`` component that indicates the ``totalRequests`` that
        were part of the original batch request and ``successfulRequests`` i.e. queries which were
        executed successfully. The batch response also includes a ``batchItems`` array which contains a
        response for each and every query in the batch request. The ``batchItems`` will contain the
        results in the exact same order the original queries were sent in the batch request. Each item
        is of one of the following types:


        * ``GeocodingResponse`` - If the query completed successfully.

        * ``Error`` - If the query failed. The response will contain a ``code`` and a ``message`` in this case.

        :param reverse_geocoding_batch_request_body: The list of reverse geocoding queries/requests to
         process. The list can contain a max of 100 queries and must contain at least 1 query. Is either
         a ReverseGeocodingBatchRequestBody type or a IO[bytes] type. Required.
        :type reverse_geocoding_batch_request_body:
         ~azure.maps.search.models.ReverseGeocodingBatchRequestBody or IO[bytes]
        :return: GeocodingBatchResponse
        :rtype: ~azure.maps.search.models.GeocodingBatchResponse
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        generated_batch_items = []
        for batch_item in reverse_geocoding_batch_request_body.batch_items:
            coordinates = batch_item.coordinates
            generated_batch_items.append(_models.ReverseGeocodingBatchRequestItem(
                optional_id=batch_item.optional_id,
                coordinates=coordinates and [coordinates.lon, coordinates.lat] or None,
                result_types=batch_item.result_types,
                view=batch_item.localized_map_view
            ))
        result = await self._search_client.get_reverse_geocoding_batch(
            reverse_geocoding_batch_request_body=_models.ReverseGeocodingBatchRequestBody(
                batch_items=generated_batch_items
            ),
            **kwargs
        )
        return result

    @distributed_trace_async
    async def get_polygon(
            self,
            *,
            coordinates: LatLon,
            localized_map_view: Optional[str] = None,
            result_type: Union[str, BoundaryResultTypeEnum] = "countryRegion",
            resolution: Union[str, ResolutionEnum] = "medium",
            **kwargs: Any
    ) -> Boundary:
        """Use to get polygon data of a geographical area shape such as a city or a country region.

        The ``Get Polygon`` API is an HTTP ``GET`` request that supplies polygon data of a geographical
        area outline such as a city or a country region.

        :keyword coordinates: A point on the earth specified as a longitude and latitude. Example:
         LatLon(lat, lon). Required.
        :paramtype coordinates: LatLon
        :keyword localized_map_view: A string that represents an `ISO 3166-1 Alpha-2 region/country code
         <https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2>`_. This will alter Geopolitical disputed
         borders and labels to align with the specified user region. By default, the View parameter is
         set to “Auto” even if you haven’t defined it in the request.

         Please refer to `Supported Views <https://aka.ms/AzureMapsLocalizationViews>`_ for details and
         to see the available Views. Default value is None.
        :paramtype localized_map_view: str or ~azure.maps.search.models.LocalizedMapView
        :keyword result_type: The geopolitical concept to return a boundary for. Known values are:
         "countryRegion", "adminDistrict", "adminDistrict2", "postalCode", "postalCode2", "postalCode3",
         "postalCode4", "neighborhood", and "locality". Default value is "countryRegion".
        :paramtype result_type: str or ~azure.maps.search.models.BoundaryResultTypeEnum
        :keyword resolution: Resolution determines the amount of points to send back. Known values are:
         "small", "medium", "large", and "huge". Default value is "medium".
        :paramtype resolution: str or ~azure.maps.search.models.ResolutionEnum
        :return: Boundary
        :rtype: ~azure.maps.search.models.Boundary
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        result = await self._search_client.get_polygon(
            coordinates=coordinates and [coordinates.lon, coordinates.lat] or None,
            view=localized_map_view,
            result_type=result_type,
            resolution=resolution,
            **kwargs
        )
        return result

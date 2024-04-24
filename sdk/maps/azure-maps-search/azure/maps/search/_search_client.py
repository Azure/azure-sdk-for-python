# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

# pylint: disable=unused-import,ungrouped-imports, R0904, C0302
from typing import Union, Any, IO, List, Optional

from azure.core.credentials import AzureKeyCredential, TokenCredential
from azure.core.tracing.decorator import distributed_trace
import azure.maps.search._generated.models as _models

from ._base_client import MapsSearchClientBase


# By default, use the latest supported API version
class MapsSearchClient(MapsSearchClientBase):
    """Azure Maps Search REST APIs.

    :param credential:
        Credential needed for the client to connect to Azure.
    :type credential:
        ~azure.core.credentials.TokenCredential or ~azure.core.credentials.AzureKeyCredential
    :keyword str base_url:
        Supported Maps Services or Language resource base_url
        (protocol and hostname, for example: 'https://us.atlas.microsoft.com').
    :keyword str client_id:
        Specifies which account is intended for usage with the Azure AD security model.
        It represents a unique ID for the Azure Maps account.
    :keyword api_version:
        The API version of the service to use for requests.
        It defaults to the latest service version.
        Setting to an older version may result in reduced feature compatibility.
    :paramtype api_version:
        str
    """

    def __init__(
        self,
        credential: Union[AzureKeyCredential, TokenCredential],
        **kwargs: Any
    )-> None:

        super().__init__(
            credential=credential, **kwargs
        )


    @distributed_trace
    def get_geocoding(
            self,
            *,
            top: int = 5,
            query: Optional[str] = None,
            address_line: Optional[str] = None,
            country_region: Optional[str] = None,
            bbox: Optional[List[float]] = None,
            view: Optional[str] = None,
            coordinates: Optional[List[float]] = None,
            admin_district: Optional[str] = None,
            admin_district2: Optional[str] = None,
            admin_district3: Optional[str] = None,
            locality: Optional[str] = None,
            postal_code: Optional[str] = None,
            **kwargs: Any
    ) -> _models.GeocodingResponse:
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
        :keyword bbox: A rectangular area on the earth defined as a bounding box object. The sides of
         the rectangles are defined by longitude and latitude values. When you specify this parameter,
         the geographical area is taken into account when computing the results of a location query.

         Example: lon1,lat1,lon2,lat2. Default value is None.
        :paramtype bbox: list[float]
        :keyword view: A string that represents an `ISO 3166-1 Alpha-2 region/country code
         <https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2>`_. This will alter Geopolitical disputed
         borders and labels to align with the specified user region. By default, the View parameter is
         set to “Auto” even if you haven’t defined it in the request.

         Please refer to `Supported Views <https://aka.ms/AzureMapsLocalizationViews>`_ for details and
         to see the available Views. Default value is None.
        :paramtype view: str
        :keyword coordinates: A point on the earth specified as a longitude and latitude. When you
         specify this parameter, the user’s location is taken into account and the results returned may
         be more relevant to the user. Example: &coordinates=lon,lat. Default value is None.
        :paramtype coordinates: list[float]
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

        result = self._search_client.get_geocoding(
            top=top,
            query=query,
            address_line=address_line,
            country_region=country_region,
            bbox=bbox,
            view=view,
            coordinates=coordinates,
            admin_district=admin_district,
            admin_district2=admin_district2,
            admin_district3=admin_district3,
            locality=locality,
            postal_code=postal_code,
            **kwargs,
        )
        return result

    @distributed_trace
    def get_geocoding_batch(
        self,
        geocoding_batch_request_body: Union[_models.GeocodingBatchRequestBody, IO[bytes]],
        **kwargs: Any
    ) -> _models.GeocodingBatchResponse:
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

        .. code-block::

           POST https://atlas.microsoft.com/geocode:batch?api-version=2023-06-01

        POST Body for Batch Request
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^

        To send the *geocoding* queries you will use a ``POST`` request where the request body will
        contain the ``batchItems`` array in ``json`` format and the ``Content-Type`` header will be set
        to ``application/json``. Here's a sample request body containing 2 *geocoding* queries:

        .. code-block::

           {
             "batchItems": [
               {
                 "addressLine": "One, Microsoft Way, Redmond, WA 98052",
                 "top": 2
               },
               {
                 "addressLine": "Pike Pl",
                 "adminDistrict": "WA",
                 "locality": "Seattle",
                 "top": 3
               }
             ]
           }

        A *geocoding* batchItem object can accept any of the supported *geocoding* `URI parameters
        </rest/api/maps/search/get-geocoding#uri-parameters>`_.

        The batch should contain at least **1** query.

        Batch Response Model
        ^^^^^^^^^^^^^^^^^^^^

        The batch response contains a ``summary`` component that indicates the ``totalRequests`` that
        were part of the original batch request and ``successfulRequests`` i.e. queries which were
        executed successfully. The batch response also includes a ``batchItems`` array which contains a
        response for each and every query in the batch request. The ``batchItems`` will contain the
        results in the exact same order the original queries were sent in the batch request. Each item
        is of one of the following types:


        *
          `\ ``GeocodingResponse`` </rest/api/maps/search/get-geocoding#geocodingresponse>`_ - If the
        query completed successfully.

        *
          ``Error`` - If the query failed. The response will contain a ``code`` and a ``message`` in
        this case.

        :param geocoding_batch_request_body: The list of address geocoding queries/requests to process.
         The list can contain a max of 100 queries and must contain at least 1 query. Is either a
         GeocodingBatchRequestBody type or a IO[bytes] type. Required.
        :type geocoding_batch_request_body: ~azure.maps.search.models.GeocodingBatchRequestBody or
         IO[bytes]
        :return: GeocodingBatchResponse
        :rtype: ~azure.maps.search.models.GeocodingBatchResponse
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        result = self._search_client.get_geocoding_batch(
            geocoding_batch_request_body,
            **kwargs
        )
        return result

    @distributed_trace
    def get_reverse_geocoding(
            self,
            *,
            coordinates: List[float],
            result_types: Optional[List[Union[str, _models.ReverseGeocodingResultTypeEnum]]] = None,
            view: Optional[str] = None,
            **kwargs: Any
    ) -> _models.GeocodingResponse:
        """Use to get a street address and location info from latitude and longitude coordinates.

        The ``Get Reverse Geocoding`` API is an HTTP ``GET`` request used to translate a coordinate
        (example: 37.786505, -122.3862) into a human understandable street address. Useful in tracking
        applications where you receive a GPS feed from the device or asset and wish to know the address
        associated with the coordinates. This endpoint will return address information for a given
        coordinate.

        :keyword coordinates: The coordinates of the location that you want to reverse geocode.
         Example: &coordinates=lon,lat. Required.
        :paramtype coordinates: list[float]
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
        :keyword view: A string that represents an `ISO 3166-1 Alpha-2 region/country code
         <https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2>`_. This will alter Geopolitical disputed
         borders and labels to align with the specified user region. By default, the View parameter is
         set to “Auto” even if you haven’t defined it in the request.

         Please refer to `Supported Views <https://aka.ms/AzureMapsLocalizationViews>`_ for details and
         to see the available Views. Default value is None.
        :paramtype view: str
        :return: GeocodingResponse
        :rtype: ~azure.maps.search.models.GeocodingResponse
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        result = self._search_client.get_reverse_geocoding(
            coordinates=coordinates,
            result_types=result_types,
            view=view,
            **kwargs
        )
        return result

    @distributed_trace
    def get_reverse_geocoding_batch(
            self,
            reverse_geocoding_batch_request_body: Union[_models.ReverseGeocodingBatchRequestBody, IO[bytes]],
            **kwargs: Any
    ) -> _models.GeocodingBatchResponse:
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

        .. code-block::

           POST https://atlas.microsoft.com/reverseGeocode:batch?api-version=2023-06-01

        POST Body for Batch Request
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^

        To send the *reverse geocoding* queries you will use a ``POST`` request where the request body
        will contain the ``batchItems`` array in ``json`` format and the ``Content-Type`` header will
        be set to ``application/json``. Here's a sample request body containing 2 *reverse geocoding*
        queries:

        .. code-block::

           {
             "batchItems": [
               {
                 "coordinates": [-122.128275, 47.639429],
                 "resultTypes": ["Address", "PopulatedPlace"]
               },
               {
                 "coordinates": [-122.341979399674, 47.6095253501216]
               }
             ]
           }

        A *reverse geocoding* batchItem object can accept any of the supported *reverse geocoding* `URI
        parameters </rest/api/maps/search/get-reverse-geocoding#uri-parameters>`_.

        The batch should contain at least **1** query.

        Batch Response Model
        ^^^^^^^^^^^^^^^^^^^^

        The batch response contains a ``summary`` component that indicates the ``totalRequests`` that
        were part of the original batch request and ``successfulRequests`` i.e. queries which were
        executed successfully. The batch response also includes a ``batchItems`` array which contains a
        response for each and every query in the batch request. The ``batchItems`` will contain the
        results in the exact same order the original queries were sent in the batch request. Each item
        is of one of the following types:


        *
          `\ ``GeocodingResponse`` </rest/api/maps/search/get-reverse-geocoding#geocodingresponse>`_ -
        If the query completed successfully.

        *
          ``Error`` - If the query failed. The response will contain a ``code`` and a ``message`` in
        this case.

        :param reverse_geocoding_batch_request_body: The list of reverse geocoding queries/requests to
         process. The list can contain a max of 100 queries and must contain at least 1 query. Is either
         a ReverseGeocodingBatchRequestBody type or a IO[bytes] type. Required.
        :type reverse_geocoding_batch_request_body:
         ~azure.maps.search.models.ReverseGeocodingBatchRequestBody or IO[bytes]
        :return: GeocodingBatchResponse
        :rtype: ~azure.maps.search.models.GeocodingBatchResponse
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        result = self._search_client.get_reverse_geocoding_batch(
            reverse_geocoding_batch_request_body,
            **kwargs
        )
        return result

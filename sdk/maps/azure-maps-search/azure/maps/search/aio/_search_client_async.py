# ---------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# ---------------------------------------------------------------------

# pylint: disable=unused-import,ungrouped-imports, R0904, C0302, too-many-function-args, W0212
from typing import overload, Any, List, Union, Tuple
from collections import namedtuple
from azure.core.tracing.decorator_async import distributed_trace_async
from azure.core.exceptions import HttpResponseError
from azure.core.credentials import AzureKeyCredential
from azure.core.credentials_async import AsyncTokenCredential
from azure.core.polling import AsyncLROPoller

from ._base_client_async import AsyncMapsSearchClientBase
from .._generated.models import (
    PointOfInterestCategory,
    ReverseSearchCrossStreetAddressResult,
    SearchAddressBatchResult,
    Polygon,
)
from ..models import (
    LatLon,
    BoundingBox,
    StructuredAddress,
    SearchAddressResult,
    SearchAlongRouteOptions,
    ReverseSearchAddressResult,
    ReverseSearchAddressBatchProcessResult,
)

from .._shared import (
    parse_geometry_input
)

def get_batch_id_from_poller(polling_method):
    if hasattr(polling_method, "_operation"):
        operation=polling_method._operation
        return operation._location_url.split('/')[-1].split('?')[0]
    return None


# By default, use the latest supported API version
class MapsSearchClient(AsyncMapsSearchClientBase):
    """Azure Maps Search REST APIs.

    :param credential:
        Credential needed for the client to connect to Azure.
    :type credential:
        ~azure.core.credentials.AsyncTokenCredential or ~azure.core.credentials.AzureKeyCredential
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
        credential: Union[AzureKeyCredential, AsyncTokenCredential],
        **kwargs: Any
    )-> None:

        super().__init__(
            credential=credential, **kwargs
        )

    @distributed_trace_async
    async def get_geometries(
        self,
        geometry_ids: List[str],
        **kwargs: Any
    )-> List[Polygon]:
        """**Get Geometries**
        The Get Geometries service allows you to request the geometry data such as a city or country
        outline for a set of entities, previously retrieved from an Online Search request in GeoJSON
        format. The geometry ID is returned in the sourceGeometry object under "geometry" and "id" in
        either a Search Address or Search Fuzzy call.

        :param geometry_ids:
            list of geometry UUIDs string, previously retrieved from an Online Search request.
        :type geometry_ids:
            list[str]
        :return:
            The result list of Polygon/Geometries.
        :rtype:
            List[~azure.maps.search.models.Polygon]
        """
        polygon_result = await self._search_client.list_polygons(
            geometry_ids,
            **kwargs
        )
        result = [] if not polygon_result else polygon_result.polygons
        return result


    @distributed_trace_async
    async def fuzzy_search(
        self,
        query: str,
        **kwargs: Any
    )-> SearchAddressResult:
        """**Free Form Search**

        The basic default API is Free Form Search which handles the most fuzzy of inputs handling any
        combination of address or POI tokens. This search API is the canonical 'single line search'.
        The Free Form Search API is a seamless combination of POI search and geocoding. The API can
        also be weighted with a contextual position (lat./lon. pair), or fully constrained by a
        coordinate and radius, or it can be executed more generally without any geo biasing anchor
        point. We strongly advise you to use the 'country_filter' parameter to
        specify only the countries for which your application needs coverage, as the default behavior
        will be to search the entire world, potentially returning unnecessary results.

        :param query:
            The applicable query string (e.g., "seattle", "pizza"). Can *also* be specified
            as a comma separated string composed by latitude followed by longitude (e.g., "47.641268,
            -122.125679"). Must be properly URL encoded.
        :type query:
            str
        :keyword bool is_type_ahead:
            Boolean. If the typeahead flag is set, the query will be interpreted as a
            partial input and the search will enter predictive mode.
        :keyword str top:
            Maximum number of responses that will be returned. Default: 10, minimum: 1 and
            maximum: 100.
        :keyword int skip:
            Starting offset of the returned results within the full result set. Default: 0,
            minimum: 0 and maximum: 1900.
        :keyword list[int] category_filter:
            A comma-separated list of category set IDs which could be used to
            restrict the result to specific Points of Interest categories. ID order does not matter. When
            multiple category identifiers are provided, only POIs that belong to (at least) one of the
            categories from the provided list will be returned. The list of supported categories can be
            discovered using  `POI Categories API`.
        :keyword int radius_in_meters:
            The radius in meters to for the results to be constrained to the
            defined area.
        :keyword LatLon coordinates:
            coordinates as (lat, lon)
        :keyword country_filter:
            Comma separated string of country codes, e.g. FR,ES. This will limit the
            search to the specified countries.
        :paramtype country_filter:
            list[str]
        :keyword BoundingBox bounding_box:
            north(top), west(left), south(bottom), east(right)
            position of the bounding box as float. E.g. BoundingBox(west=37.553, south=-122.453, east=33.2, north=57)
        :keyword str language:
            Language in which search results should be returned. Should be one of
            supported IETF language tags, case insensitive. When data in specified language is not
            available for a specific field, default language is used.
        :keyword extended_postal_codes_for:
            Indexes for which extended postal codes should be included in
            the results.
        :paramtype extended_postal_codes_for:
            list[str or ~azure.maps.search.models.SearchIndexes]
        :keyword int min_fuzzy_level:
            Minimum fuzziness level to be used.
        :keyword int max_fuzzy_level:
            Maximum fuzziness level to be used.
        :keyword index_filter:
            A comma separated list of indexes which should be utilized for the search.
            Item order does not matter.
        :paramtype index_filter:
            list[str or ~azure.maps.search.models.SearchIndexes]
        :keyword list[str] brand_filter:
            A comma-separated list of brand names which could be used to restrict the
            result to specific brands. Item order does not matter. When multiple brands are provided, only
            results that belong to (at least) one of the provided list will be returned. Brands that
            contain a "," in their name should be put into quotes.
        :keyword electric_vehicle_connector_filter:
            A comma-separated list of connector types which could
            be used to restrict the result to Electric Vehicle Station supporting specific connector types.
            Item order does not matter. When multiple connector types are provided, only results that
            belong to (at least) one of the provided list will be returned.
        :paramtype electric_vehicle_connector_filter:
            list[str or ~azure.maps.search.models.ElectricVehicleConnector]
        :keyword entity_type:
            Specifies the level of filtering performed on geographies. Narrows the
            search for specified geography entity types, e.g. return only municipality. The resulting
            response will contain the geography ID as well as the entity type matched. If you provide more
            than one entity as a comma separated list, endpoint will return the 'smallest entity
            available'.
        :paramtype entity_type:
            str or ~azure.maps.search.models.GeographicEntityType
        :keyword localized_map_view:
            The View parameter (also called the "user region" parameter) allows
            you to show the correct maps for a certain country/region for geopolitically disputed regions.
            Different countries have different views of such regions, and the View parameter allows your
            application to comply with the view required by the country your application will be serving.
            By default, the View parameter is set to “Unified” even if you haven’t defined it in  the
            request. It is your responsibility to determine the location of your users, and then set the
            View parameter correctly for that location. Alternatively, you have the option to set
            ‘View=Auto’, which will return the map data based on the IP  address of the request.
        :paramtype localized_map_view:
            str or ~azure.maps.search.models.LocalizedMapView
        :keyword operating_hours:
            Hours of operation for a POI (Points of Interest). The availability of
            hours of operation will vary based on the data available. If not passed, then no opening hours
            information will be returned.
            Supported value: nextSevenDays.
        :paramtype operating_hours:
            str or ~azure.maps.search.models.OperatingHoursRange
        :return:
            The results of the search.
        :rtype:
            ~azure.maps.search.models.SearchAddressResult
        :raises:
            ~azure.core.exceptions.HttpResponseError:
        """

        coordinates = kwargs.pop("coordinates", (0, 0))
        bounding_box = kwargs.pop("bounding_box", BoundingBox())

        result = await self._search_client.fuzzy_search(
            query,
            lat=coordinates[0],
            lon=coordinates[1],
            btm_right=f"{bounding_box.south}, {bounding_box.east}",
            top_left=f"{bounding_box.north}, {bounding_box.west}",
            **kwargs
        )
        return SearchAddressResult(summary=result.summary, results=result.results)

    @distributed_trace_async
    async def get_point_of_interest_categories(
        self,
        **kwargs: Any
    ) -> List[PointOfInterestCategory]:
        """**Get POI Category Tree**

        POI Category API provides a full list of supported Points of Interest (POI) categories and
        subcategories together with their translations and synonyms. The returned content can be used
        to provide more meaningful results through other Search Service APIs,

        :keyword str language:
            Language in which search results should be returned. Should be one of
            supported IETF language tags, except NGT and NGT-Latn. Language tag is case insensitive. When
            data in specified language is not available for a specific field, default language is used
            (English).
        :return:
            The result as list of point of interest categories.
        :rtype:
            List[~azure.maps.search.models.PointOfInterestCategory]
        :raises:
            ~azure.core.exceptions.HttpResponseError:
        """
        result = await self._search_client.get_point_of_interest_category_tree(
            **kwargs
        )
        return result.categories

    @distributed_trace_async
    async def reverse_search_address(
        self,
        coordinates: LatLon,
        **kwargs: Any
    ) -> ReverseSearchAddressResult:
        """**Search Address Reverse Batch API**

        There may be times when you need to translate a  coordinate (example: 37.786505, -122.3862)
        into a human understandable street address. Most often  this is needed in tracking applications
        where you receive a GPS feed from the device or asset and  wish to know what address where the
        coordinate is located. This endpoint will return address information for a given coordinate.

        :param coordinates:
            The applicable coordinates as (lat, lon)
        :type coordinates:
            LatLon
        :param language:
            Language in which search results should be returned.
        :type language:
            str
        :keyword bool include_speed_limit:
            Boolean. To enable return of the posted speed limit.
        :keyword int heading:
            The directional heading of the vehicle in degrees, for travel along a segment
            of roadway.
        :keyword int radius_in_meters:
            The radius in meters to for the results to be constrained to the
            defined area.
        :keyword str number:
            If a number is sent in along with the request, the response may include the side
            of the street (Left/Right) and also an offset position for that number.
        :keyword bool include_road_use:
            Boolean. To enable return of the road use array for reverse geocodes
            at street level.
        :keyword road_use:
            To restrict reverse geocodes to a certain type of road use.
        :paramtype road_use:
            list[str or ~azure.maps.search.models.RoadUseType]
        :keyword bool allow_freeform_newline:
            Format of newlines in the formatted address.
        :keyword bool include_match_type:
            Include information on the type of match the geocoder achieved in
            the response.
        :keyword entity_type:
            Specifies the level of filtering performed on geographies.
        :paramtype entity_type:
            str or ~azure.maps.search.models.GeographicEntityType
        :keyword localized_map_view:
            The View parameter (also called the "user region" parameter) allows
            you to show the correct maps for a certain country/region for geopolitically disputed regions.
        :paramtype localized_map_view:
            str or ~azure.maps.search.models.LocalizedMapView
        :return:
            The results of the search
        :rtype:
            ~azure.maps.search.models.ReverseSearchAddressResult
        :raises:
            ~azure.core.exceptions.HttpResponseError:
        """
        result = await self._search_client.reverse_search_address(
            query=[coordinates[0], coordinates[1]],
            ** kwargs
        )
        return ReverseSearchAddressResult(summary=result.summary, results=result.addresses)

    @distributed_trace_async
    async def reverse_search_cross_street_address(
        self,
        coordinates: LatLon,
        **kwargs: Any
    )-> ReverseSearchCrossStreetAddressResult:
        """**Reverse Geocode to a Cross Street**

        There may be times when you need to translate a  coordinate (example: 37.786505, -122.3862)
        into a human understandable cross street. Most often this  is needed in tracking applications
        where you  receive a GPS feed from the device or asset and wish to know what address where the
        coordinate is  located.
        This endpoint will return cross street information  for a given coordinate.

        :param coordinates:
            The applicable coordinates as (lat, lon)
        :type coordinates:
            LatLon
        :keyword int top:
            Maximum number of responses that will be returned. Default: 10, minimum: 1 and
            maximum: 100.
        :keyword int heading:
            The directional heading of the vehicle in degrees, for travel along a segment
            of roadway. 0 is North, 90 is East and so on, values range from -360 to 360. The precision can
            include up to one decimal place.
        :keyword int radius_in_meters:
            The radius in meters to for the results to be constrained to the
            defined area.
        :keyword str language:
            Language in which search results should be returned. Should be one of
            supported IETF language tags, case insensitive. When data in specified language is not
            available for a specific field, default language is used.
        :keyword localized_map_view:
            The View parameter (also called the "user region" parameter) allows
            you to show the correct maps for a certain country/region for geopolitically disputed regions.
            Different countries have different views of such regions, and the View parameter allows your
            application to comply with the view required by the country your application will be serving.
            By default, the View parameter is set to “Unified” even if you haven’t defined it in  the
            request. It is your responsibility to determine the location of your users, and then set the
            View parameter correctly for that location. Alternatively, you have the option to set
            ‘View=Auto’, which will return the map data based on the IP  address of the request.
        :paramtype localized_map_view:
            str or ~azure.maps.search.models.LocalizedMapView
        :return:
            The results of the reverse search.
        :rtype:
            ~azure.maps.search.models.ReverseSearchCrossStreetAddressResult
        :raises:
            ~azure.core.exceptions.HttpResponseError:
        """
        return await self._search_client.reverse_search_cross_street_address(
            query=[coordinates[0], coordinates[1]],
            **kwargs
        )

    @distributed_trace_async
    async def search_along_route(
        self,
        query: str,
        max_detour_time: int,
        route: SearchAlongRouteOptions,
        **kwargs: Any
    ) -> SearchAddressResult:
        """
        The Search Along Route endpoint allows you to perform a fuzzy search for POIs along a specified
        route.

        :param query:
            The POI name to search for (e.g., "statue of liberty", "starbucks", "pizza").
            Must be properly URL encoded.
        :type query:
            str
        :param max_detour_time:
            Maximum detour time of the point of interest in seconds. Max value is
            3600 seconds.
        :type max_detour_time:
            int
        :param route:
            This represents the route to search along and should be a valid ``GeoJSON
            LineString`` type.
        :type route:
            ~azure.maps.search.models.SearchAlongRouteOptions
        :keyword int top:
            Maximum number of responses that will be returned. Default value is 10. Max value
         is 20.
        :keyword list[str] brand_filter:
            A comma-separated list of brand names which could be used to restrict the
            result to specific brands. Item order does not matter. When multiple brands are provided, only
            results that belong to (at least) one of the provided list will be returned. Brands that
            contain a "," in their name should be put into quotes.
        :keyword list[int] category_filter:
            A comma-separated list of category set IDs
            which could be used to restrict the result to specific Points of Interest categories.
            ID order does not matter.
        :keyword electric_vehicle_connector_filter:
            A comma-separated list of connector types which could
            be used to restrict the result to Electric Vehicle Station supporting specific connector types.
            Item order does not matter. When multiple connector types are provided, only results that
            belong to (at least) one of the provided list will be returned.
        :paramtype electric_vehicle_connector_filter:
            list[str or ~azure.maps.search.models.ElectricVehicleConnector]
        :keyword localized_map_view:
            The View parameter (also called the "user region" parameter) allows
            you to show the correct maps for a certain country/region for geopolitically disputed regions.
            Different countries have different views of such regions, and the View parameter allows your
            application to comply with the view required by the country your application will be serving.
            By default, the View parameter is set to “Unified” even if you haven’t defined it in  the
            request. It is your responsibility to determine the location of your users, and then set the
            View parameter correctly for that location. Alternatively, you have the option to set
            ‘View=Auto’, which will return the map data based on the IP  address of the request. The View
            parameter in Azure Maps must be used in compliance with applicable laws, including those
            regarding mapping, of the country where maps, images and other data and third party content
            that you are authorized to  access via Azure Maps is made available. Example: view=IN.
        :paramtype localized_map_view:
            str or ~azure.maps.search.models.LocalizedMapView
        :keyword operating_hours:
            Hours of operation for a POI (Points of Interest). The availability of
            hours of operation will vary based on the data available. If not passed, then no opening hours
            information will be returned.
            Supported value: nextSevenDays.
        :paramtype operating_hours:
            str or ~azure.maps.search.models.OperatingHoursRange
        :return:
            The results of the search.
        :rtype:
            ~azure.maps.search.models.SearchAddressResult
        :raises:
            ~azure.core.exceptions.HttpResponseError:
        """
        result = await self._search_client.search_along_route(
            query,
            max_detour_time=max_detour_time,
            route=route,
            **kwargs
        )
        return SearchAddressResult(summary=result.summary, results=result.results)

    @distributed_trace_async
    async def search_inside_geometry(
        self,
        query: str,
        geometry: Union[object, str],
        **kwargs: Any
    ) -> SearchAddressResult:
        """
        The Search Geometry endpoint allows you to perform a free form search inside a single geometry
        or many of them.

        :param query:
            The POI name to search for (e.g., "statue of liberty", "starbucks", "pizza").
            Must be properly URL encoded.
        :type query:
            str
        :param geometry:
            This represents the geometry for one or more geographical features (parks,
            state boundary etc.) to search in and should be a GeoJSON compliant type.
            We are accepting GeoJson object or geo_interface
        :type geometry:
            obejct or str
        :keyword int top:
            Maximum number of responses that will be returned. Default: 10, minimum: 1 and
            maximum: 100.
        :keyword str language:
            Language in which search results should be returned. Should be one of
            supported IETF language tags, case insensitive. When data in specified language is not
            available for a specific field, default language is used.
        :keyword list[int] category_filter:
            A comma-separated list of category set IDs
            which could be used to restrict the result to specific Points of Interest categories.
            ID order does not matter.
        :keyword extended_postal_codes_for:
            Indexes for which extended postal codes should be included in
            the results.
        :paramtype extended_postal_codes_for:
            list[str or ~azure.maps.search.models.SearchIndexes]
        :keyword index_filter:
            A comma separated list of indexes which should be utilized for the search.
            Item order does not matter.
        :paramtype index_filter:
            list[str or ~azure.maps.search.models.SearchIndexes]
        :keyword localized_map_view:
            The View parameter (also called the "user region" parameter) allows
            you to show the correct maps for a certain country/region for geopolitically disputed regions.
            Different countries have different views of such regions, and the View parameter allows your
            application to comply with the view required by the country your application will be serving.
            By default, the View parameter is set to “Unified” even if you haven’t defined it in  the
            request. It is your responsibility to determine the location of your users, and then set the
            View parameter correctly for that location. Alternatively, you have the option to set
            ‘View=Auto’, which will return the map data based on the IP  address of the request. The View
            parameter in Azure Maps must be used in compliance with applicable laws, including those
            regarding mapping, of the country where maps, images and other data and third party content
            that you are authorized to  access via Azure Maps is made available. Example: view=IN.
        :paramtype localized_map_view:
            str or ~azure.maps.search.models.LocalizedMapView
        :keyword operating_hours:
            Hours of operation for a POI (Points of Interest). The availability of
            hours of operation will vary based on the data available. If not passed, then no opening hours
            information will be returned.
            Supported value: nextSevenDays.
        :paramtype operating_hours:
            str or ~azure.maps.search.models.OperatingHoursRange
        :return:
            The results of search.
        :rtype:
            ~azure.maps.search.models.SearchAddressResult
        :raises:
            ~azure.core.exceptions.HttpResponseError:
        """
        result = await self._search_client.search_inside_geometry(
            query,
            geometry=parse_geometry_input(geometry),
            **kwargs
        )
        return SearchAddressResult(result.summary, result.results)


    @distributed_trace_async
    async def search_point_of_interest(
        self,
        query: str,
        **kwargs: Any
    ) -> SearchAddressResult:
        """**Get POI by Name**

        Points of Interest (POI) Search allows you to request POI results by name.  Search supports
        additional query parameters such as language and filtering results by area of interest driven
        by country or bounding box.  Endpoint will return only POI results matching the query string.
        Response includes POI details such as address, coordinate location and category.

        :param query:
            The POI name to search for (e.g., "statue of liberty", "starbucks"), must be
            properly URL encoded.
        :type query:
            str
        :keyword bool is_type_ahead:
            Boolean. If the typeahead flag is set, the query will be interpreted as a
            partial input and the search will enter predictive mode.
        :keyword int top:
            Maximum number of responses that will be returned. Default: 10, minimum: 1 and
            maximum: 100.
        :keyword int skip:
            Starting offset of the returned results within the full result set. Default: 0,
            minimum: 0 and maximum: 1900.
        :keyword list[int] category_filter:
            A comma-separated list of category set IDs which could be used to
            restrict the result to specific Points of Interest categories.
        :keyword list[int] country_filter:
            Comma separated string of country codes, e.g. FR,ES. This will limit the
            search to the specified countries.
        :keyword LatLon coordinates:
            coordinates as (lat, lon)
        :keyword int radius_in_meters:
            The radius in meters to for the results to be constrained to the
            defined area.
        :keyword BoundingBox bounding_box:
            north(top), west(left), south(bottom), east(right)
            position of the bounding box as float. E.g. BoundingBox(west=37.553, south=-122.453, east=33.2, north=57)
        :keyword extended_postal_codes_for:
            Indexes for which extended postal codes should be included in
            the results.
        :paramtype extended_postal_codes_for:
            list[str or ~azure.maps.search.models.PointOfInterestExtendedPostalCodes]
        :keyword list[str] brand_filter:
            A comma-separated list of brand names which could be used to restrict the
            result to specific brands.
        :keyword electric_vehicle_connector_filter:
            A comma-separated list of connector types which could
            be used to restrict the result to Electric Vehicle Station supporting specific connector types.
        :paramtype electric_vehicle_connector_filter:
            list[str or ~azure.maps.search.models.ElectricVehicleConnector]
        :keyword localized_map_view:
            The View parameter (also called the "user region" parameter) allows
            you to show the correct maps for a certain country/region for geopolitically disputed regions.
        :paramtype localized_map_view:
            str or ~azure.maps.search.models.LocalizedMapView
        :keyword operating_hours:
            Hours of operation for a POI (Points of Interest).
        :paramtype operating_hours:
            str or ~azure.maps.search.models.OperatingHoursRange
        :return:
            The results of search.
        :rtype:
            ~azure.maps.search.models.SearchAddressResult
        :raises:
            ~azure.core.exceptions.HttpResponseError
        """
        coordinates = kwargs.pop("coordinates", (0, 0))
        bounding_box = kwargs.pop("bounding_box", BoundingBox())

        result = await self._search_client.search_point_of_interest(
            query,
            lat=coordinates[0],
            lon=coordinates[1],
            btm_right=f"{bounding_box.south}, {bounding_box.east}",
            top_left=f"{bounding_box.north}, {bounding_box.west}",
            **kwargs
        )
        return SearchAddressResult(result.summary, result.results)

    @distributed_trace_async
    async def search_nearby_point_of_interest(
        self,
        coordinates: LatLon,
        **kwargs: Any
    ) -> SearchAddressResult:
        """**Search Nearby Point of Interest **

        If you have a use case for only retrieving POI results around a specific location, the nearby
        search method may be the right choice. This endpoint will only return POI results, and does not
        take in a search query parameter.

        :keyword int top:
            Maximum number of responses that will be returned. Default: 10, minimum: 1 and
            maximum: 100.
        :keyword int skip:
            Starting offset of the returned results within the full result set. Default: 0,
            minimum: 0 and maximum: 1900.
        :keyword list[int] category_filter:
            A comma-separated list of category set IDs which could be used to
            restrict the result to specific Points of Interest categories. ID order does not matter.
        :keyword list[str] country_filter:
            Comma separated string of country codes, e.g. FR,ES. This will limit the
            search to the specified countries.
        :param coordinates:
            The applicable coordinates as (lat, lon)
        :type coordinates:
            LatLon
        :keyword int radius_in_meters:
            The radius in meters to for the results to be constrained to the
            defined area, Min value is 1, Max Value is 50000.
        :keyword str language:
            Language in which search results should be returned. Should be one of
            supported IETF language tags, case insensitive.
        :keyword extended_postal_codes_for:
            Indexes for which extended postal codes should be included in
            the results.
        :paramtype extended_postal_codes_for:
            list[str or ~azure.maps.search.models.SearchIndexes]
        :keyword list[str] brand_filter:
            A comma-separated list of brand names which could be used to restrict the
            result to specific brands. Item order does not matter.
        :keyword electric_vehicle_connector_filter:
            A comma-separated list of connector types which could
            be used to restrict the result to Electric Vehicle Station supporting specific connector types.
        :paramtype electric_vehicle_connector_filter:
            list[str or ~azure.maps.search.models.ElectricVehicleConnector]
        :keyword localized_map_view:
            The View parameter (also called the "user region" parameter) allows
            you to show the correct maps for a certain country/region for geopolitically disputed regions.
        :paramtype localized_map_view:
            str or ~azure.maps.search.models.LocalizedMapView
        :return:
            The results of search.
        :rtype:
            ~azure.maps.search.models.SearchAddressResult
        :raises:
            ~azure.core.exceptions.HttpResponseError
        """

        result = await self._search_client.search_nearby_point_of_interest(
            lat=coordinates[0],
            lon=coordinates[1],
            **kwargs
        )
        return SearchAddressResult(result.summary, result.results)


    @distributed_trace_async
    async def search_point_of_interest_category(
        self,
        query: str,
        **kwargs: Any
    ) -> SearchAddressResult:
        """**Get POI by Category**

        Points of Interest (POI) Category Search allows you to request POI results from given category.
        Search allows to query POIs from one category at a time.  Endpoint will only return POI results
        which are categorized as specified.  Response includes POI details such as address, coordinate
        location and classification.

        :param query:
            The POI category to search for (e.g., "AIRPORT", "RESTAURANT"), must be properly URL encoded.
        :type query:
            str
        :keyword bool is_type_ahead:
            Boolean. If the typeahead flag is set, the query will be interpreted as a
            partial input and the search will enter predictive mode.
        :keyword int top:
            Maximum number of responses that will be returned. Default: 10, minimum: 1 and maximum: 100.
        :keyword int skip:
            Starting offset of the returned results within the full result set. Default: 0,
            minimum: 0 and maximum: 1900.
        :keyword LatLon coordinates:
            coordinates as (lat, lon)
        :keyword list[int] category_filter:
            A comma-separated list of category set IDs which could be used to
            restrict the result to specific Points of Interest categories.
        :keyword country_filter:
            Comma separated string of country codes, e.g. FR,ES. This will limit the
            search to the specified countries.
        :paramtype country_filter:
            list[str]
        :keyword int radius_in_meters:
            The radius in meters to for the results to be constrained to the
            defined area.
        :keyword BoundingBox bounding_box:
            north(top), west(left), south(bottom), east(right)
            position of the bounding box as float. E.g. BoundingBox(west=37.553, south=-122.453, east=33.2, north=57)
        :keyword str language:
            Language in which search results should be returned.
        :keyword extended_postal_codes_for:
            Indexes for which extended postal codes should be included in the results.
        :paramtype extended_postal_codes_for:
            list[str or ~azure.maps.search.models.SearchIndexes]
        :keyword list[str] brand_filter:
            A comma-separated list of brand names which could be used to restrict the
            result to specific brands. Item order does not matter.
        :keyword electric_vehicle_connector_filter:
            A comma-separated list of connector types which could
            be used to restrict the result to Electric Vehicle Station supporting specific connector types.
        :paramtype electric_vehicle_connector_filter:
            list[str or ~azure.maps.search.models.ElectricVehicleConnector]
        :keyword localized_map_view:
            The View parameter (also called the "user region" parameter) allows
            you to show the correct maps for a certain country/region for geopolitically disputed regions.
        :paramtype localized_map_view:
            str or ~azure.maps.search.models.LocalizedMapView
        :keyword operating_hours:
            Hours of operation for a POI (Points of Interest). The availability of
            hours of operation will vary based on the data available. If not passed, then no opening hours
            information will be returned.
            Supported value: nextSevenDays.
        :paramtype operating_hours:
            str or ~azure.maps.search.models.OperatingHoursRange
        :return:
            The results of search.
        :rtype:
            ~azure.maps.search.models.SearchAddressResult
        :raises:
            ~azure.core.exceptions.HttpResponseError
        """

        coordinates = kwargs.pop("coordinates", (0, 0))
        bounding_box = kwargs.pop("bounding_box", BoundingBox())

        result = await self._search_client.search_point_of_interest_category(
            query,
            lat=coordinates[0],
            lon=coordinates[1],
            btm_right=f"{bounding_box.south}, {bounding_box.east}",
            top_left=f"{bounding_box.north}, {bounding_box.west}",
            **kwargs
        )
        return SearchAddressResult(result.summary, result.results)

    @distributed_trace_async
    async def search_address(
        self,
        query: str,
        **kwargs: Any
    ) -> SearchAddressResult:
        """**Address Geocoding**

        In many cases, the complete search service might be too much, for instance if you are only
        interested in traditional geocoding. Search can also be accessed for address look up
        exclusively. The geocoding is performed by hitting the geocode endpoint with just the address
        or partial address in question. The geocoding search index will be queried for everything above
        the street level data. No POIs will be returned. Note that the geocoder is very tolerant of
        typos and incomplete addresses. It will also handle everything from exact street addresses or
        street or intersections as well as higher level geographies such as city centers, counties,
        states etc.

        :param query:
            The address to search for (e.g., "1 Microsoft way, Redmond, WA"), must be properly URL encoded.
        :type query:
            str
        :keyword bool is_type_ahead:
            Boolean. If the typeahead flag is set, the query will be interpreted as a
            partial input and the search will enter predictive mode.
        :keyword int top:
            Maximum number of responses that will be returned. Default: 10, minimum: 1 and maximum: 100.
        :keyword int skip:
            Starting offset of the returned results within the full result set. Default: 0,
            minimum: 0 and maximum: 1900.
        :keyword int radius_in_meters:
            The radius in meters to for the results to be constrained to the defined area.
        :keyword LatLon coordinates:
            coordinates as (lat, lon)
        :keyword country_filter:
            Comma separated string of country codes, e.g. FR,ES. This will limit the
            search to the specified countries.
        :paramtype country_filter:
            list[str]
        :keyword BoundingBox bounding_box:
            north(top), west(left), south(bottom), east(right)
            position of the bounding box as float.
            E.g. BoundingBox(west=37.553, south=-122.453, east=33.2, north=57)
        :keyword str language:
            Language in which search results should be returned.
        :keyword extended_postal_codes_for:
            Indexes for which extended postal codes should be included in the results.
        :paramtype extended_postal_codes_for:
            list[str or ~azure.maps.search.models.SearchIndexes]
        :keyword entity_type:
            Specifies the level of filtering performed on geographies.
        :paramtype entity_type:
            str or ~azure.maps.search.models.GeographicEntityType
        :keyword localized_map_view:
            The View parameter (also called the "user region" parameter) allows
            you to show the correct maps for a certain country/region for geopolitically disputed regions.
        :paramtype localized_map_view:
            str or ~azure.maps.search._generated.models.LocalizedMapView
        :return:
            The results of search.
        :rtype:
            ~azure.maps.search.models.SearchAddressResult
        :raises:
            ~azure.core.exceptions.HttpResponseError
        """
        coordinates = kwargs.pop("coordinates", (0, 0))
        bounding_box = kwargs.pop("bounding_box", BoundingBox())

        result = await self._search_client.search_address(
            query,
            lat=coordinates[0],
            lon=coordinates[1],
            btm_right=f"{bounding_box.south}, {bounding_box.east}",
            top_left=f"{bounding_box.north}, {bounding_box.west}",
            **kwargs
        )
        return SearchAddressResult(result.summary, result.results)

    @distributed_trace_async
    async def search_structured_address(
        self,
        structured_address: StructuredAddress,
        **kwargs: Any
    ) -> SearchAddressResult:
        """**Structured Address Geocoding**

        Azure Address Geocoding can also be accessed for structured address look up exclusively. The
        geocoding search index will be queried for everything above the  street level data. No POIs
        will be returned. Note that the geocoder is very tolerant of typos and incomplete  addresses.
        It will also handle everything from exact  street addresses or street or intersections as well
        as higher level geographies such as city centers,  counties, states etc.

        :param structured_address:
            structured address type
        :type structured_address:
            ~azure.maps.search._models.StructuredAddress
        :type top:
            int
        :keyword int skip:
            Starting offset of the returned results within the full result set.
            Default: 0, minimum: 0 and maximum: 1900.
        :keyword extended_postal_codes_for:
            Indexes for which extended postal codes should be included in the results.
        :paramtype extended_postal_codes_for:
            list[str or ~azure.maps.search.models.SearchIndexes]
        :keyword entity_type:
            Specifies the level of filtering performed on geographies.
        :paramtype entity_type:
            str or ~azure.maps.search.models.GeographicEntityType
        :keyword localized_map_view:
            The View parameter (also called the "user region" parameter) allows you to show
            the correct maps for a certain country/region for geopolitically disputed regions.
        :paramtype localized_map_view:
            str or ~azure.maps.search.models.LocalizedMapView
        :return:
            The results of search.
        :rtype:
            ~azure.maps.search.models.SearchAddressResult
        :raises:
            ~azure.core.exceptions.HttpResponseError
        """
        result = await self._search_client.search_structured_address(
            country_code=structured_address.country_code,
            cross_street=structured_address.cross_street,
            street_number=structured_address.street_number,
            street_name=structured_address.street_name,
            municipality=structured_address.municipality,
            municipality_subdivision=structured_address.municipality_subdivision,
            country_tertiary_subdivision=structured_address.country_tertiary_subdivision,
            country_secondary_subdivision=structured_address.country_secondary_subdivision,
            country_subdivision=structured_address.country_subdivision,
            postal_code=structured_address.postal_code,
            **kwargs)
        return SearchAddressResult(result.summary, result.results)

    @distributed_trace_async
    async def fuzzy_search_batch(
        self,
        search_queries: List[str],
        **kwargs: Any
    ) -> SearchAddressBatchResult:
        """**Search Fuzzy Batch API**

        The Search Address Batch API sends batches of queries to `Search Fuzzy API`.
        You can call Search Address Fuzzy Batch API to run either asynchronously (async) or
        synchronously (sync). The async API allows caller to batch up to **10,000** queries and sync
        API up to **100** queries.

        :param search_queries:
            The list of search fuzzy queries/requests to process. The list can
            contain a max of 10,000 queries and must contain at least 1 query.
        :type search_queries:
            List[str]
        :return:
            The results of search batch request.
        :rtype:
            ~azure.maps.search.models.SearchAddressBatchResult
        :raises:
            ~azure.core.exceptions.HttpResponseError
        """
        batch_items = [{"query": f"?query={query}"} for query in search_queries] if search_queries else []

        batch_response = await self._search_client.fuzzy_search_batch_sync(
            batch_request={"batch_items": batch_items},
            **kwargs
        )

        result = SearchAddressBatchResult(
            batch_response.batch_summary, batch_response.batch_items
        )
        return result

    @overload
    async def begin_fuzzy_search_batch(
        self,
        search_queries: List[str],
        **kwargs: Any
    )-> AsyncLROPoller[SearchAddressBatchResult]:
        pass

    @overload
    async def begin_fuzzy_search_batch(
        self,
        batch_id: str,
        **kwargs: Any
    ) -> AsyncLROPoller[SearchAddressBatchResult]:
        pass

    @distributed_trace_async
    async def begin_fuzzy_search_batch(
        self,
        **kwargs: Any
    ) -> AsyncLROPoller[SearchAddressBatchResult]:
        """**Begin Search Fuzzy Batch API Request**

        Sends batches of fuzzy search requests.
        The method returns a poller for retrieving the result later.

        The Search Address Batch API sends batches of queries to `Search Fuzzy API` using just a single API
        call. You can call Search Address Fuzzy Batch API to run either asynchronously (async) or
        synchronously (sync). The async API allows caller to batch up to **10,000** queries and sync
        API up to **100** queries.

        :keyword search_queries:
            The list of search fuzzy queries/requests to process.
            The list can contain a max of 10,000 queries and must contain at least 1 query.
        :paramtype search_queries:
            List[str]
        :keyword str batch_id:
            Batch id for querying the operation.
        :return:
            The results of search batch request.
        :rtype:
            ~azure.core.polling.AsyncLROPoller[~azure.maps.search.models.SearchAddressBatchResult]
        :raises:
            ~azure.core.exceptions.HttpResponseError:
        """
        batch_id = kwargs.pop("batch_id", None)
        search_queries = kwargs.pop("search_queries", None)

        if batch_id:
            return await self._search_client.begin_get_fuzzy_search_batch(
                batch_id=batch_id,
                **kwargs
            )

        batch_items = [{"query": f"?query={query}"} for query in search_queries] if search_queries else []
        batch_poller = await self._search_client.begin_fuzzy_search_batch(
            batch_request={"batch_items": batch_items},
            **kwargs
        )

        batch_poller.batch_id = get_batch_id_from_poller(batch_poller.polling_method())
        return batch_poller


    @distributed_trace_async
    async def search_address_batch(
        self,
        search_queries: List[str],
        **kwargs: Any
    ) -> SearchAddressBatchResult:
        """**Search Address Batch API**

        :param search_queries:
            The list of search fuzzy queries/requests to process. The list can
            contain  a max of 10,000 queries and must contain at least 1 query.
        :type search_queries:
            List[str]
        :return:
            The results of search batch request.
        :rtype:
            ~azure.maps.search.models.SearchAddressBatchResult
        :raises:
            ~azure.core.exceptions.HttpResponseError:
        """
        batch_items = [{"query": f"?query={query}"} for query in search_queries] if search_queries else []

        batch_response = await self._search_client.search_address_batch_sync(
            batch_request={"batch_items": batch_items},
            **kwargs
        )

        result = SearchAddressBatchResult(
            batch_response.batch_summary, batch_response.batch_items
        )
        return result


    @overload
    async def begin_search_address_batch(
        self,
        search_queries: List[str],
        **kwargs: Any
    ) -> AsyncLROPoller[SearchAddressBatchResult]:
        pass

    @overload
    async def begin_search_address_batch(
        self,
        batch_id: str,
        **kwargs: Any
    ) -> AsyncLROPoller[SearchAddressBatchResult]:
        pass

    @distributed_trace_async
    async def begin_search_address_batch(
        self,
        **kwargs  # type: Any
    ):
        # type: (...) -> AsyncLROPoller["SearchAddressBatchResult"]
        """**Begin Search Address Batch API**

        Sends batches of geocoding requests.
        The method returns a poller for retrieving the result later.

        The Search Address Batch API sends batches of queries to `Search Address API` using just a single API
        call. You can call Search Address Batch API to run either asynchronously (async) or
        synchronously (sync). The async API allows caller to batch up to **10,000** queries and sync
        API up to **100** queries.

        :keyword search_queries:
            The list of search fuzzy queries/requests to process.
            The list can contain a max of 10,000 queries and must contain at least 1 query.
        :paramtype search_queries:
            List[str]
        :keyword str batch_id:
            Batch id for querying the operation.
        :return:
            The results of search batch request.
        :rtype:
            ~azure.core.polling.AsyncLROPoller[~azure.maps.search.models.SearchAddressBatchResult]
        :raises:
            ~azure.core.exceptions.HttpResponseError:
        """
        batch_id = kwargs.pop("batch_id", None)
        search_queries = kwargs.pop("search_queries", None)

        if batch_id:
            return await self._search_client.begin_get_search_address_batch(
                batch_id=batch_id,
                **kwargs
            )

        batch_items = [{"query": f"?query={query}"} for query in search_queries] if search_queries else []
        batch_poller = await self._search_client.begin_search_address_batch(
            batch_request={"batch_items": batch_items},
            polling=True,
            **kwargs
        )

        batch_poller.batch_id = get_batch_id_from_poller(batch_poller.polling_method())
        return batch_poller


    @distributed_trace_async
    async def reverse_search_address_batch(
        self,
        search_queries: List[str],
        **kwargs: Any
    ) -> ReverseSearchAddressBatchProcessResult:
        """**Search Address Reverse Batch API**

        The Search Address Batch API sends batches of queries to `Search Address Reverse API`.
        You can call Search Address Reverse Batch API to run either asynchronously (async) or
        synchronously (sync). The async API allows caller to batch up to **10,000** queries and sync
        API up to **100** queries.

        :param search_queries: The list of search fuzzy queries/requests to process.
            The list can contain a max of 10,000 queries and must contain at least 1 query.
        :type search_queries:
            List[str]
        :return:
            The results of search batch request.
        :rtype:
            ~azure.maps.search.models.ReverseSearchAddressBatchProcessResult
        :raises:
            ~azure.core.exceptions.HttpResponseError:
        """
        batch_items = [{"query": f"?query={query}"} for query in search_queries] if search_queries else []

        batch_result = await self._search_client.reverse_search_address_batch_sync(
            batch_request={"batch_items": batch_items},
            **kwargs
        )
        result = ReverseSearchAddressBatchProcessResult(
            batch_result.batch_summary, batch_result.batch_items
        )
        return result



    @overload
    async def begin_reverse_search_address_batch(
        self,
        search_queries: List[str],
        **kwargs: Any
    ) -> AsyncLROPoller[SearchAddressBatchResult]:
        pass

    @overload
    async def begin_reverse_search_address_batch(
        self,
        batch_id: str,
        **kwargs: Any
    ) -> AsyncLROPoller[SearchAddressBatchResult]:
        pass

    @distributed_trace_async
    async def begin_reverse_search_address_batch(
        self,
        **kwargs: Any
    ) -> AsyncLROPoller[ReverseSearchAddressBatchProcessResult]:
        """*Begin Search Address Reverse Batch API Request**

        Sends batches of reverse geocoding requests.
        The method returns a poller for retrieving the result later.

        The Search Address Batch API sends batches of queries to `Search Address Reverse API`.
        You can call Search Address Reverse Batch API to run either asynchronously (async) or
        synchronously (sync). The async API allows caller to batch up to **10,000** queries and sync
        API up to **100** queries.

        :keyword search_queries: The list of search fuzzy queries/requests to process.
            The list can contain a max of 10,000 queries and must contain at least 1 query.
        :paramtype search_queries:
            List[str]
        :keyword str batch_id:
            Batch id for querying the operation.
        :return:
            The results of reverse search batch request.
        :paramtype:
            ~azure.core.polling.AsyncLROPoller[~azure.maps.search.models.ReverseSearchAddressBatchProcessResult]
        :raises:
            ~azure.core.exceptions.HttpResponseError:
        """
        batch_id = kwargs.pop("batch_id", None)
        search_queries = kwargs.pop("search_queries", None)

        if batch_id:
            return await self._search_client.begin_get_reverse_search_address_batch(
                batch_id=batch_id,
                **kwargs
            )

        batch_items = [{"query": f"?query={query}"} for query in search_queries] if search_queries else []
        batch_poller = await self._search_client.begin_reverse_search_address_batch(
            batch_request={"batch_items": batch_items},
            polling=True,
            **kwargs
        )

        batch_poller.batch_id = get_batch_id_from_poller(batch_poller.polling_method())
        return batch_poller

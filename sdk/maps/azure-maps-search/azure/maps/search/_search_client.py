# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

# pylint: disable=unused-import,ungrouped-imports
from typing import TYPE_CHECKING, overload, Union, Any, List, Optional
from azure.core.tracing.decorator import distributed_trace
from azure.core.polling import LROPoller
from ._generated._search_client import SearchClient as SearchClientGen
from ._generated.models import (
    PointOfInterestCategory,
    ReverseSearchCrossStreetAddressResult,
    SearchAlongRouteRequest,
    GeoJsonObject,
    BatchRequest,
    SearchAddressBatchResult,
    Polygon,
)
from .models import (
    LatLon,
    StructuredAddress,
    SearchAddressResult,
    ReverseSearchAddressResult,
    ReverseSearchAddressBatchProcessResult,
)
if TYPE_CHECKING:
    from azure.core.credentials import TokenCredential



class SearchClient(object):
    """Azure Maps Search REST APIs.
    :param credential: Credential needed for the client to connect to Azure.
    :type credential: ~azure.core.credentials.TokenCredential
    """

    def __init__(
        self,
        credential,  # type: TokenCredential
        api_version=None, # type: Optional[str]
        **kwargs  # type: Any
    ):
        # type: (...) -> None

        if not credential:
            raise ValueError(
                "You need to provide account shared key to authenticate.")

        self._search_client = SearchClientGen(
            credential,
            api_version=api_version,
            **kwargs
        ).search

    @distributed_trace
    def get_geometries(
        self,
        geometry_ids,  # type: List[str]
        **kwargs  # type: Any
    ):
        # type: (...) -> List[Polygon]
        """**Get Polygon**
        `Reference Document <https://docs.microsoft.com/en-us/rest/api/maps/search/get-search-polygon>`_.

        :param geometry_ids: Comma separated list of geometry UUIDs, previously retrieved from an
         Online Search request.
        :type geometry_ids: list[str]
        :return: List[Polygon], or the result of cls(response)
        """
        polygon_result = self._search_client.list_polygons(
            geometry_ids,
            **kwargs
        )
        result = [] if not polygon_result else polygon_result.polygons
        return result

    @overload
    def fuzzy_search(
        self,
        query,  # type: str
        *,
        coordinates,  # type: Union[str, LatLon]
        **kwargs  # type: Any
    ):
        # type: (...) -> "SearchAddressResult"
        """
        :param query: The applicable query string (e.g., "seattle", "pizza"). Can *also* be specified
         as a comma separated string composed by latitude followed by longitude (e.g., "47.641268,
         -122.125679"). Must be properly URL encoded.
        :type query: str
        :param coordinates: coordinates
        :type coordinates: ~azure.maps.search._models.LatLon
        """

    @overload
    def fuzzy_search(
        self,
        query,  # type: str
        *,
        country_filter,  # type Optional[list[str]]
        **kwargs  # type: Any
    ):
        # type: (...) -> "SearchAddressResult"
        """
        :param query: The applicable query string (e.g., "seattle", "pizza"). Can *also* be specified
         as a comma separated string composed by latitude followed by longitude (e.g., "47.641268,
         -122.125679"). Must be properly URL encoded.
        :type query: str
         :param country_filter: Comma separated string of country codes, e.g. FR,ES. This will limit the
         search to the specified countries.
        :type country_filter: list[str]
        """

    @distributed_trace
    def fuzzy_search(
        self,
        query,  # type: str
        **kwargs  # type: Any
    ):
        # type: (...) -> "SearchAddressResult"
        """**Free Form Search**
        `Reference Document <https://docs.microsoft.com/en-us/rest/api/maps/search/get-search-fuzzy>`_.

        :param query: The applicable query string (e.g., "seattle", "pizza"). Can *also* be specified
         as a comma separated string composed by latitude followed by longitude (e.g., "47.641268,
         -122.125679"). Must be properly URL encoded.
        :type query: str
        :keyword str is_type_ahead: Boolean. If the typeahead flag is set, the query will be interpreted as a
         partial input and the search will enter predictive mode.
        :keyword str top: Maximum number of responses that will be returned. Default: 10, minimum: 1 and
         maximum: 100.
        :keyword int skip: Starting offset of the returned results within the full result set. Default: 0,
         minimum: 0 and maximum: 1900.
        :keyword list[int] category_filter: A comma-separated list of category set IDs which could be used to
         restrict the result to specific Points of Interest categories. ID order does not matter. When
         multiple category identifiers are provided, only POIs that belong to (at least) one of the
         categories from the provided list will be returned. The list of supported categories can be
         discovered using  `POI Categories API <https://aka.ms/AzureMapsPOICategoryTree>`_.
        :param country_filter: Comma separated string of country codes, e.g. FR,ES. This will limit the
         search to the specified countries.
        :type country_filter: list[str]
        :param coordinates: coordinates
        :type coordinates: ~azure.maps.search._models.LatLon
        :keyword int radius_in_meters: The radius in meters to for the results to be constrained to the
         defined area.
        :param top_left: Top left position of the bounding box. E.g. 37.553,-122.453.
        :type top_left: BoundingBox
        :param btm_right: Bottom right position of the bounding box. E.g. 37.553,-122.453.
        :type btm_right: BoundingBox
        :keyword str language: Language in which search results should be returned. Should be one of
         supported IETF language tags, case insensitive. When data in specified language is not
         available for a specific field, default language is used.
        :keyword  extended_postal_codes_for: Indexes for which extended postal codes should be included in
         the results.
        :paramtype extended_postal_codes_for: list[str or ~azure.maps.search.models.SearchIndexes]
        :keyword int min_fuzzy_level: Minimum fuzziness level to be used. Default: 1, minimum: 1 and maximum:
         4
        :keyword int max_fuzzy_level: Maximum fuzziness level to be used. Default: 2, minimum: 1 and maximum:
         4
        :keyword index_filter: A comma separated list of indexes which should be utilized for the search.
         Item order does not matter.
        :paramtype index_filter: list[str or ~azure.maps.search.models.SearchIndexes]
        :keyword list[str] brand_filter: A comma-separated list of brand names which could be used to restrict the
         result to specific brands. Item order does not matter. When multiple brands are provided, only
         results that belong to (at least) one of the provided list will be returned. Brands that
         contain a "," in their name should be put into quotes.
        :keyword electric_vehicle_connector_filter: A comma-separated list of connector types which could
         be used to restrict the result to Electric Vehicle Station supporting specific connector types.
         Item order does not matter. When multiple connector types are provided, only results that
         belong to (at least) one of the provided list will be returned.
        :paramtype electric_vehicle_connector_filter: list[str or ~azure.maps.search.models.ElectricVehicleConnector]
        :keyword entity_type: Specifies the level of filtering performed on geographies. Narrows the
         search for specified geography entity types, e.g. return only municipality. The resulting
         response will contain the geography ID as well as the entity type matched. If you provide more
         than one entity as a comma separated list, endpoint will return the 'smallest entity
         available'.
        :paramtype entity_type: str or ~azure.maps.search.models.GeographicEntityType
        :keyword localized_map_view: The View parameter (also called the "user region" parameter) allows
         you to show the correct maps for a certain country/region for geopolitically disputed regions.
         Different countries have different views of such regions, and the View parameter allows your
         application to comply with the view required by the country your application will be serving.
         By default, the View parameter is set to “Unified” even if you haven’t defined it in  the
         request. It is your responsibility to determine the location of your users, and then set the
         View parameter correctly for that location. Alternatively, you have the option to set
         ‘View=Auto’, which will return the map data based on the IP  address of the request.
        :paramtype localized_map_view: str or ~azure.maps.search.models.LocalizedMapView
        :keyword operating_hours: Hours of operation for a POI (Points of Interest). The availability of
         hours of operation will vary based on the data available. If not passed, then no opening hours
         information will be returned.
         Supported value: nextSevenDays.
        :paramtype operating_hours: str or ~azure.maps.search.models.OperatingHoursRange
        :return: SearchAddressResult, or the result of cls(response)
        :raises: ~azure.core.exceptions.HttpResponseError
        """

        coordinates = kwargs.get("coordinates", None)
        country_filter = kwargs.get("country_filter", None)

        if not coordinates or not country_filter:
            raise TypeError(
                'at least "coordinates" or "country_filter" is required')

        return self._search_client.fuzzy_search(
            query,
            lat=coordinates.lat,
            lon=coordinates.lon,
            country_filter=country_filter,
            **kwargs
        )

    @distributed_trace
    def get_point_of_interest_categories(
        self,
        **kwargs  # type: Any
    ):
        # type: (...) -> List[PointOfInterestCategory]
        """**Get POI Category Tree**
        `Reference Document
         <https://docs.microsoft.com/en-us/rest/api/maps/search/get-search-poi-category-tree-preview>`_.

        :keyword str language: Language in which search results should be returned. Should be one of
         supported IETF language tags, except NGT and NGT-Latn. Language tag is case insensitive. When
         data in specified language is not available for a specific field, default language is used
         (English).
        :return: List[PointOfInterestCategory], or the result of cls(response)
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        result = self._search_client.get_point_of_interest_category_tree(
            **kwargs
        )
        return result.categories

    @distributed_trace
    def reverse_search_address(
        self,
        coordinates,  # type: Union[str, LatLon]
        **kwargs  # type: Any
    ):
        # type: (...) -> "ReverseSearchAddressResult"
        """**Search Address Reverse Batch API**
        `Reference Document
         <https://docs.microsoft.com/en-us/rest/api/maps/search/post-search-address-reverse-batch>`_.

        :param coordinates: The applicable coordinates
        :type coordinates: ~azure.maps.search._models.LatLon
        :param language: Language in which search results should be returned.
        :type language: str
        :keyword bool include_speed_limit: Boolean. To enable return of the posted speed limit.
        :keyword int heading: The directional heading of the vehicle in degrees, for travel along a segment
         of roadway.
        :keyword int radius_in_meters: The radius in meters to for the results to be constrained to the
         defined area.
        :keyword str number: If a number is sent in along with the request, the response may include the side
         of the street (Left/Right) and also an offset position for that number.
        :keyword bool include_road_use: Boolean. To enable return of the road use array for reverse geocodes
         at street level.
        :keyword road_use: To restrict reverse geocodes to a certain type of road use.
        :paramtype road_use: list[str or ~azure.maps.search.models.RoadUseType]
        :keyword bool allow_freeform_newline: Format of newlines in the formatted address.
        :keyword bool include_match_type: Include information on the type of match the geocoder achieved in
         the response.
        :keyword entity_type: Specifies the level of filtering performed on geographies.
        :paramtype entity_type: str or ~azure.maps.search.models.GeographicEntityType
        :keyword localized_map_view: The View parameter (also called the "user region" parameter) allows
         you to show the correct maps for a certain country/region for geopolitically disputed regions.
        :paramtype localized_map_view: str or ~azure.maps.search.models.LocalizedMapView
        :return: ReverseSearchAddressResult, or the result of cls(response)
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        result = self._search_client.reverse_search_address(
            query=[coordinates.lat, coordinates.lat]
            ** kwargs
        )
        return ReverseSearchAddressResult(summary=result.summary, results=result.addresses)

    @distributed_trace
    def reverse_search_cross_street_address(
        self,
        coordinates,  # type: Union[str, LatLon]
        **kwargs  # type: Any
    ):
        # type: (...) -> "ReverseSearchCrossStreetAddressResult"
        """**Reverse Geocode to a Cross Street**
        `Reference Document
         <https://docs.microsoft.com/en-us/rest/api/maps/search/get-search-address-reverse-cross-street>`_.

        :param coordinates: The applicable coordinates
        :type coordinates: ~azure.maps.search._models.LatLon
        :keyword int top: Maximum number of responses that will be returned. Default: 10, minimum: 1 and
         maximum: 100.
        :keyword int heading: The directional heading of the vehicle in degrees, for travel along a segment
         of roadway. 0 is North, 90 is East and so on, values range from -360 to 360. The precision can
         include up to one decimal place.
        :keyword int radius_in_meters: The radius in meters to for the results to be constrained to the
         defined area.
        :keyword str language: Language in which search results should be returned. Should be one of
         supported IETF language tags, case insensitive. When data in specified language is not
         available for a specific field, default language is used.
        :keyword localized_map_view: The View parameter (also called the "user region" parameter) allows
         you to show the correct maps for a certain country/region for geopolitically disputed regions.
         Different countries have different views of such regions, and the View parameter allows your
         application to comply with the view required by the country your application will be serving.
         By default, the View parameter is set to “Unified” even if you haven’t defined it in  the
         request. It is your responsibility to determine the location of your users, and then set the
         View parameter correctly for that location. Alternatively, you have the option to set
         ‘View=Auto’, which will return the map data based on the IP  address of the request.
        :paramtype localized_map_view: str or ~azure.maps.search.models.LocalizedMapView
        :return: ReverseSearchCrossStreetAddressResult, or the result of cls(response)
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        return self._search_client.reverse_search_cross_street_address(
            [coordinates.lat, coordinates.lat],
            **kwargs
        )

    @distributed_trace
    def search_along_route(
        self,
        query,  # type: str
        max_detour_time,  # type: int
        route,  # type: "SearchAlongRouteRequest"
        **kwargs  # type: Any
    ):
        # type: (...) -> "SearchAddressResult"
        """
        The Search Along Route endpoint allows you to perform a fuzzy search for POIs along a specified
        route.
        `Reference Document <https://docs.microsoft.com/en-us/rest/api/maps/search/post-search-along-route>`_

        :param query: The POI name to search for (e.g., "statue of liberty", "starbucks", "pizza").
         Must be properly URL encoded.
        :type query: str
        :param max_detour_time: Maximum detour time of the point of interest in seconds. Max value is
         3600 seconds.
        :type max_detour_time: int
        :param route: This represents the route to search along and should be a valid ``GeoJSON
         LineString`` type. Please refer to `RFC 7946
         <https://tools.ietf.org/html/rfc7946#section-3.1.4>`_ for details.
        :type route: ~azure.maps.search.models.SearchAlongRouteRequest
        :keyword int top: Maximum number of responses that will be returned. Default value is 10. Max value
         is 20.
        :keyword list[str] brand_filter: A comma-separated list of brand names which could be used to restrict the
         result to specific brands. Item order does not matter. When multiple brands are provided, only
         results that belong to (at least) one of the provided list will be returned. Brands that
         contain a "," in their name should be put into quotes.
        :keyword list[int] category_filter: A comma-separated list of category set IDs which could be used to
         restrict the result to specific Points of Interest categories. ID order does not matter. When
         multiple category identifiers are provided, only POIs that belong to (at least) one of the
         categories from the provided list will be returned. The list of supported categories can be
         discovered using  `POI Categories API <https://aka.ms/AzureMapsPOICategoryTree>`_.
        :keyword electric_vehicle_connector_filter: A comma-separated list of connector types which could
         be used to restrict the result to Electric Vehicle Station supporting specific connector types.
         Item order does not matter. When multiple connector types are provided, only results that
         belong to (at least) one of the provided list will be returned.
        :paramtype electric_vehicle_connector_filter: list[str or ~azure.maps.search.models.ElectricVehicleConnector]
        :keyword localized_map_view: The View parameter (also called the "user region" parameter) allows
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
        :paramtype localized_map_view: str or ~azure.maps.search.models.LocalizedMapView
        :keyword operating_hours: Hours of operation for a POI (Points of Interest). The availability of
         hours of operation will vary based on the data available. If not passed, then no opening hours
         information will be returned.
         Supported value: nextSevenDays.
        :paramtype operating_hours: str or ~azure.maps.search.models.OperatingHoursRange
        :return: SearchAddressResult, or the result of cls(response)
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        result = self._search_client.search_along_route(
            query,
            max_detour_time,
            route,
            **kwargs
        )
        return SearchAddressResult(summary=result.summary, results=result.results)

    @distributed_trace
    def search_inside_geometry(
        self,
        query,  # type: str
        geometry,  # type: "GeoJsonObject"
        **kwargs  # type: Any
    ):
        # type: (...) -> "SearchAddressResult"
        """
        The Search Geometry endpoint allows you to perform a free form search inside a single geometry
        or many of them.
        `Reference Document <>`_

        :param query: The POI name to search for (e.g., "statue of liberty", "starbucks", "pizza").
         Must be properly URL encoded.
        :type query: str
        :param geometry: This represents the geometry for one or more geographical features (parks,
         state boundary etc.) to search in and should be a GeoJSON compliant type. Please refer to `RFC
         7946 <https://tools.ietf.org/html/rfc7946>`_ for details.
        :type geometry: ~azure.maps.search.models.SearchInsideGeometryRequest
        :keyword int top: Maximum number of responses that will be returned. Default: 10, minimum: 1 and
         maximum: 100.
        :keyword str language: Language in which search results should be returned. Should be one of
         supported IETF language tags, case insensitive. When data in specified language is not
         available for a specific field, default language is used.
        :keyword list[int] category_filter: A comma-separated list of category set IDs which could be used to
         restrict the result to specific Points of Interest categories. ID order does not matter. When
         multiple category identifiers are provided, only POIs that belong to (at least) one of the
         categories from the provided list will be returned. The list of supported categories can be
         discovered using  `POI Categories API <https://aka.ms/AzureMapsPOICategoryTree>`_.
        :keyword extended_postal_codes_for: Indexes for which extended postal codes should be included in
         the results.
        :paramtype extended_postal_codes_for: list[str or ~azure.maps.search.models.SearchIndexes]
        :keyword index_filter: A comma separated list of indexes which should be utilized for the search.
         Item order does not matter.
        :paramtype index_filter: list[str or ~azure.maps.search.models.SearchIndexes]
        :keyword localized_map_view: The View parameter (also called the "user region" parameter) allows
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
        :paramtype localized_map_view: str or ~azure.maps.search.models.LocalizedMapView
        :keyword operating_hours: Hours of operation for a POI (Points of Interest). The availability of
         hours of operation will vary based on the data available. If not passed, then no opening hours
         information will be returned.
         Supported value: nextSevenDays.
        :paramtype operating_hours: str or ~azure.maps.search.models.OperatingHoursRange
        :return: SearchAddressResult, or the result of cls(response)
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        result = self._search_client.search_inside_geometry(
            query,
            geometry,
            **kwargs
        )
        return SearchAddressResult(result.summary, result.results)

    @overload
    def search_point_of_interest(
        self,
        query,  # type: str
        coordinates,  # type: Union[str, LatLon]
        **kwargs  # type: Any
    ):
        # type: (...) -> "SearchAddressResult"
        """**Get POI by Name**
        `Reference Document <https://docs.microsoft.com/en-us/rest/api/maps/search/get-search-poi-category>`_

        Points of Interest (POI) Search allows you to request POI results by name.  Search supports
        additional query parameters such as language and filtering results by area of interest driven
        by country or bounding box.  Endpoint will return only POI results matching the query string.
        Response includes POI details such as address, coordinate location and category.

        :param query: The POI name to search for (e.g., "statue of liberty", "starbucks"), must be
         properly URL encoded.
        :type query: str
        :param coordinates: coordinates
        :type coordinates: ~azure.maps.search._models.LatLon
        :return: SearchAddressResult, or the result of cls(response)
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        coordinates = LatLon() if not coordinates else coordinates

        result = self._search_client.search_point_of_interest(
            query,
            lat=coordinates.lat,
            lon=coordinates.lon,
            **kwargs
        )
        return SearchAddressResult(result.summary, result.results)

    @overload
    def search_point_of_interest(
        self,
        query,  # type: str
        country_filter,  # type list[str]
        **kwargs  # type: Any
    ):
        # type: (...) -> "SearchAddressResult"
        """**Get POI by Name**
        `Reference Document <https://docs.microsoft.com/en-us/rest/api/maps/search/get-search-poi-category>`_

        Points of Interest (POI) Search allows you to request POI results by name.  Search supports
        additional query parameters such as language and filtering results by area of interest driven
        by country or bounding box.  Endpoint will return only POI results matching the query string.
        Response includes POI details such as address, coordinate location and category.

        :param query: The POI name to search for (e.g., "statue of liberty", "starbucks"), must be
         properly URL encoded.
        :type query: str
        :keyword list[int] category_filter: A comma-separated list of category set IDs which could be used to
         restrict the result to specific Points of Interest categories.
        :keyword list[int] country_filter: Comma separated string of country codes, e.g. FR,ES. This will limit the
        :return: SearchAddressResult, or the result of cls(response)
        :raises: ~azure.core.exceptions.HttpResponseError
        """

        result = self._search_client.search_point_of_interest(
            query,
            country_filter=country_filter,
            **kwargs
        )
        return SearchAddressResult(result.summary, result.results)

    @distributed_trace
    def search_point_of_interest(
        self,
        query,  # type: str
        **kwargs  # type: Any
    ):
        # type: (...) -> "SearchAddressResult"
        """**Get POI by Name**
        `Reference Document <https://docs.microsoft.com/en-us/rest/api/maps/search/get-search-poi-category>`_

        Points of Interest (POI) Search allows you to request POI results by name.  Search supports
        additional query parameters such as language and filtering results by area of interest driven
        by country or bounding box.  Endpoint will return only POI results matching the query string.
        Response includes POI details such as address, coordinate location and category.

        :param query: The POI name to search for (e.g., "statue of liberty", "starbucks"), must be
         properly URL encoded.
        :type query: str
        :keyword bool is_type_ahead: Boolean. If the typeahead flag is set, the query will be interpreted as a
         partial input and the search will enter predictive mode.
        :keyword int top: Maximum number of responses that will be returned. Default: 10, minimum: 1 and
         maximum: 100.
        :keyword int skip: Starting offset of the returned results within the full result set. Default: 0,
         minimum: 0 and maximum: 1900.
        :keyword list[int] category_filter: A comma-separated list of category set IDs which could be used to
         restrict the result to specific Points of Interest categories.
        :keyword list[int] country_filter: Comma separated string of country codes, e.g. FR,ES. This will limit the
         search to the specified countries.
        :param coordinates: coordinates
        :type coordinates: ~azure.maps.search._models.LatLon
        :keyword int radius_in_meters: The radius in meters to for the results to be constrained to the
         defined area.
        :param top_left: Top left position of the bounding box. E.g. 37.553,-122.453.
        :type top_left: str
        :param btm_right: Bottom right position of the bounding box. E.g. 37.553,-122.453.
        :type btm_right: str
        :keyword str language: Language in which search results should be returned.
        :keyword extended_postal_codes_for: Indexes for which extended postal codes should be included in
         the results.
        :paramtype extended_postal_codes_for: list[str or ~azure.maps.search.models.PointOfInterestExtendedPostalCodes]
        :keyword list[str] brand_filter: A comma-separated list of brand names which could be used to restrict the
         result to specific brands.
        :keyword electric_vehicle_connector_filter: A comma-separated list of connector types which could
         be used to restrict the result to Electric Vehicle Station supporting specific connector types.
        :paramtype electric_vehicle_connector_filter: list[str or ~azure.maps.search.models.ElectricVehicleConnector]
        :keyword localized_map_view: The View parameter (also called the "user region" parameter) allows
         you to show the correct maps for a certain country/region for geopolitically disputed regions.
        :paramtype localized_map_view: str or ~azure.maps.search.models.LocalizedMapView
        :keyword operating_hours: Hours of operation for a POI (Points of Interest).
        :paramtype operating_hours: str or ~azure.maps.search.models.OperatingHoursRange
        :return: SearchAddressResult, or the result of cls(response)
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        coordinates = kwargs.get("coordinates", None)
        country_filter = kwargs.get("country_filter", None)

        if not coordinates or not country_filter:
            raise TypeError(
                'at least "coordinates" or "country_filter" is required')

        coordinates = LatLon() if not coordinates else coordinates

        result = self._search_client.search_point_of_interest(
            query,
            lat=coordinates.lat,
            lon=coordinates.lon,
            country_filter=country_filter,
            **kwargs
        )
        return SearchAddressResult(result.summary, result.results)

    @distributed_trace
    def search_nearby_point_of_interest(
        self,
        coordinates,  # type: Union[str, LatLon]
        **kwargs  # type: Any
    ):
        # type: (...) -> "SearchAddressResult"
        """**Search Nearby Point of Interest **
        Please refer to
         `Document <https://docs.microsoft.com/en-us/rest/api/maps/search/get-search-nearby>`_ for details.

        :keyword int top: Maximum number of responses that will be returned. Default: 10, minimum: 1 and
         maximum: 100.
        :keyword int skip: Starting offset of the returned results within the full result set. Default: 0,
         minimum: 0 and maximum: 1900.
        :keyword list[int] category_filter: A comma-separated list of category set IDs which could be used to
         restrict the result to specific Points of Interest categories. ID order does not matter.
        :keyword list[str] country_filter: Comma separated string of country codes, e.g. FR,ES. This will limit the
         search to the specified countries.
        :param coordinates: The applicable coordinates
        :type coordinates: ~azure.maps.search._models.LatLon
        :keyword int radius_in_meters: The radius in meters to for the results to be constrained to the
         defined area, Min value is 1, Max Value is 50000.
        :keyword str language: Language in which search results should be returned. Should be one of
         supported IETF language tags, case insensitive.
        :keyword extended_postal_codes_for: Indexes for which extended postal codes should be included in
         the results.
        :paramtype extended_postal_codes_for: list[str or ~azure.maps.search.models.SearchIndexes]
        :keyword list[str] brand_filter: A comma-separated list of brand names which could be used to restrict the
         result to specific brands. Item order does not matter.
        :keyword electric_vehicle_connector_filter: A comma-separated list of connector types which could
         be used to restrict the result to Electric Vehicle Station supporting specific connector types.
        :paramtype electric_vehicle_connector_filter: list[str or ~azure.maps.search.models.ElectricVehicleConnector]
        :keyword localized_map_view: The View parameter (also called the "user region" parameter) allows
         you to show the correct maps for a certain country/region for geopolitically disputed regions.
        :paramtype localized_map_view: str or ~azure.maps.search.models.LocalizedMapView
        :return: SearchAddressResult, or the result of cls(response)
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        coordinates = LatLon() if not coordinates else coordinates

        result = self._search_client.search_nearby_point_of_interest(
            lat=coordinates.lat,
            lon=coordinates.lon,
            **kwargs
        )
        return SearchAddressResult(result.summary, result.results)

    @overload
    def search_point_of_interest_category(
        self,
        query,  # type: str
        *,
        coordinates,  # type: Union[str, LatLon]
        **kwargs  # type: Any
    ):
        # type: (...) -> "SearchAddressResult"
        """
        :param query: The applicable query string (e.g., "seattle", "pizza"). Can *also* be specified
         as a comma separated string composed by latitude followed by longitude (e.g., "47.641268,
         -122.125679"). Must be properly URL encoded.
        :type query: str
        :param coordinates: coordinates
        :type coordinates: ~azure.maps.search._models.LatLon
        """

    @overload
    def search_point_of_interest_category(
        self,
        query,  # type: str
        *,
        country_filter,  # type Optional[list[str]]
        **kwargs  # type: Any
    ):
        # type: (...) -> "SearchAddressResult"
        """
        :param query: The applicable query string (e.g., "seattle", "pizza"). Can *also* be specified
         as a comma separated string composed by latitude followed by longitude (e.g., "47.641268,
         -122.125679"). Must be properly URL encoded.
        :type query: str
         :param country_filter: Comma separated string of country codes, e.g. FR,ES. This will limit the
         search to the specified countries.
        :type country_filter: list[str]
        """

    @distributed_trace
    def search_point_of_interest_category(
        self,
        query,  # type: str
        **kwargs  # type: Any
    ):
        # type: (...) -> "SearchAddressResult"
        """**Get POI by Category**

        Points of Interest (POI) Category Search allows you to request POI results from given category.
        Search allows to query POIs from one category at a time.  Endpoint will only return POI results
        which are categorized as specified.  Response includes POI details such as address, coordinate
        location and classification.

        :param query: The POI category to search for (e.g., "AIRPORT", "RESTAURANT"), must be properly
         URL encoded.
        :type query: str
        :keyword bool is_type_ahead: Boolean. If the typeahead flag is set, the query will be interpreted as a
         partial input and the search will enter predictive mode.
        :keyword int top: Maximum number of responses that will be returned. Default: 10, minimum: 1 and
         maximum: 100.
        :keyword int skip: Starting offset of the returned results within the full result set. Default: 0,
         minimum: 0 and maximum: 1900.
        :param coordinates: The applicable coordinates
        :type coordinates: ~azure.maps.search._models.LatLon
        :keyword list[int] category_filter: A comma-separated list of category set IDs which could be used to
         restrict the result to specific Points of Interest categories.
        :param country_filter: Comma separated string of country codes, e.g. FR,ES. This will limit the
         search to the specified countries.
        :type country_filter: list[str]
        :keyword int radius_in_meters: The radius in meters to for the results to be constrained to the
         defined area.
        :param top_left: Top left position of the bounding box. E.g. 37.553,-122.453.
        :type top_left: str
        :param btm_right: Bottom right position of the bounding box. E.g. 37.553,-122.453.
        :type btm_right: str
        :keyword str language: Language in which search results should be returned.
        :keyword extended_postal_codes_for: Indexes for which extended postal codes should be included in
         the results.
        :paramtype extended_postal_codes_for: list[str or ~azure.maps.search.models.SearchIndexes]
        :keyword list[str] brand_filter: A comma-separated list of brand names which could be used to restrict the
         result to specific brands. Item order does not matter.
        :keyword electric_vehicle_connector_filter: A comma-separated list of connector types which could
         be used to restrict the result to Electric Vehicle Station supporting specific connector types.
        :paramtype electric_vehicle_connector_filter: list[str or ~azure.maps.search.models.ElectricVehicleConnector]
        :keyword localized_map_view: The View parameter (also called the "user region" parameter) allows
         you to show the correct maps for a certain country/region for geopolitically disputed regions.
        :paramtype localized_map_view: str or ~azure.maps.search.models.LocalizedMapView
        :keyword operating_hours: Hours of operation for a POI (Points of Interest). The availability of
         hours of operation will vary based on the data available. If not passed, then no opening hours
         information will be returned.
         Supported value: nextSevenDays.
        :paramtype operating_hours: str or ~azure.maps.search.models.OperatingHoursRange
        :return: SearchAddressResult, or the result of cls(response)
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        coordinates = kwargs.get("coordinates", None)
        country_filter = kwargs.get("country_filter", None)

        if not coordinates or not country_filter:
            raise TypeError(
                'at least "coordinates" or "country_filter" is required')

        coordinates = LatLon() if not coordinates else coordinates

        result = self._search_client.search_point_of_interest_category(
            query,
            lat=coordinates.lat,
            lon=coordinates.lon,
            country_filter=country_filter,
            **kwargs
        )
        return SearchAddressResult(result.summary, result.results)

    @distributed_trace
    def search_address(
        self,
        query,  # type: str
        coordinates=None,  # type: "LatLon"
        **kwargs  # type: Any
    ):
        # type: (...) -> "SearchAddressResult"
        """**Address Geocoding**

        In many cases, the complete search service might be too much, for instance if you are only
        interested in traditional geocoding. Search can also be accessed for address look up
        exclusively. The geocoding is performed by hitting the geocode endpoint with just the address
        or partial address in question. The geocoding search index will be queried for everything above
        the street level data. No POIs will be returned. Note that the geocoder is very tolerant of
        typos and incomplete addresses. It will also handle everything from exact street addresses or
        street or intersections as well as higher level geographies such as city centers, counties,
        states etc.

        :param query: The address to search for (e.g., "1 Microsoft way, Redmond, WA"), must be
         properly URL encoded.
        :type query: str
        :keyword bool is_type_ahead: Boolean. If the typeahead flag is set, the query will be interpreted as a
         partial input and the search will enter predictive mode.
        :keyword int top: Maximum number of responses that will be returned. Default: 10, minimum: 1 and
         maximum: 100.
        :keyword int skip: Starting offset of the returned results within the full result set. Default: 0,
         minimum: 0 and maximum: 1900.
        :keyword list[str] country_filter: Comma separated string of country codes, e.g. FR,ES. This will limit the
         search to the specified countries.
        :param coordinates: The applicable coordinates
        :type coordinates: ~azure.maps.search._models.LatLon
        :keyword int radius_in_meters: The radius in meters to for the results to be constrained to the
         defined area.
        :param top_left: Top left position of the bounding box. E.g. 37.553,-122.453.
        :type top_left: str
        :param btm_right: Bottom right position of the bounding box. E.g. 37.553,-122.453.
        :type btm_right: str
        :keyword str language: Language in which search results should be returned.
        :keyword extended_postal_codes_for: Indexes for which extended postal codes should be included in
         the results.
        :paramtype extended_postal_codes_for: list[str or ~azure.maps.search.models.SearchIndexes]
        :keyword entity_type: Specifies the level of filtering performed on geographies.
        :paramtype entity_type: str or ~azure.maps.search.models.GeographicEntityType
        :keyword localized_map_view: The View parameter (also called the "user region" parameter) allows
         you to show the correct maps for a certain country/region for geopolitically disputed regions.
        :paramtype localized_map_view: str or ~azure.maps.search._generated.models.LocalizedMapView
        :return: SearchAddressResult, or the result of cls(response)
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        coordinates = LatLon() if not coordinates else coordinates

        result = self._search_client.search_address(
            query,
            lat=coordinates.lat,
            lon=coordinates.lon,
            **kwargs
        )
        return SearchAddressResult(result.summary, result.results)

    @distributed_trace
    def search_structured_address(
        self,
        structured_address,  # type: "StructuredAddress"
        **kwargs  # type: Any
    ):
        # type: (...) -> "SearchAddressResult"
        """**Structured Address Geocoding**

        Azure Address Geocoding can also be accessed for structured address look up exclusively. The
        geocoding search index will be queried for everything above the  street level data. No POIs
        will be returned. Note that the geocoder is very tolerant of typos and incomplete  addresses.
        It will also handle everything from exact  street addresses or street or intersections as well
        as higher level geographies such as city centers,  counties, states etc.
        :param structured_address: structured address type
        :type structured_address: ~azure.maps.search._models.StructuredAddress
        :type top: int
        :keyword int skip: Starting offset of the returned results within the full result set. Default: 0,
         minimum: 0 and maximum: 1900.
        :keyword extended_postal_codes_for: Indexes for which extended postal codes should be included in
         the results.
        :paramtype extended_postal_codes_for: list[str or ~azure.maps.search.models.SearchIndexes]
        :keyword entity_type: Specifies the level of filtering performed on geographies.
        :paramtype entity_type: str or ~azure.maps.search.models.GeographicEntityType
        :keyword localized_map_view: The View parameter (also called the "user region" parameter) allows
         you to show the correct maps for a certain country/region for geopolitically disputed regions.
        :paramtype localized_map_view: str or ~azure.maps.search.models.LocalizedMapView
        :return: SearchAddressResult, or the result of cls(response)
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        result = self._search_client.search_structured_address(
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

    @distributed_trace
    def fuzzy_search_batch_sync(
        self,
        batch_request,  # type: "BatchRequest"
        **kwargs  # type: Any
    ):
        # type: (...) -> "SearchAddressBatchResult"
        """**Search Fuzzy Batch API**

        The Search Address Batch API sends batches of queries to `Search Fuzzy API
        <https://docs.microsoft.com/rest/api/maps/search/getsearchfuzzy>`_ using just a single API
        call. You can call Search Address Fuzzy Batch API to run either asynchronously (async) or
        synchronously (sync). The async API allows caller to batch up to **10,000** queries and sync
        API up to **100** queries.

        :param batch_request: The list of search fuzzy queries/requests to process. The list can
         contain  a max of 10,000 queries and must contain at least 1 query.
        :type batch_request: ~azure.maps.search._generated.models.BatchRequest
        :return: SearchAddressBatchResult, or the result of cls(response)
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        return self._search_client.fuzzy_search_batch_sync(
            batch_request,
            **kwargs
        )

    @distributed_trace
    def search_address_batch_sync(
        self,
        batch_request,  # type: "BatchRequest"
        **kwargs  # type: Any
    ):
        # type: (...) -> "SearchAddressBatchResult"
        """**Search Address Batch API**

        :param batch_request: The list of address geocoding queries/requests to process. The list can
         contain  a max of 10,000 queries and must contain at least 1 query.
        :type batch_request: ~azure.maps.search._generated.models.BatchRequest
        :return: SearchAddressBatchResult, or the result of cls(response)
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        return self._search_client.search_address_batch_sync(
            batch_request,
            **kwargs
        )

    @distributed_trace
    def reverse_search_address_batch_sync(
        self,
        batch_request,  # type: "BatchRequest"
        **kwargs  # type: Any
    ):
        # type: (...) -> "ReverseSearchAddressBatchProcessResult"
        """**Search Address Reverse Batch API**

        **Applies to**\\ : S1 pricing tier.

        The Search Address Batch API sends batches of queries to `Search Address Reverse API
        <https://docs.microsoft.com/rest/api/maps/search/getsearchaddressreverse>`_ using just a single
        API call. You can call Search Address Reverse Batch API to run either asynchronously (async) or
        synchronously (sync). The async API allows caller to batch up to **10,000** queries and sync
        API up to **100** queries.
        :param batch_request: The list of reverse geocoding queries/requests to process. The list can
         contain  a max of 10,000 queries and must contain at least 1 query.
        :type batch_request: ~azure.maps.search._generated.models.BatchRequest
        :return: ReverseSearchAddressBatchProcessResult, or the result of cls(response)
        :raises: ~azure.core.exceptions.HttpResponseError
        """

        batch_result = self._search_client.reverse_search_address_batch_sync(
            batch_request,
            **kwargs
        )
        result = ReverseSearchAddressBatchProcessResult(
            batch_result.batch_summary, batch_result.batch_items
        )
        return result

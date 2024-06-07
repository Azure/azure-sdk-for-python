# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from typing import Optional, List, Union
from azure.maps.search._generated.models import ResultType

class LatLon:
    """Represents coordinate latitude and longitude

    :keyword lat: The coordinate as latitude.
    :paramtype lat: float
    :keyword lon: The coordinate as longitude.
    :paramtype lon: float
    """
    def __init__(self, lat: float = 0.0, lon: float = 0.0):
        self.lat = lat
        self.lon = lon

class BoundingBox:
    """Represents information about the coordinate range

    :keyword west: The westmost value of coordinates.
    :paramtype west: float
    :keyword south: The southmost value of coordinates.
    :paramtype south: float
    :keyword east: The eastmost value of coordinates.
    :paramtype east: float
    :keyword north: The northmost value of coordinates.
    :paramtype north: float
    """
    def __init__(self, west: float = 0.0, south: float = 0.0, east: float = 0.0, north: float = 0.0):
        self.west = west
        self.south = south
        self.east = east
        self.north = north

# pylint: disable=too-many-instance-attributes
class GeocodingBatchRequestItem:
    """Batch Query object.

    :keyword optional_id: id of the request which would show in corresponding batchItem.
    :paramtype optional_id: str
    :keyword top: Maximum number of responses that will be returned. Default: 5, minimum: 1 and
     maximum: 20.
    :paramtype top: int
    :keyword query: A string that contains information about a location, such as an address or
     landmark name.
    :paramtype query: str
    :keyword address_line: The official street line of an address relative to the area, as specified
     by the locality, or postalCode, properties. Typical use of this element would be to provide a
     street address or any official address.

     **If query is given, should not use this parameter.**.
    :paramtype address_line: str
    :keyword country_region: Signal for the geocoding result to an `ISO 3166-1 Alpha-2 region/country
     code <https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2>`_ that is specified e.g. FR./

     **If query is given, should not use this parameter.**.
    :paramtype country_region: str
    :keyword bounding_box: A rectangular area on the earth defined as a bounding box object. The sides of the
     rectangles are defined by longitude and latitude values. For more information, see Location and
     Area Types. When you specify this parameter, the geographical area is taken into account when
     computing the results of a location query.

     Example: BoundingBox(west=37.553, south=-122.453, east=33.2, north=57).
    :paramtype bounding_box: BoundingBox
    :keyword localized_map_view: A string that specifies an `ISO 3166-1 Alpha-2 region/country code
     <https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2>`_. This will alter Geopolitical disputed
     borders and labels to align with the specified user region.
    :paramtype localized_map_view: str or ~azure.maps.search.models.LocalizedMapView
    :keyword coordinates: A point on the earth specified as a longitude and latitude. When you specify
     this parameter, the user’s location is taken into account and the results returned may be more
     relevant to the user. Example: LatLon(lat, lon).
    :paramtype coordinates: LatLon
    :keyword admin_district: The country subdivision portion of an address, such as WA.

     **If query is given, should not use this parameter.**.
    :paramtype admin_district: str
    :keyword admin_district2: The county for the structured address, such as King.

     **If query is given, should not use this parameter.**.
    :paramtype admin_district2: str
    :keyword admin_district3: The named area for the structured address.

     **If query is given, should not use this parameter.**.
    :paramtype admin_district3: str
    :keyword locality: The locality portion of an address, such as Seattle.

     **If query is given, should not use this parameter.**.
    :paramtype locality: str
    :keyword postal_code: The postal code portion of an address.

     **If query is given, should not use this parameter.**.
    :paramtype postal_code: str
    """
    def __init__(self,
                 optional_id: Optional[str] = None,
                 top: int = 5,
                 query: Optional[str] = None,
                 address_line: Optional[str] = None,
                 country_region: Optional[str] = None,
                 bounding_box: Optional[BoundingBox] = None,
                 localized_map_view: str = "auto",
                 coordinates: Optional[LatLon] = None,
                 admin_district: Optional[str] = None,
                 admin_district2: Optional[str] = None,
                 admin_district3: Optional[str] = None,
                 locality: Optional[str] = None,
                 postal_code: Optional[str] = None):
        self.optional_id = optional_id
        self.top = top
        self.query = query
        self.address_line = address_line
        self.country_region = country_region
        self.bounding_box = bounding_box
        self.localized_map_view = localized_map_view
        self.coordinates = coordinates
        self.admin_district = admin_district
        self.admin_district2 = admin_district2
        self.admin_district3 = admin_district3
        self.locality = locality
        self.postal_code = postal_code

class GeocodingBatchRequestBody:
    """The list of address geocoding queries/requests to process. The list can contain a max of 100
    queries and must contain at least 1 query.

    :keyword batch_items: The list of queries to process.
    :paramtype batch_items: list[~azure.maps.search.models.GeocodingBatchRequestItem]
    """
    def __init__(self, batch_items: Optional[List[GeocodingBatchRequestItem]] = None):
        self.batch_items = batch_items

class ReverseGeocodingBatchRequestItem:
    """Batch Query object.

    :keyword optional_id: id of the request which would show in corresponding batchItem.
    :paramtype optional_id: str
    :keyword coordinates: The coordinates of the location that you want to reverse geocode. Example:
     LatLon(lat, lon).
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
    :paramtype result_types: list[str or ~azure.maps.search.models.ResultType]
    :keyword localized_map_view: A string that specifies an `ISO 3166-1 Alpha-2 region/country code
     <https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2>`_. This will alter Geopolitical disputed
     borders and labels to align with the specified user region.
    :paramtype localized_map_view: str or ~azure.maps.search.models.LocalizedMapView
    """
    def __init__(self,
                 optional_id: Optional[str] = None,
                 coordinates: Optional[LatLon] = None,
                 result_types: Optional[List[Union[str, ResultType]]] = None,
                 localized_map_view: Optional[str] = None):
        self.optional_id = optional_id
        self.coordinates = coordinates
        self.result_types = result_types
        self.localized_map_view = localized_map_view

class ReverseGeocodingBatchRequestBody:
    """The list of reverse geocoding queries/requests to process. The list can contain a max of 100
    queries and must contain at least 1 query.

    :keyword batch_items: The list of queries to process.
    :paramtype batch_items: list[~azure.maps.search.models.ReverseGeocodingBatchRequestItem]
    """
    def __init__(self, batch_items: Optional[List[ReverseGeocodingBatchRequestItem]] = None):
        self.batch_items = batch_items

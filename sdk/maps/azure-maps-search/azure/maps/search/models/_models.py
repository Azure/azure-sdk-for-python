# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

# pylint: disable=unused-import,ungrouped-imports, C0302, C0203
from typing import List, Optional, Union
import msrest.serialization

from .._generated.models import (
    PointOfInterest,
    DataSource,
    SearchAlongRouteRequest,
    SearchAddressBatchItem as _SearchAddressBatchItem,
    SearchAddressBatchItemResponse,
    ReverseSearchAddressBatchItem as _ReverseSearchAddressBatchItem,
    BatchResultSummary,
    GeoJsonObjectType
)

class LatLon(object):

    def __init__(
        self,
        lat: float = None,
        lon: float = None
    ):
        self._lat = lat
        self._lon = lon

    @property
    def lat(self) -> float:
        return self._lat

    @lat.setter
    def lat(self, value: float) -> None:
        self._lat = value

    @property
    def lon(self) -> float:
        return self._lon

    @lon.setter
    def lon(self, value: float) -> None:
        self._lon = value


class BoundingBox(object):

    def __init__(
        self,
        top_left: LatLon = LatLon(),
        bottom_right: LatLon = LatLon(),
        top_right: LatLon = LatLon(),
        bottom_left: LatLon = LatLon()
    ):
        self.top_left = top_left
        self.bottom_right = bottom_right
        self.top = top_left.lat
        self.bottom = bottom_right.lat
        self.left = top_left.lon
        self.right = bottom_right.lon
        self.top_right = top_right if top_right else LatLon(
            top_left.lat, bottom_right.lon)
        self.bottom_left = bottom_left if bottom_left else LatLon(
            bottom_right.lat, top_left.lon)


# pylint: disable=too-many-instance-attributes
class StructuredAddress(object):

    def __init__(
        self,
        country_code: str,
        cross_street: Optional[str] = None,
        street_number: Optional[str] = None,
        street_name: Optional[str] = None,
        municipality: Optional[str] = None,
        municipality_subdivision: Optional[str] = None,
        country_tertiary_subdivision: Optional[str] = None,
        country_secondary_subdivision: Optional[str] = None,
        country_subdivision: Optional[str] = None,
        postal_code: Optional[str] = None
    ):
        self._country_code = country_code
        self.cross_street = cross_street
        self.street_number = street_number
        self.street_name = street_name
        self.municipality = municipality
        self.municipality_subdivision = municipality_subdivision
        self.country_tertiary_subdivision = country_tertiary_subdivision
        self.country_secondary_subdivision = country_secondary_subdivision
        self.country_subdivision = country_subdivision
        self.postal_code = postal_code

    @property
    def country_code(self) -> str:
        return self._country_code

    @country_code.setter
    def country_code(self, value: str) -> None:
        self._country_code = value

    @property
    def cross_street(self) -> str:
        return self._cross_street

    @cross_street.setter
    def cross_street(self, value: str) -> None:
        self._cross_street = value

    @property
    def street_number(self) -> str:
        return self._street_number

    @street_number.setter
    def street_number(self, value) -> None:
        self._street_number = value

    @property
    def street_name(self) -> str:
        return self._street_name

    @street_name.setter
    def street_name(self, value: str) -> None:
        self._street_name = value

    @property
    def municipality(self) -> str:
        return self._municipality

    @municipality.setter
    def municipality(self, value: str) -> None:
        self._municipality = value

    @property
    def municipality_subdivision(self) -> str:
        return self._municipality_subdivision

    @municipality_subdivision.setter
    def municipality_subdivision(self, value: str) -> None:
        self._municipality_subdivision = value

    @property
    def country_tertiary_subdivision(self) -> str:
        return self._country_tertiary_subdivision

    @country_tertiary_subdivision.setter
    def country_tertiary_subdivision(self, value: str) -> None:
        self._country_tertiary_subdivision = value

    @property
    def country_secondary_subdivision(self) -> str:
        return self._country_secondary_subdivision

    @country_secondary_subdivision.setter
    def country_secondary_subdivision(self, value: str) -> None:
        self._country_secondary_subdivision = value

    @property
    def country_subdivision(self) -> str:
        return self._country_subdivision

    @country_subdivision.setter
    def country_subdivision(self, value: str) -> None:
        self._country_subdivision = value

    @property
    def postal_code(self) -> str:
        return self._postal_code

    @postal_code.setter
    def postal_code(self, value: str) -> None:
        self._postal_code = value


class SearchSummary(object):

    def __init__(
        self,
        query: str = None,
        query_type: str = None,
        query_time: int = None,
        num_results: int = None,
        top: int = None,
        skip: int = None,
        total_results: int = None,
        fuzzy_level: int = None,
        geo_bias: LatLon = None
    ):
        self.query = query
        self.query_type = query_type
        self.query_time = query_time
        self.num_results = num_results
        self.top = top
        self.skip = skip
        self.total_results = total_results
        self.fuzzy_level = fuzzy_level
        self.geo_bias = geo_bias


class AddressRanges(object):
    def __init__(
        self,
        range_left: str = None,
        range_right: str = None,
        from_property: LatLon = None,
        to_: LatLon = None
    ):
        self.range_left = range_left
        self.range_right = range_right
        self.from_property = LatLon() if not from_property else LatLon(
            from_property.lat, from_property.lon
        )
        self.to = LatLon() if not to_ else LatLon(
            to_.lat, to_.lon
        )


class EntryPoint(object):
    def __init__(
        self,
        type_: str = None,
        position: LatLon = None
    ):
        self.type = type_
        self.position = LatLon() if not position else LatLon(
            position.lat, position.lon
        )


# pylint: disable=too-many-instance-attributes
class Address(object):

    def __init__(
        self,
        building_number: str,
        street: str,
        cross_street: str = None,
        street_number: str = None,
        route_numbers: List[int] = None,
        street_name: str = None,
        street_name_and_number: str = None,
        municipality: str = None,
        municipality_subdivision: str = None,
        country_tertiary_subdivision: str = None,
        country_secondary_subdivision: str = None,
        country_subdivision: str = None,
        postal_code: str = None,
        extended_postal_code: str = None,
        country_code: str = None,
        country: str = None,
        country_code_iso3: str = None,
        freeform_address: str = None,
        country_subdivision_name: str = None,
        local_name: str = None,
        bounding_box: BoundingBox = None,
    ):
        self.building_number = building_number
        self.street = street
        self.cross_street = cross_street
        self.street_number = street_number
        self.route_numbers = route_numbers
        self.street_name = street_name
        self.street_name_and_number = street_name_and_number
        self.municipality = municipality
        self.municipality_subdivision = municipality_subdivision
        self.country_tertiary_subdivision = country_tertiary_subdivision
        self.country_secondary_subdivision = country_secondary_subdivision
        self.country_subdivision = country_subdivision
        self.postal_code = postal_code
        self.extended_postal_code = extended_postal_code
        self.country_code = country_code
        self.country = country
        self.country_code_iso3 = country_code_iso3
        self.freeform_address = freeform_address
        self.country_subdivision_name = country_subdivision_name
        self.local_name = local_name
        self.bounding_box = bounding_box


# pylint: disable=too-many-instance-attributes
class SearchAddressResultItem(object):

    def __init__(
        self,
        type_: str = None,
        id_: str = None,
        score: float = None,
        distance_in_meters: float = None,
        info: str = None,
        entity_type: str = None,
        point_of_interest: PointOfInterest = None,
        address: Address = None,
        position: LatLon = None,
        viewport: BoundingBox = None,
        entry_points: EntryPoint = None,
        address_ranges: AddressRanges = None,
        data_sources: DataSource = None,
        match_type: str = None,
        detour_time: int = None
    ):
        self.type = type_
        self.id = id_
        self.score = score
        self.distance_in_meters = distance_in_meters
        self.info = info
        self.entity_type = entity_type
        self.point_of_interest = point_of_interest
        self.address = address
        self.position = LatLon() if not position else LatLon(
            position.lat, position.lon
        )
        self.viewport = viewport
        self.entry_points = entry_points
        self.address_ranges = LatLon() if not position else LatLon(
            address_ranges.range_left, address_ranges.range_right
        )
        self.data_sources = data_sources
        self.match_type = match_type
        self.detour_time = detour_time


class SearchAddressResult(object):
    """This object is returned from a successful Search calls.

    Variables are only populated by the server, and will be ignored when sending a request.

    :keyword summary: Summary object for a Search API response.
    :paramtype summary: ~azure.maps.search.models.SearchSummary
    :keyword results: A list of Search API results.
    :paramtype results: list[~azure.maps.search.models.SearchAddressResultItem]
    """

    def __init__(
        self,
        summary: SearchSummary = None,
        results: List[SearchAddressResultItem] = None
    ):
        self.query = summary.query
        self.query_type = summary.query_type
        self.query_time = summary.query_time
        self.num_results = summary.num_results
        self.top = summary.top
        self.skip = summary.skip
        self.total_results = summary.total_results
        self.fuzzy_level = summary.fuzzy_level
        self.geo_bias = LatLon() if not summary.geo_bias else LatLon(
            summary.geo_bias.lat, summary.geo_bias.lon
        )
        self.results = results


class ReverseSearchAddressResultItem(object):
    """Result object for a Search Address Reverse response.

    Variables are only populated by the server, and will be ignored when sending a request.

    :keyword address: The address of the result.
    :paramtype address: ~azure.maps.search.models.Address
    :keyword position: Position property in the form of "latitude,longitude".
    :paramtype position: LatLon
    :keyword road_use:
    :paramtype road_use: list[str]
    :keyword match_type: Information on the type of match.
    :paramtype match_type: str or ~azure.maps.search.models.MatchType
    """

    def __init__(
        self,
        address: Address = None,
        position: LatLon = None,
        road_use: List[str] = None,
        match_type: str = None
    ):
        self.address = address
        self.position = LatLon() if not position else LatLon(
            float(position.split(',')[0]), float(position.split(',')[1])
        )
        self.road_use = road_use
        self.match_type = match_type


class ReverseSearchAddressResult(object):
    """This object is returned from a successful Search Address Reverse call.

    Variables are only populated by the server, and will be ignored when sending a request.

    :keyword summary: Summary object for a Search Address Reverse response.
    :paramtype summary: ~azure.maps.search.models.SearchSummary
    :keyword results: Addresses array.
    :paramtype results: list[~azure.maps.search.models.ReverseSearchAddressResultItem]
    """

    def __init__(
        self,
        summary: SearchSummary = None,
        results: List[ReverseSearchAddressResultItem] = None
    ):
        self.query_type = summary.query_type
        self.query_time = summary.query_time
        self.results = results


class ReverseSearchAddressBatchItem(_ReverseSearchAddressBatchItem):
    """An item returned from Search Address Reverse Batch service call.

    Variables are only populated by the server, and will be ignored when sending a request.

    :keyword response: The result of the query. SearchAddressReverseResponse if the query completed
     successfully, ErrorResponse otherwise.
    :paramtype response: ~azure.maps.search.models.ReverseSearchAddressBatchItemResponse
    """

    def __init__(
        self,
        **kwargs
    ):
        super(ReverseSearchAddressBatchItem, self).__init__(**kwargs)
        self.response = None


class ReverseSearchAddressBatchProcessResult(object):
    """This object is returned from a successful Search Address Reverse Batch service call.

    Variables are only populated by the server, and will be ignored when sending a request.

    :keyword summary: Summary of the results for the batch request.
    :paramtype summary: ~azure.maps.search._generated.models.BatchResultSummary
    :keyword items: Array containing the batch results.
    :paramtype items: list[ReverseSearchAddressBatchItem]
    """

    def __init__(
        self,
        summary: BatchResultSummary = None,
        items: List[ReverseSearchAddressBatchItem] = None
    ):
        self.summary = summary
        self.items = items

class GeoJsonObject(msrest.serialization.Model):
    """A valid ``GeoJSON`` object.
    Please refer to `RFC 7946 <https://tools.ietf.org/html/rfc7946#section-3>`_ for details.

    You probably want to use the sub-classes and not this class directly. Known
    sub-classes are: GeoJsonFeature, GeoJsonFeatureCollection, GeoJsonGeometry,
     GeoJsonGeometryCollection, GeoJsonLineString, GeoJsonMultiLineString,
     GeoJsonMultiPoint, GeoJsonMultiPolygon, GeoJsonPoint, GeoJsonPolygon.

    All required parameters must be populated in order to send to Azure.

    :param type: Required. Specifies the ``GeoJSON`` type. Must be one of the nine valid GeoJSON
     object types - Point, MultiPoint, LineString, MultiLineString, Polygon, MultiPolygon,
     GeometryCollection, Feature and FeatureCollection.Constant filled by server.  Possible values
     include: "Point", "MultiPoint", "LineString", "MultiLineString", "Polygon", "MultiPolygon",
     "GeometryCollection", "Feature", "FeatureCollection".
    :type type: str or ~azure.maps.search._generated.models.GeoJsonObjectType
    """

    _validation = {
        'type': {'required': True},
    }

    _attribute_map = {
        'type': {'key': 'type', 'type': 'str'},
    }

    _subtype_map = {
        'type': {'Feature': 'GeoJsonFeature', 'FeatureCollection': 'GeoJsonFeatureCollection',
                 'GeoJsonGeometry': 'GeoJsonGeometry', 'GeometryCollection': 'GeoJsonGeometryCollection',
                 'LineString': 'GeoJsonLineString', 'MultiLineString': 'GeoJsonMultiLineString',
                 'MultiPoint': 'GeoJsonMultiPoint', 'MultiPolygon': 'GeoJsonMultiPolygon',
                 'Point': 'GeoJsonPoint', 'Polygon': 'GeoJsonPolygon'
        }
    }

    def __init__(
        self,
        type_: Union[str, GeoJsonObjectType] = None,
        **kwargs
    ):
        super(GeoJsonObject, self).__init__(**kwargs)
        self.type = type_  # type: Optional[Union[str, GeoJsonObjectType]]

class GeoJsonFeatureData(msrest.serialization.Model):
    """GeoJsonFeatureData.

    All required parameters must be populated in order to send to Azure.

    :param geometry: Required. A valid ``GeoJSON`` object. Please refer to `RFC 7946
     <https://tools.ietf.org/html/rfc7946#section-3>`_ for details.
    :type geometry: ~azure.maps.search.models.GeoJsonObject
    :param properties: Properties can contain any additional metadata about the ``Feature``. Value
     can be any JSON object or a JSON null value.
    :type properties: object
    :param feature_type: The type of the feature. The value depends on the data model the current
     feature is part of. Some data models may have an empty value.
    :type feature_type: str
    """

    _validation = {
        'geometry': {'required': True},
    }

    _attribute_map = {
        'geometry': {'key': 'geometry', 'type': 'GeoJsonObject'},
        'properties': {'key': 'properties', 'type': 'object'},
        'feature_type': {'key': 'featureType', 'type': 'str'},
    }

    def __init__(
        self,
        *,
        geometry: "GeoJsonObject",
        properties: Optional[object] = None,
        feature_type: Optional[str] = None,
        **kwargs
    ):
        super(GeoJsonFeatureData, self).__init__(**kwargs)
        self.geometry = geometry
        self.properties = properties
        self.feature_type = feature_type

class GeoJsonFeature(GeoJsonObject, GeoJsonFeatureData):
    """A valid ``GeoJSON Feature`` object type.
    Please refer to `RFC 7946 <https://tools.ietf.org/html/rfc7946#section-3.2>`_ for details.

    All required parameters must be populated in order to send to Azure.

    :param geometry: Required. A valid ``GeoJSON`` object. Please refer to `RFC 7946
     <https://tools.ietf.org/html/rfc7946#section-3>`_ for details.
    :type geometry: ~azure.maps.search.models.GeoJsonObject
    :param properties: Properties can contain any additional metadata about the ``Feature``. Value
     can be any JSON object or a JSON null value.
    :type properties: object
    :param feature_type: The type of the feature. The value depends on the data model the current
     feature is part of. Some data models may have an empty value.
    :type feature_type: str
    :param type: Required. Specifies the ``GeoJSON`` type. Must be one of the nine valid GeoJSON
     object types - Point, MultiPoint, LineString, MultiLineString, Polygon, MultiPolygon,
     GeometryCollection, Feature and FeatureCollection.Constant filled by server.  Possible values
     include: "Point", "MultiPoint", "LineString", "MultiLineString", "Polygon", "MultiPolygon",
     "GeometryCollection", "Feature", "FeatureCollection".
    :type type: str or ~azure.maps.search._generated.models.GeoJsonObjectType
    """

    def __init__(
        self,
        *,
        geometry: GeoJsonObject,
        properties: Optional[object] = None,
        feature_type: Optional[str] = None,
        **kwargs
    ):
        super(GeoJsonFeature, self).__init__(
            geometry=geometry, properties=properties, feature_type=feature_type, **kwargs
        )
        self.geometry = geometry
        self.properties = properties
        self.feature_type = feature_type
        self.type = 'Feature'  # type: str


class GeoJsonFeatureCollectionData(msrest.serialization.Model):
    """GeoJsonFeatureCollectionData.

    All required parameters must be populated in order to send to Azure.

    :param features: Required. Contains a list of valid ``GeoJSON Feature`` objects.
    :type features: list[~azure.maps.search.models.GeoJsonFeature]
    """

    _validation = {
        'features': {'required': True},
    }

    _attribute_map = {
        'features': {'key': 'features', 'type': '[GeoJsonFeature]'},
    }

    def __init__(
        self,
        *,
        features: List["GeoJsonFeature"],
        **kwargs
    ):
        super(GeoJsonFeatureCollectionData, self).__init__(**kwargs)
        self.features = features


class GeoJsonFeatureCollection(GeoJsonObject, GeoJsonFeatureCollectionData):
    """A valid ``GeoJSON FeatureCollection`` object type.
    Please refer to `RFC 7946 <https://tools.ietf.org/html/rfc7946#section-3.3>`_ for details.

    All required parameters must be populated in order to send to Azure.

    :param features: Required. Contains a list of valid ``GeoJSON Feature`` objects.
    :type features: list[~azure.maps.search.models.GeoJsonFeature]
    :param type: Required. Specifies the ``GeoJSON`` type. Must be one of the nine valid GeoJSON
     object types - Point, MultiPoint, LineString, MultiLineString, Polygon, MultiPolygon,
     GeometryCollection, Feature and FeatureCollection.Constant filled by server.  Possible values
     include: "Point", "MultiPoint", "LineString", "MultiLineString", "Polygon", "MultiPolygon",
     "GeometryCollection", "Feature", "FeatureCollection".
    :type type: str or ~azure.maps.search._generated.models.GeoJsonObjectType
    """

    _validation = {
        'features': {'required': True},
        'type': {'required': True},
    }

    _attribute_map = {
        'features': {'key': 'features', 'type': '[GeoJsonFeature]'},
        'type': {'key': 'type', 'type': 'str'},
    }

    def __init__(
        self,
        *,
        features: List["GeoJsonFeature"],
        **kwargs
    ):
        super(GeoJsonFeatureCollection, self).__init__(features=features, **kwargs)
        self.features = features
        self.type = 'FeatureCollection'  # type: str
        self.type = 'FeatureCollection'  # type: str


class GeoJsonGeometry(GeoJsonObject):
    """A valid ``GeoJSON`` geometry object.
    The type must be one of the seven valid GeoJSON geometry types -
    Point, MultiPoint, LineString, MultiLineString, Polygon, MultiPolygon and GeometryCollection.
    Please refer to `RFC 7946 <https://tools.ietf.org/html/rfc7946#section-3.1>`_ for details.

    All required parameters must be populated in order to send to Azure.

    :param type: Required. Specifies the ``GeoJSON`` type. Must be one of the nine valid GeoJSON
     object types - Point, MultiPoint, LineString, MultiLineString, Polygon, MultiPolygon,
     GeometryCollection, Feature and FeatureCollection.Constant filled by server.  Possible values
     include: "Point", "MultiPoint", "LineString", "MultiLineString", "Polygon", "MultiPolygon",
     "GeometryCollection", "Feature", "FeatureCollection".
    :type type: str or ~azure.maps.search._generated.models.GeoJsonObjectType
    """

    _validation = {
        'type': {'required': True},
    }

    _attribute_map = {
        'type': {'key': 'type', 'type': 'str'},
    }

    def __init__(
        self,
        **kwargs
    ):
        super(GeoJsonGeometry, self).__init__(**kwargs)
        self.type = 'GeoJsonGeometry'  # type: str


class GeoJsonGeometryCollectionData(msrest.serialization.Model):
    """GeoJsonGeometryCollectionData.

    All required parameters must be populated in order to send to Azure.

    :param geometries: Required. Contains a list of valid ``GeoJSON`` geometry objects. **Note**
     that coordinates in GeoJSON are in x, y order (longitude, latitude).
    :type geometries: list[~azure.maps.search.models.GeoJsonObject]
    """

    _validation = {
        'geometries': {'required': True},
    }

    _attribute_map = {
        'geometries': {'key': 'geometries', 'type': '[GeoJsonObject]'},
    }

    def __init__(
        self,
        *,
        geometries: List["GeoJsonObject"],
        **kwargs
    ):
        super(GeoJsonGeometryCollectionData, self).__init__(**kwargs)
        self.geometries = geometries


class GeoJsonGeometryCollection(GeoJsonObject, GeoJsonGeometryCollectionData):
    """A valid ``GeoJSON GeometryCollection`` object type.
    Please refer to `RFC 7946 <https://tools.ietf.org/html/rfc7946#section-3.1.8>`_ for details.

    All required parameters must be populated in order to send to Azure.

    :param geometries: Required. Contains a list of valid ``GeoJSON`` geometry objects. **Note**
     that coordinates in GeoJSON are in x, y order (longitude, latitude).
    :type geometries: list[~azure.maps.search.models.GeoJsonObject]
    :param type: Required. Specifies the ``GeoJSON`` type. Must be one of the nine valid GeoJSON
     object types - Point, MultiPoint, LineString, MultiLineString, Polygon, MultiPolygon,
     GeometryCollection, Feature and FeatureCollection.Constant filled by server.  Possible values
     include: "Point", "MultiPoint", "LineString", "MultiLineString", "Polygon", "MultiPolygon",
     "GeometryCollection", "Feature", "FeatureCollection".
    :type type: str or ~azure.maps.search._generated.models.GeoJsonObjectType
    """

    _validation = {
        'geometries': {'required': True},
        'type': {'required': True},
    }

    _attribute_map = {
        'geometries': {'key': 'geometries', 'type': '[GeoJsonObject]'},
        'type': {'key': 'type', 'type': 'str'},
    }

    def __init__(
        self,
        *,
        geometries: List["GeoJsonObject"],
        **kwargs
    ):
        super(GeoJsonGeometryCollection, self).__init__(geometries=geometries, **kwargs)
        self.geometries = geometries
        self.type = 'GeometryCollection'  # type: str
        self.type = 'GeometryCollection'  # type: str


class GeoJsonLineStringData(msrest.serialization.Model):
    """GeoJsonLineStringData.

    All required parameters must be populated in order to send to Azure.

    :param coordinates: Required. Coordinates for the ``GeoJson LineString`` geometry.
    :type coordinates: list[LatLon]
    """

    _validation = {
        'coordinates': {'required': True},
    }

    _attribute_map = {
        'coordinates': {'key': 'coordinates', 'type': '[LatLon]'},
    }

    def __init__(
        self,
        *,
        coordinates: List[LatLon],
        **kwargs
    ):
        super(GeoJsonLineStringData, self).__init__(**kwargs)
        self.coordinates = coordinates

class GeoJsonLineString(GeoJsonObject, GeoJsonLineStringData):
    """A valid ``GeoJSON LineString`` geometry type.
    Please refer to `RFC 7946 <https://tools.ietf.org/html/rfc7946#section-3.1.4>`_ for details.

    All required parameters must be populated in order to send to Azure.

    :param coordinates: Required. Coordinates for the ``GeoJson LineString`` geometry.
    :type coordinates: list[LatLon]
    :param type: Required. Specifies the ``GeoJSON`` type. Must be one of the nine valid GeoJSON
     object types - Point, MultiPoint, LineString, MultiLineString, Polygon, MultiPolygon,
     GeometryCollection, Feature and FeatureCollection.Constant filled by server.  Possible values
     include: "Point", "MultiPoint", "LineString", "MultiLineString", "Polygon", "MultiPolygon",
     "GeometryCollection", "Feature", "FeatureCollection".
    :type type: str or ~azure.maps.search._generated.models.GeoJsonObjectType
    """

    _validation = {
        'coordinates': {'required': True},
        'type': {'required': True},
    }

    _attribute_map = {
        'coordinates': {'key': 'coordinates', 'type': '[LatLon]'},
        'type': {'key': 'type', 'type': 'str'},
    }

    def __init__(
        self,
        *,
        coordinates: List[LatLon],
        **kwargs
    ):
        super(GeoJsonLineString, self).__init__(coordinates=coordinates, **kwargs)
        self.coordinates = coordinates
        self.type = 'LineString'  # type: str
        self.type = 'LineString'  # type: str


class GeoJsonMultiLineStringData(msrest.serialization.Model):
    """GeoJsonMultiLineStringData.

    All required parameters must be populated in order to send to Azure.

    :param coordinates: Required. Coordinates for the ``GeoJson MultiLineString`` geometry.
    :type coordinates: list[list[LatLon]]
    """

    _validation = {
        'coordinates': {'required': True},
    }

    _attribute_map = {
        'coordinates': {'key': 'coordinates', 'type': '[[LatLon]]'},
    }

    def __init__(
        self,
        *,
        coordinates: List[List[LatLon]],
        **kwargs
    ):
        super(GeoJsonMultiLineStringData, self).__init__(**kwargs)
        self.coordinates = coordinates


class GeoJsonMultiLineString(GeoJsonObject, GeoJsonMultiLineStringData):
    """A valid ``GeoJSON MultiLineString`` geometry type.
    Please refer to `RFC 7946 <https://tools.ietf.org/html/rfc7946#section-3.1.5>`_ for details.

    All required parameters must be populated in order to send to Azure.

    :param coordinates: Required. Coordinates for the ``GeoJson MultiLineString`` geometry.
    :type coordinates: list[list[LatLon]]
    :param type: Required. Specifies the ``GeoJSON`` type. Must be one of the nine valid GeoJSON
     object types - Point, MultiPoint, LineString, MultiLineString, Polygon, MultiPolygon,
     GeometryCollection, Feature and FeatureCollection.Constant filled by server.  Possible values
     include: "Point", "MultiPoint", "LineString", "MultiLineString", "Polygon", "MultiPolygon",
     "GeometryCollection", "Feature", "FeatureCollection".
    :type type: str or ~azure.maps.search._generated.models.GeoJsonObjectType
    """

    _validation = {
        'coordinates': {'required': True},
        'type': {'required': True},
    }

    _attribute_map = {
        'coordinates': {'key': 'coordinates', 'type': '[[LatLon]]'},
        'type': {'key': 'type', 'type': 'str'},
    }

    def __init__(
        self,
        *,
        coordinates: List[List[LatLon]],
        **kwargs
    ):
        super(GeoJsonMultiLineString, self).__init__(coordinates=coordinates, **kwargs)
        self.coordinates = coordinates
        self.type = 'MultiLineString'  # type: str
        self.type = 'MultiLineString'  # type: str


class GeoJsonMultiPointData(msrest.serialization.Model):
    """Data contained by a ``GeoJson MultiPoint``.

    All required parameters must be populated in order to send to Azure.

    :param coordinates: Required. Coordinates for the ``GeoJson MultiPoint`` geometry.
    :type coordinates: list[LatLon]
    """

    _validation = {
        'coordinates': {'required': True},
    }

    _attribute_map = {
        'coordinates': {'key': 'coordinates', 'type': '[LatLon]'},
    }

    def __init__(
        self,
        *,
        coordinates: List[LatLon],
        **kwargs
    ):
        super(GeoJsonMultiPointData, self).__init__(**kwargs)
        self.coordinates = coordinates


class GeoJsonMultiPoint(GeoJsonObject, GeoJsonMultiPointData):
    """A valid ``GeoJSON MultiPoint`` geometry type.
    Please refer to `RFC 7946 <https://tools.ietf.org/html/rfc7946#section-3.1.3>`_ for details.

    All required parameters must be populated in order to send to Azure.

    :param coordinates: Required. Coordinates for the ``GeoJson MultiPoint`` geometry.
    :type coordinates: list[LatLon]
    :param type: Required. Specifies the ``GeoJSON`` type. Must be one of the nine valid GeoJSON
     object types - Point, MultiPoint, LineString, MultiLineString, Polygon, MultiPolygon,
     GeometryCollection, Feature and FeatureCollection.Constant filled by server.  Possible values
     include: "Point", "MultiPoint", "LineString", "MultiLineString", "Polygon", "MultiPolygon",
     "GeometryCollection", "Feature", "FeatureCollection".
    :type type: str or ~azure.maps.search._generated.models.GeoJsonObjectType
    """

    _validation = {
        'coordinates': {'required': True},
        'type': {'required': True},
    }

    _attribute_map = {
        'coordinates': {'key': 'coordinates', 'type': '[LatLon]'},
        'type': {'key': 'type', 'type': 'str'},
    }

    def __init__(
        self,
        *,
        coordinates: List[LatLon],
        **kwargs
    ):
        super(GeoJsonMultiPoint, self).__init__(coordinates=coordinates, **kwargs)
        self.coordinates = coordinates
        self.type = 'MultiPoint'  # type: str
        self.type = 'MultiPoint'  # type: str


class GeoJsonMultiPolygonData(msrest.serialization.Model):
    """GeoJsonMultiPolygonData.

    All required parameters must be populated in order to send to Azure.

    :param coordinates: Required. Contains a list of valid ``GeoJSON Polygon`` objects. **Note**
     that coordinates in GeoJSON are in x, y order (longitude, latitude).
    :type coordinates: list[list[list[LatLon]]]
    """

    _validation = {
        'coordinates': {'required': True},
    }

    _attribute_map = {
        'coordinates': {'key': 'coordinates', 'type': '[[[LatLon]]]'},
    }

    def __init__(
        self,
        *,
        coordinates: List[List[List[LatLon]]],
        **kwargs
    ):
        super(GeoJsonMultiPolygonData, self).__init__(**kwargs)
        self.coordinates = coordinates


class GeoJsonMultiPolygon(GeoJsonObject, GeoJsonMultiPolygonData):
    """A valid ``GeoJSON MultiPolygon`` object type.
    Please refer to `RFC 7946 <https://tools.ietf.org/html/rfc7946#section-3.1.7>`_ for details.

    All required parameters must be populated in order to send to Azure.

    :param coordinates: Required. Contains a list of valid ``GeoJSON Polygon`` objects. **Note**
     that coordinates in GeoJSON are in x, y order (longitude, latitude).
    :type coordinates: list[list[list[LatLon]]]
    :param type: Required. Specifies the ``GeoJSON`` type. Must be one of the nine valid GeoJSON
     object types - Point, MultiPoint, LineString, MultiLineString, Polygon, MultiPolygon,
     GeometryCollection, Feature and FeatureCollection.Constant filled by server.  Possible values
     include: "Point", "MultiPoint", "LineString", "MultiLineString", "Polygon", "MultiPolygon",
     "GeometryCollection", "Feature", "FeatureCollection".
    :type type: str or ~azure.maps.search._generated.models.GeoJsonObjectType
    """

    _validation = {
        'coordinates': {'required': True},
        'type': {'required': True},
    }

    _attribute_map = {
        'coordinates': {'key': 'coordinates', 'type': '[[[LatLon]]]'},
        'type': {'key': 'type', 'type': 'str'},
    }

    def __init__(
        self,
        *,
        coordinates: List[List[List[LatLon]]],
        **kwargs
    ):
        super(GeoJsonMultiPolygon, self).__init__(coordinates=coordinates, **kwargs)
        self.coordinates = coordinates
        self.type = 'MultiPolygon'  # type: str
        self.type = 'MultiPolygon'  # type: str


class GeoJsonPointData(msrest.serialization.Model):
    """Data contained by a ``GeoJson Point``.

    All required parameters must be populated in order to send to Azure.

    :param coordinates: Required. A ``Position`` is an array of numbers with two or more elements.
     The first two elements are *longitude* and *latitude*, precisely in that order.
     *Altitude/Elevation* is an optional third element. Please refer to `RFC 7946
     <https://tools.ietf.org/html/rfc7946#section-3.1.1>`_ for details.
    :type coordinates: LatLon
    """

    _validation = {
        'coordinates': {'required': True},
    }

    _attribute_map = {
        'coordinates': {'key': 'coordinates', 'type': 'LatLon'},
    }

    def __init__(
        self,
        *,
        coordinates: LatLon,
        **kwargs
    ):
        super(GeoJsonPointData, self).__init__(**kwargs)
        self.coordinates = coordinates


class GeoJsonPoint(GeoJsonObject, GeoJsonPointData):
    """A valid ``GeoJSON Point`` geometry type.
    Please refer to `RFC 7946 <https://tools.ietf.org/html/rfc7946#section-3.1.2>`_ for details.

    All required parameters must be populated in order to send to Azure.

    :param coordinates: Required. A ``Position`` is an array of numbers with two or more elements.
     The first two elements are *longitude* and *latitude*, precisely in that order.
     *Altitude/Elevation* is an optional third element. Please refer to `RFC 7946
     <https://tools.ietf.org/html/rfc7946#section-3.1.1>`_ for details.
    :type coordinates: LatLon
    :param type: Required. Specifies the ``GeoJSON`` type. Must be one of the nine valid GeoJSON
     object types - Point, MultiPoint, LineString, MultiLineString, Polygon, MultiPolygon,
     GeometryCollection, Feature and FeatureCollection.Constant filled by server.  Possible values
     include: "Point", "MultiPoint", "LineString", "MultiLineString", "Polygon", "MultiPolygon",
     "GeometryCollection", "Feature", "FeatureCollection".
    :type type: str or ~azure.maps.search._models.GeoJsonObjectType
    """

    _validation = {
        'coordinates': {'required': True},
        'type': {'required': True},
    }

    _attribute_map = {
        'coordinates': {'key': 'coordinates', 'type': 'LatLon'},
        'type': {'key': 'type', 'type': 'str'},
    }

    def __init__(
        self,
        *,
        coordinates: LatLon,
        **kwargs
    ):
        super(GeoJsonPoint, self).__init__(coordinates=coordinates, **kwargs)
        self.coordinates = coordinates
        self.type = 'Point'  # type: str
        self.type = 'Point'  # type: str


class GeoJsonPolygonData(msrest.serialization.Model):
    """GeoJsonPolygonData.

    All required parameters must be populated in order to send to Azure.

    :param coordinates: Required. Coordinates for the ``GeoJson Polygon`` geometry type.
    :type coordinates: list[list[LatLon]]
    """

    _validation = {
        'coordinates': {'required': True},
    }

    _attribute_map = {
        'coordinates': {'key': 'coordinates', 'type': '[[LatLon]]'},
    }

    def __init__(
        self,
        *,
        coordinates: List[List[LatLon]],
        **kwargs
    ):
        super(GeoJsonPolygonData, self).__init__(**kwargs)
        self.coordinates = coordinates


class GeoJsonPolygon(GeoJsonObject, GeoJsonPolygonData):
    """A valid ``GeoJSON Polygon`` geometry type.
    Please refer to `RFC 7946 <https://tools.ietf.org/html/rfc7946#section-3.1.6>`_ for details.

    All required parameters must be populated in order to send to Azure.

    :param coordinates: Required. Coordinates for the ``GeoJson Polygon`` geometry type.
    :type coordinates: list[list[LatLon]]
    :param type: Required. Specifies the ``GeoJSON`` type. Must be one of the nine valid GeoJSON
     object types - Point, MultiPoint, LineString, MultiLineString, Polygon, MultiPolygon,
     GeometryCollection, Feature and FeatureCollection.Constant filled by server.  Possible values
     include: "Point", "MultiPoint", "LineString", "MultiLineString", "Polygon", "MultiPolygon",
     "GeometryCollection", "Feature", "FeatureCollection".
    :type type: str or ~azure.maps.search._generated.models.GeoJsonObjectType
    """

    _validation = {
        'coordinates': {'required': True},
        'type': {'required': True},
    }

    _attribute_map = {
        'coordinates': {'key': 'coordinates', 'type': '[[LatLon]]'},
        'type': {'key': 'type', 'type': 'str'},
    }

    def __init__(
        self,
        *,
        coordinates: List[List[LatLon]],
        **kwargs
    ):
        super(GeoJsonPolygon, self).__init__(coordinates=coordinates, **kwargs)
        self.coordinates = coordinates
        self.type = 'Polygon'  # type: str
        self.type = 'Polygon'  # type: str


class SearchAlongRouteOptions(object):
    def __init__(
        self,
        *,
        route: Optional["GeoJsonLineString"] = None,
        **kwargs
    ):
        super(SearchAlongRouteOptions, self).__init__(**kwargs)
        self.route = route


class SearchAddressBatchItem(object):
    """An item returned from Search Address Batch service call.

    Variables are only populated by the server, and will be ignored when sending a request.

    :keyword status_code: HTTP request status code.
    :paramtype status_code: int
    :keyword response: The result of the query. SearchAddressResponse if the query completed
     successfully, ErrorResponse otherwise.
    :paramtype response: ~azure.maps.search.models.SearchAddressBatchItemResponse
    """

    def __init__(
        self,
        response: SearchAddressBatchItemResponse = None,
        **kwargs
    ):
        super(SearchAddressBatchItem, self).__init__(**kwargs)
        self.response = response

class SearchAddressBatchResult(object):
    """This object is returned from a successful Search Address Batch service call.

    Variables are only populated by the server, and will be ignored when sending a request.

    :keyword summary: Summary of the results for the batch request.
    :paramtype summary: ~azure.maps.search._generated.models.BatchResultSummary
    :keyword items: Array containing the batch results.
    :paramtype items: list[~azure.maps.search._generated.models.SearchAddressBatchItem]
    """

    def __init__(
        self,
        summary: BatchResultSummary = None,
        items: List[SearchAddressBatchItem] = None
    ):
        self.summary = summary
        self.items = items

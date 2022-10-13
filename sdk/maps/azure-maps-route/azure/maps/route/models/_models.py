# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

# pylint: disable=unused-import,ungrouped-imports, super-init-not-called
from typing import List, Optional, Union, NamedTuple
from enum import Enum, EnumMeta
from six import with_metaclass
import msrest.serialization

from azure.core import CaseInsensitiveEnumMeta
from .._generated.models import (
    BatchResult as GenBatchResult,
    RouteLeg as GenRouteLeg,
    BatchResultSummary,
    ErrorDetail,
    RouteReport,
    RouteSectionTec
)

class LatLon(NamedTuple):
    """Represents coordinate latitude and longitude

    :keyword lat: The coordinate as latitude.
    :paramtype lat: float
    :keyword lon: The coordinate as longitude.
    :paramtype lon: float
    """
    lat: float = 0
    lon: float = 0

class BoundingBox(NamedTuple):
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
    west: float = 0.0
    south: float = 0.0
    east: float = 0.0
    north: float = 0.0

# cSpell:disable
class RouteSection(object):
    """Route sections contain additional information about parts of a route. Each section contains at least the elements ``startPointIndex``\ , ``endPointIndex``\ , and ``sectionType``.

    Variables are only populated by the server, and will be ignored when sending a request.

    :ivar start_point_index: Index of the first point (offset 0) in the route this section applies
     to.
    :vartype start_point_index: int
    :ivar end_point_index: Index of the last point (offset 0) in the route this section applies to.
    :vartype end_point_index: int
    :ivar section_type: Section types of the reported route response. Known values are:
     "CAR_TRAIN", "COUNTRY", "FERRY", "MOTORWAY", "PEDESTRIAN", "TOLL_ROAD", "TOLL_VIGNETTE",
     "TRAFFIC", "TRAVEL_MODE", "TUNNEL", "CARPOOL", and "URBAN".
    :vartype section_type: str or ~azure.maps.route.models.SectionType
    :ivar travel_mode: Travel mode for the calculated route. The value will be set to ``other`` if
     the requested mode of transport is not possible in this section. Known values are: "car",
     "truck", "taxi", "bus", "van", "motorcycle", "bicycle", "pedestrian", and "other".
    :vartype travel_mode: str or ~azure.maps.route.models.TravelMode
    :ivar simple_category: Type of the incident. Can currently be JAM, ROAD_WORK, ROAD_CLOSURE, or
     OTHER. See "tec" for detailed information. Known values are: "JAM", "ROAD_WORK",
     "ROAD_CLOSURE", and "OTHER".
    :vartype simple_category: str or ~azure.maps.route.models.SimpleCategory
    :ivar effective_speed_in_kmh: Effective speed of the incident in km/h, averaged over its entire
     length.
    :vartype effective_speed_in_kmh: int
    :ivar delay_in_seconds: Delay in seconds caused by the incident.
    :vartype delay_in_seconds: int
    :ivar delay_magnitude: The magnitude of delay caused by the incident. These values correspond
     to the values of the response field ty of the `Get Traffic Incident Detail API
     <https://docs.microsoft.com/rest/api/maps/traffic/gettrafficincidentdetail>`_. Known values
     are: "0", "1", "2", "3", and "4".
    :vartype delay_magnitude: str or ~azure.maps.route.models.DelayMagnitude
    :ivar tec: Details of the traffic event, using definitions in the `TPEG2-TEC
     <https://www.iso.org/standard/63116.html>`_ standard. Can contain effectCode and causes
     elements.
    :vartype tec: ~azure.maps.route.models.RouteSectionTec
    """

    _validation = {
        "start_point_index": {"readonly": True},
        "end_point_index": {"readonly": True},
        "section_type": {"readonly": True},
        "travel_mode": {"readonly": True},
        "simple_category": {"readonly": True},
        "effective_speed_in_kmh": {"readonly": True},
        "delay_in_seconds": {"readonly": True},
        "delay_magnitude": {"readonly": True},
    }

    _attribute_map = {
        "start_point_index": {"key": "startPointIndex", "type": "int"},
        "end_point_index": {"key": "endPointIndex", "type": "int"},
        "section_type": {"key": "sectionType", "type": "str"},
        "travel_mode": {"key": "travelMode", "type": "str"},
        "simple_category": {"key": "simpleCategory", "type": "str"},
        "effective_speed_in_kmh": {"key": "effectiveSpeedInKmh", "type": "int"},
        "delay_in_seconds": {"key": "delayInSeconds", "type": "int"},
        "delay_magnitude": {"key": "magnitudeOfDelay", "type": "str"},
        "tec": {"key": "tec", "type": "RouteSectionTec"},
    }

    def __init__(self, *, tec: Optional["RouteSectionTec"] = None, **kwargs):
        """
        :keyword tec: Details of the traffic event, using definitions in the `TPEG2-TEC
         <https://www.iso.org/standard/63116.html>`_ standard. Can contain effectCode and causes
         elements.
        :paramtype tec: ~azure.maps.route.models.RouteSectionTec
        """
        super().__init__(**kwargs)
        self.start_point_index = None
        self.end_point_index = None
        self.section_type = None
        self.travel_mode = None
        self.simple_category = None
        self.effective_speed_in_kmh = None
        self.delay_in_seconds = None
        self.delay_magnitude = None
        self.tec = tec

class RouteDirectionsBatchItemResult(object):
    """The result of the query. RouteDirections if the query completed successfully, ErrorResponse otherwise.

    Variables are only populated by the server, and will be ignored when sending a request.

    :ivar error: The error object.
    :vartype error: ~azure.maps.route.models.ErrorDetail
    :ivar format_version: Format Version property.
    :vartype format_version: str
    :ivar routes: Routes array.
    :vartype routes: list[~azure.maps.route.models.Route]
    :ivar optimized_waypoints: Optimized sequence of waypoints. It shows the index from the user
     provided waypoint sequence for the original and optimized list. For instance, a response:

     .. code-block::

        <optimizedWaypoints>
        <waypoint providedIndex="0" optimizedIndex="1"/>
        <waypoint providedIndex="1" optimizedIndex="2"/>
        <waypoint providedIndex="2" optimizedIndex="0"/>
        </optimizedWaypoints>

     means that the original sequence is [0, 1, 2] and optimized sequence is [1, 2, 0]. Since the
     index starts by 0 the original is "first, second, third" while the optimized is "second, third,
     first".
    :vartype optimized_waypoints: list[~azure.maps.route.models.RouteOptimizedWaypoint]
    :ivar report: Reports the effective settings used in the current call.
    :vartype report: RouteReport
    """

    _validation = {
        "format_version": {"readonly": True},
        "routes": {"readonly": True},
        "optimized_waypoints": {"readonly": True},
    }

    _attribute_map = {
        "error": {"key": "error", "type": "ErrorDetail"},
        "format_version": {"key": "formatVersion", "type": "str"},
        "routes": {"key": "routes", "type": "[Route]"},
        "optimized_waypoints": {"key": "optimizedWaypoints", "type": "[RouteOptimizedWaypoint]"},
        "report": {"key": "report", "type": "RouteReport"},
    }

    def __init__(
        self, *, error: Optional["ErrorDetail"] = None, report: Optional["RouteReport"] = None, **kwargs
    ):
        """
        :keyword error: The error object.
        :paramtype error: ~azure.maps.route.models.ErrorDetail
        :keyword report: Reports the effective settings used in the current call.
        :paramtype report: ~azure.maps.route.models.RouteReport
        """
        super().__init__(report=report, error=error, **kwargs)
        self.error = error
        self.format_version = None
        self.routes = None
        self.optimized_waypoints = None
        self.report = report

class RouteDirectionsBatchItem(object):
    """An item returned from Route Directions Batch service call.

    Variables are only populated by the server, and will be ignored when sending a request.

    :ivar result: The result of the query. RouteDirections if the query completed successfully,
     ErrorResponse otherwise.
    :vartype result: RouteDirectionsBatchItemResult
    """

    _validation = {
        "result": {"readonly": True},
    }

    _attribute_map = {
        "result": {"key": "result", "type": "RouteDirectionsBatchItemResult"},
    }

    def __init__(self, **kwargs):
        """ """
        super().__init__(**kwargs)
        self.result = None

class RouteDirectionsBatchResult(object):
    """This object is returned from a successful Route Directions Batch service call.

    Variables are only populated by the server, and will be ignored when sending a request.

    :keyword summary: Summary of the results for the batch request.
    :paramtype summary: ~azure.maps.route.models.BatchResultSummary
    :keyword items: Array containing the batch results.
    :paramtype items: list[RouteDirectionsBatchItem]
    """
    def __init__(
        self,
        summary: BatchResultSummary = None,
        items: List[RouteDirectionsBatchItem] = None
    ):
        self.summary = summary
        self.items = items

class RouteLeg(GenRouteLeg):
    """A description of a part of a route, comprised of a list of points.
    Each additional waypoint provided in the request will result in an additional
    leg in the returned route.

    Variables are only populated by the server, and will be ignored when sending a request.

    :ivar summary: Summary object for route section.
    :vartype summary: ~azure.maps.route.models.RouteLegSummary
    :ivar points: Points array.
    :vartype points: list[LatLon]
    """

    def __init__(self, **kwargs):
        """ """
        super().__init__(**kwargs)
        self.summary = None
        self.points = None

class GeoJsonObjectType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Specifies the ``GeoJSON`` type. Must be one of the nine valid GeoJSON object types - Point,
    MultiPoint, LineString, MultiLineString, Polygon, MultiPolygon, GeometryCollection, Feature and
    FeatureCollection.
    """

    GEO_JSON_POINT = "Point"  #: ``GeoJSON Point`` geometry.
    GEO_JSON_MULTI_POINT = "MultiPoint"  #: ``GeoJSON MultiPoint`` geometry.
    GEO_JSON_LINE_STRING = "LineString"  #: ``GeoJSON LineString`` geometry.
    GEO_JSON_MULTI_LINE_STRING = "MultiLineString"  #: ``GeoJSON MultiLineString`` geometry.
    GEO_JSON_POLYGON = "Polygon"  #: ``GeoJSON Polygon`` geometry.
    GEO_JSON_MULTI_POLYGON = "MultiPolygon"  #: ``GeoJSON MultiPolygon`` geometry.
    GEO_JSON_GEOMETRY_COLLECTION = "GeometryCollection"  #: ``GeoJSON GeometryCollection`` geometry.
    GEO_JSON_FEATURE = "Feature"  #: ``GeoJSON Feature`` object.
    GEO_JSON_FEATURE_COLLECTION = "FeatureCollection"  #: ``GeoJSON FeatureCollection`` object.

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
    :type type: str or GeoJsonObjectType
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
        _type: Union[str, GeoJsonObjectType] = None,
        **kwargs
    ):
        super(GeoJsonObject, self).__init__(**kwargs)
        self.type = _type  # type: Optional[Union[str, GeoJsonObjectType]]

class GeoJsonFeatureData(msrest.serialization.Model):
    """GeoJsonFeatureData.

    All required parameters must be populated in order to send to Azure.

    :param geometry: Required. A valid ``GeoJSON`` object. Please refer to `RFC 7946
     <https://tools.ietf.org/html/rfc7946#section-3>`_ for details.
    :type geometry: ~azure.maps.route.models.GeoJsonObject
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
    :type geometry: ~azure.maps.route.models.GeoJsonObject
    :param properties: Properties can contain any additional metadata about the ``Feature``. Value
     can be any JSON object or a JSON null value.
    :type properties: object
    :keyword feature_type: The type of the feature. The value depends on the data model the current
     feature is part of. Some data models may have an empty value.
    :paramtype feature_type: str
    :param type: Required. Specifies the ``GeoJSON`` type. Must be one of the nine valid GeoJSON
     object types - Point, MultiPoint, LineString, MultiLineString, Polygon, MultiPolygon,
     GeometryCollection, Feature and FeatureCollection.Constant filled by server.  Possible values
     include: "Point", "MultiPoint", "LineString", "MultiLineString", "Polygon", "MultiPolygon",
     "GeometryCollection", "Feature", "FeatureCollection".
    :type type: str or GeoJsonObjectType
    """

    _validation = {
        'geometry': {'required': True},
        'type': {'required': True},
    }

    _attribute_map = {
        'geometry': {'key': 'geometry', 'type': 'GeoJsonObject'},
        'properties': {'key': 'properties', 'type': 'object'},
        'feature_type': {'key': 'featureType', 'type': 'str'},
        'type': {'key': 'type', 'type': 'str'},
    }

    def __init__(
        self,
        *,
        geometry: "GeoJsonObject",
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
    :type features: list[~azure.maps.route.models.GeoJsonFeature]
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
    :type features: list[~azure.maps.route.models.GeoJsonFeature]
    :param type: Required. Specifies the ``GeoJSON`` type. Must be one of the nine valid GeoJSON
     object types - Point, MultiPoint, LineString, MultiLineString, Polygon, MultiPolygon,
     GeometryCollection, Feature and FeatureCollection.Constant filled by server.  Possible values
     include: "Point", "MultiPoint", "LineString", "MultiLineString", "Polygon", "MultiPolygon",
     "GeometryCollection", "Feature", "FeatureCollection".
    :type type: str or GeoJsonObjectType
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
    :type type: str or GeoJsonObjectType
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
    :type geometries: list[~azure.maps.route.models.GeoJsonObject]
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
    :type geometries: list[~azure.maps.route.models.GeoJsonObject]
    :param type: Required. Specifies the ``GeoJSON`` type. Must be one of the nine valid GeoJSON
     object types - Point, MultiPoint, LineString, MultiLineString, Polygon, MultiPolygon,
     GeometryCollection, Feature and FeatureCollection.Constant filled by server.  Possible values
     include: "Point", "MultiPoint", "LineString", "MultiLineString", "Polygon", "MultiPolygon",
     "GeometryCollection", "Feature", "FeatureCollection".
    :type type: str or GeoJsonObjectType
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
    :type type: str or GeoJsonObjectType
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
    :type type: str or GeoJsonObjectType
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
    :type type: str or GeoJsonObjectType
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
    :type type: str or GeoJsonObjectType
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
    :type type: str or ~azure.maps.route._models.GeoJsonObjectType
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
    :type type: str or GeoJsonObjectType
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

class TravelMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Travel mode for the calculated route. The value will be set to ``other`` if the requested mode
    of transport is not possible in this section.
    """

    #: The returned routes are optimized for cars.
    CAR = "car"
    #: The returned routes are optimized for commercial vehicles, like for trucks.
    TRUCK = "truck"
    #: The returned routes are optimized for taxis. BETA functionality.
    TAXI = "taxi"
    #: The returned routes are optimized for buses, including the use of bus only lanes. BETA
    #: functionality.
    BUS = "bus"
    #: The returned routes are optimized for vans. BETA functionality.
    VAN = "van"
    #: The returned routes are optimized for motorcycles. BETA functionality.
    MOTORCYCLE = "motorcycle"
    #: The returned routes are optimized for bicycles, including use of bicycle lanes.
    BICYCLE = "bicycle"
    #: The returned routes are optimized for pedestrians, including the use of sidewalks.
    PEDESTRIAN = "pedestrian"
    #: The given mode of transport is not possible in this section
    OTHER = "other"
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

# pylint: disable=unused-import,ungrouped-imports
from typing import List, Optional, Union
from enum import Enum, EnumMeta
from six import with_metaclass
import msrest.serialization

from azure.core import CaseInsensitiveEnumMeta

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
        top_left: LatLon = None,
        bottom_right: LatLon = None,
        top_right: LatLon = None,
        bottom_left: LatLon = None
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
    :param feature_type: The type of the feature. The value depends on the data model the current
     feature is part of. Some data models may have an empty value.
    :type feature_type: str
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

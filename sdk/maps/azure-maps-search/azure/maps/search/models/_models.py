import msrest.serialization
from typing import List, Optional

class LatLon(object):

    def __init__(self):
        self._lat=None,
        self._lon=None

    @property
    def lat(self) -> float:
        return self._lat

    @lat.setter
    def lat(self, value: float) -> None:
        if not isinstance(value, float):
            raise TypeError(f'lat.setter(): got {type(value).__name__} but expected type is float')
        else:
            self._lat = value

    @property
    def lon(self) -> float:
        return self._lon

    @lon.setter
    def lon(self, value) -> None:
        if not isinstance(value, float):
            raise TypeError(f'lon.setter(): got {type(value).__name__} but expected type is float')
        else:
            self._lon = value

class BoundingBox(object):

    def __init__(
        self,
        top_left: str=None,
        bottom_right: str=None
    ):
        self.top_left = top_left
        self.bottom_right = bottom_right


class StructuredAddress(msrest.serialization.Model):

    _validation = {
        'country_code': {'required': True},
    }

    _attribute_map = {
        'country_code': {'key': 'country_code', 'type': 'str'},
        'street_number': {'key': 'street_number', 'type': 'str'},
        'street_name': {'key': 'street_name', 'type': 'str'},
        'cross_street': {'key': 'cross_street', 'type': 'str'},
        'municipality': {'key': 'municipality', 'type': 'str'},
        'municipality_subvision': {'key': 'municipality_subvision', 'type': 'str'},
        'country_tertiary_subdivision': {'key': 'country_tertiary_subdivision', 'type': 'str'},
        'country_secondary_subdivision': {'key': 'country_secondary_subdivision', 'type': 'str'},
        'country_subdivision': {'key': 'country_subdivision', 'type': 'str'},
        'postal_code': {'key': 'postal_code', 'type': 'str'},
    }

    def __init__(
        self,
        *,
        country_code: str,
        cross_street: Optional[str] = None,
        street_number: Optional[str] = None,
        street_name: Optional[str] = None,
        municipality: Optional[str] = None,
        municipality_subdivision: Optional[str] = None,
        country_tertiary_subdivision: Optional[str] = None,
        country_secondary_subdivision: Optional[str] = None,
        country_subdivision: Optional[str] = None,
        postal_code: Optional[str] = None,
        **kwargs
    ):
        super(StructuredAddress, self).__init__(country_code=country_code, **kwargs)
        self.country_code = country_code
        self.cross_street = cross_street
        self.street_number = street_number
        self.street_name = street_name
        self.municipality = municipality
        self.municipality_subdivision = municipality_subdivision
        self.country_tertiary_subdivision = country_tertiary_subdivision
        self.country_secondary_subdivision = country_secondary_subdivision
        self.country_subdivision = country_subdivision
        self.postal_code = postal_code


# class Polygon(msrest.serialization.Model):
#     """This object is returned from a successful Search Polygon call.

#     Variables are only populated by the server, and will be ignored when sending a request.

#     :ivar polygons: Results array.
#     :vartype polygons: list[~azure.maps.search.models.Polygon]
#     """

#     _validation = {
#         'provider_id': {'readonly': True},
#         'polygons': {'readonly': True},
#     }

#     _attribute_map = {
#         'provider_id': {'key': 'providerID', 'type': 'str'},
#         'geometry_data': {'key': 'geometryData', 'type': 'GeoJsonObject'},
#     }


#     def __init__(
#         self,
#         **kwargs
#     ):
#         super(Polygon, self).__init__(**kwargs)
#         self.provider_id = None
#         self.geometry_data = kwargs.get('geometry_data', None)


# class Polygon(msrest.serialization.Model):
#     """Polygon.

#     Variables are only populated by the server, and will be ignored when sending a request.

#     :ivar provider_id: ID of the returned entity.
#     :vartype provider_id: str
#     :param geometry_data: Geometry data in GeoJSON format. Please refer to `RFC 7946
#      <https://tools.ietf.org/html/rfc7946>`_ for details. Present only if "error" is not present.
#     :type geometry_data: ~azure.maps.search.models.GeoJsonObject
#     """

#     _validation = {
#         'provider_id': {'readonly': True},
#     }

#     _attribute_map = {
#         'provider_id': {'key': 'providerID', 'type': 'str'},
#         'geometry_data': {'key': 'geometryData', 'type': 'GeoJsonObject'},
#     }

#     def __init__(
#         self,
#         **kwargs
#     ):
#         super(Polygon, self).__init__(**kwargs)
#         self.provider_id = None
#         self.geometry_data = kwargs.get('geometry_data', None)

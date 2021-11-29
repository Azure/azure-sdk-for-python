from .._generated.models import *
import msrest.serialization
from typing import List, Optional

class LatLong(msrest.serialization.Model):
    _attribute_map = {
        'lat': {'key': 'lat', 'type': 'float'},
        'lon': {'key': 'lon', 'type': 'float'},
    }

    def __init__(
        self,
        lat=None,
        lon=None,
        **kwargs
    ):
        super(LatLong, self).__init__(**kwargs, lat, lon)
        self.lat = lat
        self.lon = lon

    def toLatLongList(self): # type: (...) -> List[float]
        return [self.latitude, self.longitude]


class BoundingBox(msrest.serialization.Model):
    _attribute_map = {
        'top_left': {'key': 'top_left', 'type': 'str'},
        'bottom_right': {'key': 'bottom_right', 'type': 'str'},
    }

    def __init__(
        self,
        top_left=None,
        bottom_right=None,
        **kwargs
    ):
        super(BoundingBox, self).__init__(**kwargs, top_left, bottom_right)
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

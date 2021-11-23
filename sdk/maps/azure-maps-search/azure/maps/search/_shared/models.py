from .._generated.models import *
import msrest.serialization
from typing import List

class LatLong(msrest.serialization.Model):
    _attribute_map = {
        'latitude': {'key': 'latitude', 'type': 'float'},
        'longitude': {'key': 'longitude', 'type': 'float'},
    }

    def __init__(
        self,
        **kwargs
    ):
        super(LatLong, self).__init__(**kwargs)
        self.latitude = kwargs.get('latitude', None)
        self.longitude = kwargs.get('longitude', None)

    def toLatLongList(self): # type: (...) -> List[float]
        return [self.latitude, self.longitude]


class BoundingBox(msrest.serialization.Model):
    _attribute_map = {
        'top_left': {'key': 'top_left', 'type': 'str'},
        'bottom_right': {'key': 'bottom_right', 'type': 'str'},
    }

    def __init__(
        self,
        **kwargs
    ):
        super(BoundingBox, self).__init__(**kwargs)
        self.top_left = kwargs.get('top_left', None)
        self.bottom_right = kwargs.get('bottom_right', None)

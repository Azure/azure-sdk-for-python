from .._generated.models import *
import msrest.serialization
from typing import List

class Coordinates(msrest.serialization.Model):
    _attribute_map = {
        'latitude': {'key': 'latitude', 'type': 'float'},
        'longitude': {'key': 'longitude', 'type': 'float'},
    }

    def __init__(
        self,
        **kwargs
    ):
        super(Coordinates, self).__init__(**kwargs)
        self.latitude = kwargs.get('latitude', None)
        self.longitude = kwargs.get('longitude', None)

    def toCoordinateList(self): # type: (...) -> List[float]
        return [self.latitude, self.longitude]

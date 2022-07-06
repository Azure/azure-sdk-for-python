from typing import List, Optional
from .._generated.models import *

class LatLon(object):

    def __init__(
        self,
        lat: float=None,
        lon: float=None
    ):
        self._lat = lat
        self._lon = lon

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
    def lon(self, value: float) -> None:
        if not isinstance(value, float):
            raise TypeError(f'lon.setter(): got {type(value).__name__} but expected type is float')
        else:
            self._lon = value

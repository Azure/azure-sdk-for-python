# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

# pylint: disable=unused-import,ungrouped-imports
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
        self._lat = value

    @property
    def lon(self) -> float:
        return self._lon

    @lon.setter
    def lon(self, value: float) -> None:
        if not isinstance(value, float):
            raise TypeError(f'lon.setter(): got {type(value).__name__} but expected type is float')
        self._lon = value

class BoundingBox(object):

    def __init__(
        self,
        top_left: LatLon=None,
        bottom_right: LatLon=None,
        top_right: LatLon=None,
        bottom_left: LatLon=None
    ):
        self.top_left = top_left
        self.bottom_right = bottom_right
        self.top = top_left.lat
        self.bottom = bottom_right.lat
        self.left = top_left.lon
        self.right = bottom_right.lon
        self.top_right = top_right if top_right else LatLon(top_left.lat, bottom_right.lon)
        self.bottom_left = bottom_left if bottom_left else LatLon(bottom_right.lat, top_left.lon)

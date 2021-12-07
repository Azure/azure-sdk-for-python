from typing import List, Optional

class LatLon(object):

    def __init__(
        self,
        lat: float=None,
        lon: float=None
    ):
        self._lat = lat
        self._lon = lon

    def __transform__(self, **kwargs): # type: (...) -> List[float]
        return [self._lat, self._lon]

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


class StructuredAddress(object):

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

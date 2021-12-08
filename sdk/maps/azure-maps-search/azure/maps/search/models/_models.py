from typing import List, Optional
from .._generated.models import PointOfInterest, Address, EntryPoint, AddressRanges, DataSource, LatLongPairAbbreviated

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
        postal_code: Optional[str] = None
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


class SearchAddressResultItem(object):

    def __init__(
        self,
        type: str = None,
        id: str = None,
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
        self.type = type
        self.id = id
        self.score = score
        self.distance_in_meters = distance_in_meters
        self.info = info
        self.entity_type = entity_type
        self.point_of_interest = point_of_interest
        self.address = address
        self.position = LatLon() if not position else LatLon(position.lat, position.lon) 
        self.viewport = viewport
        self.entry_points = entry_points
        self.address_ranges = LatLon() if not position else LatLon(
            address_ranges.range_left, address_ranges.range_right
        )
        self.data_sources = data_sources
        self.match_type = match_type
        self.detour_time = detour_time


class SearchAddressResult(object):

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

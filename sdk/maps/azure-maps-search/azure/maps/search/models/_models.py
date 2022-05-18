from typing import List, Optional
from .._generated.models import PointOfInterest, Address, EntryPoint, AddressRanges, DataSource, ReverseSearchAddressResultItem, ReverseSearchAddressBatchItem, BatchResultSummary

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

class StructuredAddress(object):

    def __init__(
        self,
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
        self._country_code = country_code
        self.cross_street = cross_street
        self.street_number = street_number
        self.street_name = street_name
        self.municipality = municipality
        self.municipality_subdivision = municipality_subdivision
        self.country_tertiary_subdivision = country_tertiary_subdivision
        self.country_secondary_subdivision = country_secondary_subdivision
        self.country_subdivision = country_subdivision
        self.postal_code = postal_code

    @property
    def country_code(self) -> str:
        return self._country_code

    @country_code.setter
    def country_code(self, value: str) -> None:
        if not isinstance(value, str):
            raise TypeError(f'country_code.setter(): got {type(value).__name__} but expected type is string')
        else:
            self._country_code = value

    @property
    def cross_street(self) -> str:
        return self._cross_street

    @cross_street.setter
    def cross_street(self, value: str) -> None:
        if not isinstance(value, str):
            raise TypeError(f'cross_street.setter(): got {type(value).__name__} but expected type is string')
        else:
            self._cross_street = value

    @property
    def street_number(self) -> str:
        return self._street_number

    @street_number.setter
    def street_number(self, value) -> None:
        if not isinstance(value, str):
            raise TypeError(f'street_number.setter(): got {type(value).__name__} but expected type is string')
        else:
            self._street_number = value

    @property
    def street_name(self) -> str:
        return self._street_name

    @street_name.setter
    def street_name(self, value: str) -> None:
        if not isinstance(value, str):
            raise TypeError(f'street_name.setter(): got {type(value).__name__} but expected type is string')
        else:
            self._street_name = value

    @property
    def municipality(self) -> str:
        return self._municipality

    @municipality.setter
    def municipality(self, value: str) -> None:
        if not isinstance(value, str):
            raise TypeError(f'municipality.setter(): got {type(value).__name__} but expected type is string')
        else:
            self._municipality = value

    @property
    def municipality_subdivision(self) -> str:
        return self._municipality_subdivision

    @municipality_subdivision.setter
    def municipality_subdivision(self, value: str) -> None:
        if not isinstance(value, str):
            raise TypeError(f'municipality_subdivision.setter(): got {type(value).__name__} but expected type is string')
        else:
            self._municipality_subdivision = value

    @property
    def country_tertiary_subdivision(self) -> str:
        return self._country_tertiary_subdivision

    @country_tertiary_subdivision.setter
    def country_tertiary_subdivision(self, value: str) -> None:
        if not isinstance(value, str):
            raise TypeError(f'country_tertiary_subdivision.setter(): got {type(value).__name__} but expected type is string')
        else:
            self._country_tertiary_subdivision = value

    @property
    def country_secondary_subdivision(self) -> str:
        return self._country_secondary_subdivision

    @country_secondary_subdivision.setter
    def country_secondary_subdivision(self, value: str) -> None:
        if not isinstance(value, str):
            raise TypeError(f'country_secondary_subdivision.setter(): got {type(value).__name__} but expected type is string')
        else:
            self._country_secondary_subdivision = value

    @property
    def country_subdivision(self) -> str:
        return self._country_subdivision

    @country_subdivision.setter
    def country_subdivision(self, value: str) -> None:
        if not isinstance(value, str):
            raise TypeError(f'country_subdivision.setter(): got {type(value).__name__} but expected type is string')
        else:
            self._country_subdivision = value

    @property
    def postal_code(self) -> str:
        return self._postal_code

    @postal_code.setter
    def postal_code(self, value: str) -> None:
        if not isinstance(value, str):
            raise TypeError(f'postal_code.setter(): got {type(value).__name__} but expected type is string')
        else:
            self._postal_code = value


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


class AddressRanges(object):

    def __init__(
        self,
        range_left: str = None,
        range_right: str = None,
        from_property: LatLon = None,
        to_: LatLon = None
    ):
        self.range_left = range_left,
        self.range_right = range_right,
        self.from_property = LatLon() if not from_property else LatLon(
            from_property.lat, from_property.lon
        ),
        self.to =  LatLon() if not to_ else LatLon(
            to_.lat, to_.lon
        )


class EntryPoint(object):
    
    def __init__(
        self,
        type: str = None,
        position: LatLon = None
    ):
        self.type = type
        self.position = LatLon() if not position else LatLon(
            position.lat, position.lon
        )


class Address(object):

    def __init__(
        self,
        building_number: str,
        street: str,
        cross_street: str = None,
        street_number: str = None,
        route_numbers: List[int] = None,
        street_name: str = None,
        street_name_and_number: str = None,
        municipality: str = None,
        municipality_subdivision: str = None,
        country_tertiary_subdivision:str = None,
        country_secondary_subdivision: str = None,
        country_subdivision: str = None,
        postal_code: str = None,
        extended_postal_code: str = None,
        country_code: str = None,
        country: str = None,
        country_code_iso3: str = None,
        freeform_address: str = None,
        country_subdivision_name: str = None,
        local_name: str = None,
        bounding_box: BoundingBox = None,
    ):
        self.building_number = building_number
        self.street = street
        self.cross_street = cross_street
        self.street_number = street_number
        self.route_numbers = route_numbers
        self.street_name = street_name
        self.street_name_and_number = street_name_and_number
        self.municipality = municipality
        self.municipality_subdivision = municipality_subdivision
        self.country_tertiary_subdivision = country_tertiary_subdivision
        self.country_secondary_subdivision = country_secondary_subdivision
        self.country_subdivision = country_subdivision
        self.postal_code = postal_code
        self.extended_postal_code = extended_postal_code
        self.country_code = country_code
        self.country = country
        self.country_code_iso3 = country_code_iso3
        self.freeform_address = freeform_address
        self.country_subdivision_name = country_subdivision_name
        self.local_name = local_name
        self.bounding_box = bounding_box


class SearchAddressResultItem(object):

    def __init__(
        self,
        type_: str = None,
        id_: str = None,
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
        self.type = type_
        self.id = id_
        self.score = score
        self.distance_in_meters = distance_in_meters
        self.info = info
        self.entity_type = entity_type
        self.point_of_interest = point_of_interest
        self.address = address
        self.position = LatLon() if not position else LatLon(
            position.lat, position.lon
        )
        self.viewport = viewport
        self.entry_points = entry_points
        self.address_ranges = LatLon() if not position else LatLon(
            address_ranges.range_left, address_ranges.range_right
        )
        self.data_sources = data_sources
        self.match_type = match_type
        self.detour_time = detour_time


class SearchAddressResult(object):
    """This object is returned from a successful Search calls.

    Variables are only populated by the server, and will be ignored when sending a request.

    :ivar summary: Summary object for a Search API response.
    :vartype summary: ~azure.maps.search.models.SearchSummary
    :ivar results: A list of Search API results.
    :vartype results: list[~azure.maps.search.models.SearchAddressResultItem]
    """
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


class ReverseSearchAddressResultItem(object):
    """Result object for a Search Address Reverse response.

    Variables are only populated by the server, and will be ignored when sending a request.

    :ivar address: The address of the result.
    :vartype address: ~azure.maps.search.models.Address
    :ivar position: Position property in the form of "latitude,longitude".
    :vartype position: str
    :ivar road_use:
    :vartype road_use: list[str]
    :ivar match_type: Information on the type of match.
    :vartype match_type: str or ~azure.maps.search.models.MatchType
    """
    def __init__(
        self,
        address: Address = None,
        position: str = None,
        road_use: List[str] = None,
        match_type: str = None
    ):
        self.address = address
        self.position = LatLon() if not position else LatLon(
            float(position.split(',')[0]), float(position.split(',')[1])
        )
        self.road_use = road_use
        self.match_type = match_type


class ReverseSearchAddressResult(object):
    """This object is returned from a successful Search Address Reverse call.

    Variables are only populated by the server, and will be ignored when sending a request.

    :ivar summary: Summary object for a Search Address Reverse response.
    :vartype summary: ~azure.maps.search.models.SearchSummary
    :ivar addresses: Addresses array.
    :vartype addresses: list[~azure.maps.search.models.ReverseSearchAddressResultItem]
    """
    def __init__(
        self,
        summary: SearchSummary = None,
        results: List[ReverseSearchAddressResultItem] = None
    ):
        self.query_type = summary.query_type
        self.query_time = summary.query_time
        self.results = results


class ReverseSearchAddressBatchProcessResult(object):
    """This object is returned from a successful Search Address Reverse Batch service call.

    Variables are only populated by the server, and will be ignored when sending a request.

    :ivar summary: Summary of the results for the batch request.
    :vartype batch_summary: ~azure.maps.search._generated.models.BatchResultSummary
    :ivar items: Array containing the batch results.
    :vartype batch_items: list[~azure.maps.search._generated.models.ReverseSearchAddressBatchItem]
    """

    def __init__(
        self,
        summary: BatchResultSummary = None,
        items: List[ReverseSearchAddressBatchItem] = None
    ):
        self.summary = summary
        self.items = items
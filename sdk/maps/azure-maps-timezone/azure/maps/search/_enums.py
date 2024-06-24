# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from enum import Enum
from azure.core import CaseInsensitiveEnumMeta


class LocalizedMapView(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """LocalizedMapView."""

    AE = "AE"
    """United Arab Emirates (Arabic View)"""
    AR = "AR"
    """Argentina (Argentinian View)"""
    BH = "BH"
    """Bahrain (Arabic View)"""
    IN = "IN"
    """India (Indian View)"""
    IQ = "IQ"
    """Iraq (Arabic View)"""
    JO = "JO"
    """Jordan (Arabic View)"""
    KW = "KW"
    """Kuwait (Arabic View)"""
    LB = "LB"
    """Lebanon (Arabic View)"""
    MA = "MA"
    """Morocco (Moroccan View)"""
    OM = "OM"
    """Oman (Arabic View)"""
    PK = "PK"
    """Pakistan (Pakistani View)"""
    PS = "PS"
    """Palestinian Authority (Arabic View)"""
    QA = "QA"
    """Qatar (Arabic View)"""
    SA = "SA"
    """Saudi Arabia (Arabic View)"""
    SY = "SY"
    """Syria (Arabic View)"""
    YE = "YE"
    """Yemen (Arabic View)"""
    AUTO = "Auto"
    """Return the map data based on the IP address of the request."""
    UNIFIED = "Unified"
    """Unified View (Others)"""


class BoundaryResultType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """BoundaryResultType."""

    COUNTRY_REGION = "countryRegion"
    """Country or region."""
    ADMIN_DISTRICT = "adminDistrict"
    """First administrative level within the country/region level, such as a state or a province."""
    ADMIN_DISTRICT2 = "adminDistrict2"
    """Second administrative level within the country/region level, such as a county."""
    POSTAL_CODE = "postalCode"
    """The smallest post code category, such as a zip code."""
    POSTAL_CODE2 = "postalCode2"
    """The next largest post code category after postalCode that is created by aggregating postalCode
    areas."""
    POSTAL_CODE3 = "postalCode3"
    """The next largest post code category after postalCode2 that is created by aggregating
    postalCode2 areas."""
    POSTAL_CODE4 = "postalCode4"
    """The next largest post code category after postalCode3 that is created by aggregating
    postalCode3 areas."""
    NEIGHBORHOOD = "neighborhood"
    """A section of a populated place that is typically well-known, but often with indistinct
    boundaries."""
    LOCALITY = "locality"
    """A concentrated area of human settlement, such as a city, town or village."""


class CalculationMethod(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """The method that was used to compute the geocode point."""

    INTERPOLATION = "Interpolation"
    """The geocode point was matched to a point on a road using interpolation."""
    INTERPOLATION_OFFSET = "InterpolationOffset"
    """The geocode point was matched to a point on a road using interpolation with an additional
    offset to shift the point to the side of the street."""
    PARCEL = "Parcel"
    """The geocode point was matched to the center of a parcel."""
    ROOFTOP = "Rooftop"
    """The geocode point was matched to the rooftop of a building."""


class Confidence(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """The level of confidence that the geocoded location result is a match. Use this value with the
    match code to determine for more complete information about the match.
    The confidence of a geocoded location is based on many factors including the relative
    importance of the geocoded location and the user’s location, if specified.
    """

    HIGH = "High"
    """If the confidence is set to ``High``\\ , one or more strong matches were found. Multiple
    ``High`` confidence matches are sorted in ranked order by importance when applicable. For
    example, landmarks have importance but addresses do not.

    If a request includes a location or a view, then the ranking may change appropriately. For
    example, a location query for "Paris" returns "Paris, France" and "Paris, TX" both with
    ``High`` confidence. "Paris, France" is always ranked first due to importance unless a user
    location indicates that the user is in or very close to Paris, TX or the map view indicates
    that the user is searching in that area."""
    MEDIUM = "Medium"
    """In some situations, the returned match may not be at the same level as the information provided
    in the request. For example, a request may specify address information and the geocode service
    may only be able to match a postal code. In this case, if the geocode service has a confidence
    that the postal code matches the data, the confidence is set to ``Medium`` and the match code
    is set to ``UpHierarchy`` to specify that it could not match all of the information and had to
    search up-hierarchy.

    If the location information in the query is ambiguous, and there is no additional information
    to rank the locations (such as user location or the relative importance of the location), the
    confidence is set to ``Medium``. For example, a location query for "148th Ave, Bellevue" may
    return "148th Ave SE" and "148th Ave NE" both with ``Medium`` confidence.

    If the location information in the query does not provide enough information to geocode a
    specific location, a less precise location value may be returned and the confidence is set to
    ``Medium``. For example, if an address is provided, but a match is not found for the house
    number, the geocode result with a Roadblock entity type may be returned."""
    LOW = "Low"


class FeatureCollection(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """The type of a FeatureCollection object must be FeatureCollection."""

    FEATURE_COLLECTION = "FeatureCollection"


class FeatureType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """The type of a feature must be Feature."""

    FEATURE = "Feature"


class GeoJsonObjectType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Specifies the ``GeoJSON`` type. Must be one of the nine valid GeoJSON object types - Point,
    MultiPoint, LineString, MultiLineString, Polygon, MultiPolygon, GeometryCollection, Feature and
    FeatureCollection.
    """

    GEO_JSON_POINT = "Point"
    """``GeoJSON Point`` geometry."""
    GEO_JSON_MULTI_POINT = "MultiPoint"
    """``GeoJSON MultiPoint`` geometry."""
    GEO_JSON_LINE_STRING = "LineString"
    """``GeoJSON LineString`` geometry."""
    GEO_JSON_MULTI_LINE_STRING = "MultiLineString"
    """``GeoJSON MultiLineString`` geometry."""
    GEO_JSON_POLYGON = "Polygon"
    """``GeoJSON Polygon`` geometry."""
    GEO_JSON_MULTI_POLYGON = "MultiPolygon"
    """``GeoJSON MultiPolygon`` geometry."""
    GEO_JSON_GEOMETRY_COLLECTION = "GeometryCollection"
    """``GeoJSON GeometryCollection`` geometry."""
    GEO_JSON_FEATURE = "Feature"
    """``GeoJSON Feature`` object."""
    GEO_JSON_FEATURE_COLLECTION = "FeatureCollection"
    """``GeoJSON FeatureCollection`` object."""


class MatchCodes(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """MatchCodes."""

    GOOD = "Good"
    AMBIGUOUS = "Ambiguous"
    UP_HIERARCHY = "UpHierarchy"


class Resolution(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Resolution."""

    SMALL = "small"
    """Return the boundary geometry with the least amount of points."""
    MEDIUM = "medium"
    """Return the boundary geometry with more or the same amount of points as small."""
    LARGE = "large"
    """Return the boundary geometry with more or the same amount of points as medium."""
    HUGE = "huge"
    """Return the boundary geometry with more or the same amount of points as large."""


class ResultType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """ResultType."""

    ADDRESS = "Address"
    NEIGHBORHOOD = "Neighborhood"
    POPULATED_PLACE = "PopulatedPlace"
    POSTCODE1 = "Postcode1"
    ADMIN_DIVISION1 = "AdminDivision1"
    ADMIN_DIVISION2 = "AdminDivision2"
    COUNTRY_REGION = "CountryRegion"


class ReverseGeocodingResultType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """ReverseGeocodingResultType."""

    ADDRESS = "Address"
    NEIGHBORHOOD = "Neighborhood"
    POPULATED_PLACE = "PopulatedPlace"
    POSTCODE1 = "Postcode1"
    ADMIN_DIVISION1 = "AdminDivision1"
    ADMIN_DIVISION2 = "AdminDivision2"
    COUNTRY_REGION = "CountryRegion"


class UsageType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """UsageType."""

    DISPLAY = "Display"
    ROUTE = "Route"

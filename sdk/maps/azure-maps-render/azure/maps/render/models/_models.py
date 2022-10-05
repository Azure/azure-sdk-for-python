# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

# pylint: disable=unused-import,ungrouped-imports, C0302, C0203
from typing import NamedTuple
from .._generated.models import (
    Copyright as GenCopyright,
    RegionCopyrights as GenRegionCopyrights,
    RegionCopyrightsCountry as GenRegionCopyrightsCountry,
    MapTileset as GenMapTileset
)

class LatLon(NamedTuple):
    """Represents coordinate latitude and longitude

    :keyword lat: The coordinate as latitude.
    :paramtype lat: float
    :keyword lon: The coordinate as longitude.
    :paramtype lon: float
    """
    lat: float = 0
    lon: float = 0


class BoundingBox(NamedTuple):
    """Represents information about the coordinate range

    :keyword west: The westmost value of coordinates.
    :paramtype west: float
    :keyword south: The southmost value of coordinates.
    :paramtype south: float
    :keyword east: The eastmost value of coordinates.
    :paramtype east: float
    :keyword north: The northmost value of coordinates.
    :paramtype north: float
    """
    west: float = 0.0
    south: float = 0.0
    east: float = 0.0
    north: float = 0.0


class RegionalCopyrights(GenRegionCopyrights):
    """RegionCopyrights.

    Variables are only populated by the server, and will be ignored when sending a request.

    :keyword copyrights: Copyrights array.
    :paramtype copyrights: list[str]
    :keyword country: Country property.
    :paramtype country: ~azure.maps.render.models.RegionCopyrightsCountry
    """
    def __init__(self, copyrights=None, country=None):
        self.copyrights = copyrights
        self.country = country

class Copyright(GenCopyright):
    """Represents information about the coordinate range

    :keyword format_version: Format Version property.
    :paramtype format_version: str
    :keyword general_copyrights: General Copyrights array.
    :paramtype general_copyrights: list[str]
    :keyword regional_copyrights: Regions array.
    :paramtype regional_copyrights: list[RegionalCopyrights]
    """
    def __init__(self, format_version=None, general_copyrights=None, regional_copyrights=None):
        self.format_version = format_version
        self.general_copyrights = general_copyrights
        self.regional_copyrights = regional_copyrights

class RegionCopyrightsCountry(GenRegionCopyrightsCountry):
    """Country property.

    Variables are only populated by the server, and will be ignored when sending a request.

    :keyword iso3_code: ISO3 property.
    :paramtype iso3_code: str
    :keyword label: Label property.
    :paramtype label: str
    """
    def __init__(self, iso3_code=None, label=None):
        self.iso3_code = iso3_code
        self.label = label


class MapTileset(GenMapTileset):  # pylint: disable=too-many-instance-attributes
    """Metadata for a tileset in the TileJSON format.

    :keyword tilejson_version: Describes the version of the TileJSON spec that is implemented by this JSON
     object.
    :paramtype tilejson_version: str
    :keyword name: A name describing the tileset. The name can contain any legal character.
     Implementations SHOULD NOT interpret the name as HTML.
    :paramtype name: str
    :keyword description: Text description of the tileset. The description can contain any legal
     character. Implementations SHOULD NOT interpret the description as HTML.
    :paramtype description: str
    :keyword version: A semver.org style version number for the tiles contained within the tileset.
     When changes across tiles are introduced, the minor version MUST change.
    :paramtype version: str
    :keyword map_attribution: Copyright attribution to be displayed on the map. Implementations MAY decide
     to treat this as HTML or literal text. For security reasons, make absolutely sure that this
     field can't be abused as a vector for XSS or beacon tracking.
    :paramtype map_attribution: str
    :keyword template: A mustache template to be used to format data from grids for interaction.
    :paramtype template: str
    :keyword legend: A legend to be displayed with the map. Implementations MAY decide to treat this
     as HTML or literal text. For security reasons, make absolutely sure that this field can't be
     abused as a vector for XSS or beacon tracking.
    :paramtype legend: str
    :keyword scheme: Default: "xyz". Either "xyz" or "tms". Influences the y direction of the tile
     coordinates. The global-mercator (aka Spherical Mercator) profile is assumed.
    :paramtype scheme: str
    :keyword tiles_endpoints: An array of tile endpoints. If multiple endpoints are specified, clients may use
     any combination of endpoints. All endpoints MUST return the same content for the same URL. The
     array MUST contain at least one endpoint.
    :paramtype tiles_endpoints: list[str]
    :keyword grid_endpoints: An array of interactivity endpoints.
    :paramtype grid_endpoints: list[str]
    :keyword data_files: An array of data files in GeoJSON format.
    :paramtype data_files: list[str]
    :keyword min_zoom: The minimum zoom level.
    :paramtype min_zoom: int
    :keyword max_zoom: The maximum zoom level.
    :paramtype max_zoom: int
    :keyword bounds: The maximum extent of available map tiles. Bounds MUST define an area covered by
     all zoom levels. The bounds are represented in WGS:84 latitude and longitude values, in the
     order left, bottom, right, top. Values may be integers or floating point numbers.
    :paramtype bounds: BoundingBox
    :keyword center: The default location of the tileset in the form [longitude, latitude, zoom]. The
     zoom level MUST be between minzoom and maxzoom. Implementations can use this value to set the
     default location.
    :paramtype center: LatLon
    """
    def __init__(
        self,
        tilejson_version= None,
        name= None,
        description= None,
        version= None,
        map_attribution= None,
        template= None,
        legend= None,
        scheme= None,
        tiles_endpoints= None,
        grid_endpoints= None,
        data_files = None,
        min_zoom= None,
        max_zoom= None,
        bounds= None,
        center= None
    ):
        self.tilejson_version = tilejson_version
        self.name = name
        self.description = description
        self.version = version
        self.map_attribution = map_attribution
        self.template = template
        self.legend = legend
        self.scheme = scheme
        self.tiles_endpoints = tiles_endpoints
        self.grid_endpoints = grid_endpoints
        self.data_files = data_files
        self.min_zoom = min_zoom
        self.max_zoom = max_zoom
        self.bounds = bounds
        self.center = center

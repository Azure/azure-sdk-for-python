# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

# pylint: disable=unused-import,ungrouped-imports,super-init-not-called, C0302, C0203
from typing import NamedTuple, Any
from .._generated.models import (
    MapAttribution,
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

class RegionalCopyrightsCountry(GenRegionCopyrightsCountry):
    """Country property.

    Variables are only populated by the server, and will be ignored when sending a request.

    :keyword iso3_code: ISO3 property.
    :paramtype iso3_code: str
    :keyword label: Label property.
    :paramtype label: str
    """
    def __init__(
        self,
        **kwargs: Any
    ):
        self.iso3_code = kwargs.get("iso3_code", None)
        self.label = kwargs.get("label", None)

class RegionalCopyrights(GenRegionCopyrights):
    """RegionCopyrights.

    Variables are only populated by the server, and will be ignored when sending a request.

    :keyword copyrights: Copyrights array.
    :paramtype copyrights: list[str]
    :keyword country: Country property.
    :paramtype country: RegionalCopyrightsCountry
    """
    def __init__(
        self,
        **kwargs: Any
    ):
        self.copyrights = kwargs.get("copyrights", None)
        self.country = kwargs.get("country", None)

class Copyright(GenCopyright):
    """Represents information about the coordinate range

    :keyword format_version: Format Version property.
    :paramtype format_version: str
    :keyword general_copyrights: General Copyrights array.
    :paramtype general_copyrights: list[str]
    :keyword regional_copyrights: Regions array.
    :paramtype regional_copyrights: list[RegionalCopyrights]
    """
    def __init__(
        self,
        **kwargs: Any
    ):
        self.format_version = kwargs.get("format_version", None)
        self.general_copyrights = kwargs.get("general_copyrights", None)
        self.regional_copyrights = kwargs.get("regional_copyrights", None)

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
    :paramtype map_attribution: ~azure.maps.render.models.MapAttribution
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
        **kwargs: Any
    ):
        self.tilejson_version = kwargs.get("tilejson_version", None)
        self.name = kwargs.get("name", None)
        self.description = kwargs.get("description", None)
        self.version = kwargs.get("version", None)
        self.map_attribution = kwargs.get("map_attribution", None)
        self.template = kwargs.get("template", None)
        self.legend = kwargs.get("legend", None)
        self.scheme = kwargs.get("scheme", None)
        self.tiles_endpoints = kwargs.get("tiles_endpoints", None)
        self.grid_endpoints = kwargs.get("grid_endpoints", None)
        self.data_files = kwargs.get("data_files", None)
        self.min_zoom = kwargs.get("min_zoom", None)
        self.max_zoom = kwargs.get("max_zoom", None)
        self.bounds = kwargs.get("bounds", None)
        self.center = kwargs.get("center", None)

class ImagePathStyle(object):
    """Path style including line color, line opacity, circle position, color and opacity settings

    :keyword path_positions:
        The list of point coordinate on the path.
    :paramtype path_positions: LatLon
    :keyword line_color:
        Line color of the path, including line opacity information.
    :paramtype line_color: str
    :keyword fill_color:
        Fill color of the path, including line opacity information.
    :paramtype fill_color: str
    :keyword line_width_in_pixels:
        Line width of the path in pixels.
    :paramtype line_width_in_pixels: int
    :keyword circle_radius_in_meters:
        Circle radius in meters.
    :paramtype circle_radius_in_meters: int
    """
    path_positions: LatLon = None
    line_color: str = None
    fill_color: str = None
    line_width_in_pixels: int = 0
    circle_radius_in_meters: int = 0

class ImagePushpinStyle(object):
    """Pushpin style including pin and label color, scale, rotation and position settings

    :keyword pushpin_positions:
        The list of Pushpin coordinate on the map.
    :paramtype path_positions: LatLon
    :keyword pushpin_anchor_shift_in_pixels:
        To override the anchor location of the pin image,
        user can designate how to shift or move the anchor location by pixels
    :paramtype pushpin_anchor_shift_in_pixels: int
    :keyword pushpin_color:
        Pushpin color including opacity information.
    :paramtype pushpin_color: str
    :keyword pushpin_scale_ratio:
        Pushpin scale ratio. Value should greater than zero. A value of 1 is the standard scale.
        Values larger than 1 will make the pins larger, and values smaller than 1 will make them smaller.
    :paramtype pushpin_scale_ratio: float
    :keyword custom_pushpin_image_uri:
        Custom pushpin image, can only be 'ref="Uri"' format.
    :paramtype custom_pushpin_image_uri: str
    :keyword label_anchor_shift_in_pixels:
        The anchor location of label for built-in pushpins is at the top center of custom pushpins.
        To override the anchor location of the pin image,
        user can designate how to shift or move the anchor location by pixels
    :paramtype label_anchor_shift_in_pixels: LatLon
    :keyword label_color:
        Label color information. Opacity value other than 1 be ignored.
    :paramtype label_color: str
    :keyword label_scale_ratio:
        Label scale ratio. Should greater than 0. A value of 1 is the standard scale.
        Values larger than 1 will make the label larger.
    :paramtype label_scale_ratio: float
    :keyword rotation_in_degrees:
        A number of degrees of clockwise rotation.
        Use a negative number to rotate counter-clockwise.
        Value can be -360 to 360.
    :paramtype rotation_in_degrees: int
    """
    pushpin_positions: LatLon = None
    pushpin_anchor_shift_in_pixels: int = 0
    pushpin_color: str = None
    pushpin_scale_ratio: float = 0.0
    custom_pushpin_image_uri: str = None
    label_anchor_shift_in_pixels: LatLon = None
    label_color: str = None
    label_scale_ratio: float = 0.0
    rotation_in_degrees: int = 0

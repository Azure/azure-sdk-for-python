# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
Maps SDK converter for Geo Json
This module provides converters to and from GeoJSON geo_interface, etc.
Azure Maps Search uses these converters; they can also be used directly.
"""
import re
from ast import literal_eval
from typing import Union


geo_types = {
    'Point',
    'MultiPoint',
    'LineString',
    'MultiLineString',
    'Polygon',
    'MultiPolygon'
}

wkt_types = {x.upper() for x in geo_types}

type_translations = {x.upper(): x for x in geo_types}

def _reformat_coordinates(
    item: Union[list, tuple],
    style: str
) -> Union[list, tuple]:
    """
    **Reformat Coordinates**

    Converts and reformats coordinate data structures between lists and tuples to ensure compatibility
    with either GeoJSON or geo_interface specifications. This function can handle nested structures
    like lists of lists or tuples of tuples, commonly used in geographical data representations.

    :param item:
        The coordinate data to be reformatted. This can be a single coordinate pair (e.g., `[longitude, latitude]`),
        a list of coordinate pairs (e.g., `[[lng1, lat1], [lng2, lat2], ...]`), or a nested structure of these pairs.
    :type item:
        Union[list, tuple]
    :param style:
        The desired output format of the coordinates. Use 'geojson' to convert all coordinate pairs to lists,
        or 'geo_interface' to convert them to tuples.
    :type style:
        str

    :return:
        The reformatted coordinate data structured as per the specified `style`.
    :rtype:
        Union[list, tuple]

    :raises ValueError:
        If `style` is not 'geojson' or 'geo_interface', indicating an unknown formatting style.
    """
    if type(item) in {tuple, list} and type(item[0]) in {tuple, list}:
        return [_reformat_coordinates(x, style) for x in item]
    if style == 'geojson':
        return list(item)
    if style == 'geo_interface':
        return tuple(item)
    raise ValueError('Unknown style')

def geo_interface_to_geojson(geo_interface: dict) -> dict:
    """
    **Geo Interface to GeoJSON Conversion**

    Transforms a dictionary representing a geographic object in geo_interface format to a GeoJSON
    format dictionary. This conversion ensures the structure of the coordinates is compliant with
    the GeoJSON specification.

    :param geo_interface:
        A dictionary that represents a geographical feature, adhering to the geo_interface format.
        It must include at least 'type' and 'coordinates' keys. For example, a simple point may be
        represented as `{"type": "Point", "coordinates": (x, y)}`, and more complex structures are
        supported for types like `Polygon` or `MultiPoint`.
    :type geo_interface:
        dict

    :return:
        A dictionary formatted according to the GeoJSON specification, representing the same geographical
        feature as the input. This dictionary will include 'type' and 'coordinates' keys at a minimum,
        with additional keys as required by the specific geographical feature type.
    :rtype:
        dict

    :raises ValueError:
        If `geo_interface` does not contain the required keys or if the coordinates cannot be
        successfully reformatted to the GeoJSON format.
    """
    coords = _reformat_coordinates(geo_interface['coordinates'], 'geojson')

    return {'type': geo_interface['type'], 'coordinates': coords}

def wkt_to_geo_interface(wkt: str) -> dict:
    """
    **WKT to Geo Interface Conversion**

    Translates a Well-Known Text (WKT) representation of geographic geometries into a dictionary
    compliant with the geo_interface specification. It supports various geometry types like Point,
    LineString, and Polygon among others.

    :param wkt:
        The Well-Known Text (WKT) representation of the geometry to be converted. WKT is a text
        markup language for representing vector geometry objects on a map.
    :type wkt:
        str

    :return:
        A dictionary formatted according to the geo_interface specification, containing 'type' and
        'coordinates' keys, where 'type' is the geometry type and 'coordinates' is a tuple (or nested
        tuples) representing the geometry's coordinates.
    :rtype:
        dict

    :raises ValueError:
        If the `wkt` string cannot be parsed into a valid geo_interface dictionary, indicating that
        the string is not in a proper WKT format or is unsupported.
    """
    try:
        wkt_type, coords = re.split(r'(?<=[A-Z])\s', wkt)

        geo_type = type_translations[wkt_type]

        # Clean up the strings so they'll covert correctly
        if geo_type in {'Polygon', 'MultiLineString', 'MultiPolygon'}:
            coords = re.sub(r'(?<=\d)\), \((?=\d)', ')), ((', coords)

        # Pairs of coordinates must be enclosed in parentheses
        coords = re.sub(r'(?<=\d), (?=\d)', '), (', coords)

        # Coordinates within parentheses must be separated by commas
        coords = re.sub(r'(?<=\d) (?=\d)', ', ', coords)

        # Now we can turn the string into a tuple or a tuple of tuples
        coords = literal_eval(coords)

        coords = _reformat_coordinates(coords, 'geo_interface')  # type: ignore  # noqa: E501

        # If we only have a simple polygon (no hole), the coordinate array
        # won't be deep enough to satisfy the GeoJSON/geo_interface spec, so
        # we need to enclose it in a list.
        numbers = {float, int}
        if geo_type == 'Polygon' and type(coords[0][0]) in numbers:
            coords = [coords]  # type: ignore
        elif geo_type == 'MultiPolygon' and type(coords[0][0][0]) in numbers:
            coords = [coords]  # type: ignore

    except Exception as ex:
        raise ValueError('{} is not a WKT string'.format(wkt)) from ex

    return {'type': geo_type, 'coordinates': coords}

def wkt_to_geojson(wkt: str) -> str:
    """
    **WKT to GeoJSON Conversion**

    Transforms a Well-Known Text (WKT) string into its corresponding GeoJSON string representation.
    This function leverages the geo_interface format as an intermediate step to ensure accurate
    translation from WKT to GeoJSON.

    :param wkt:
        The Well-Known Text (WKT) representation of the geometry to be converted. WKT is a standard
        text notation for representing vector geometry objects.
    :type wkt:
        str

    :return:
        A string formatted in GeoJSON representing the same geometric object as defined in the input WKT.
    :rtype:
        str

    :raises ValueError:
        If the `wkt` string cannot be converted into GeoJSON, indicating that the WKT string is not in
        a valid format or represents a geometry type that is not supported.
    """
    return geo_interface_to_geojson(wkt_to_geo_interface(wkt))

def parse_geometry_input(geo_thing: Union[str, dict]) -> dict:
    """
    **Parse Geometry Input**

    Interprets various input formats and standardizes them into a GeoJSON dictionary. This function
    can handle GeoJSON strings, Well-Known Text (WKT) strings, GeoJSON-like dictionaries, and objects
    that implement the `__geo_interface__` protocol.

    :param geo_thing:
        The geometry input to parse, which can be one of the following:
        - A GeoJSON string.
        - A WKT string.
        - A dictionary with 'type' and 'coordinates' keys that follows the GeoJSON structure.
        - An object that has a `__geo_interface__` property representing the geometry.
    :type geo_thing:
        Union[str, dict]

    :return:
        A dictionary with a 'geometry' key containing the standardized geometry in GeoJSON format.
    :rtype:
        dict

    :raises ValueError:
        If the string input is not a valid GeoJSON or WKT representation, or if a dictionary input
        does not conform to the GeoJSON structure.
    :raises AttributeError:
        If the input is an object lacking a `__geo_interface__` property.
    """
    error_msg = 'Strings must be valid GeoJSON or WKT or geo_interface property'
    geometry={}
    # Input might be WKT
    if isinstance(geo_thing, str):
        wkt_type = geo_thing.split(' ')[0]
        if wkt_type not in wkt_types:
            raise ValueError(error_msg)
        geom = wkt_to_geojson(geo_thing)
    elif isinstance(geo_thing, dict):
        try:
            # geo_interface property contains coordinates as tuple type
            if isinstance(geo_thing.get("coordinates"), tuple):
                geom = geo_interface_to_geojson(geo_thing)
            # or assume it is a valid Geo Json obejct
            else:
                geom = geo_thing
        except ValueError as ex:
            raise ValueError(error_msg) from ex
    else:
        # Input might be an object with a geo_interface
        try:
            geo_interface = geo_thing.__geo_interface__
            geom = geo_interface_to_geojson(geo_interface)
        except AttributeError as ex:
            raise AttributeError('Object has no geo_interface.') from ex

    geometry['geometry'] = geom
    return geometry

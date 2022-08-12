# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
Maps SDK converter for Geo Json
This module provides converters to and from GeoJSON geo_interface, etc.
Azure Maps Search uses these converters; they can also be used directly.
"""
import json
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

def reformat_coordinates(item, style):
    # type: (Union[list, tuple], str) -> Union[list, tuple]
    """
    Converts tuples, tuples of tuples, lists of tuples, etc. into lists and
    lists of lists, etc. and preserves points/coordinate pairs as lists or
    tuples depending on the desired style.
    """
    if type(item) in {tuple, list} and type(item[0]) in {tuple, list}:
        return [reformat_coordinates(x, style) for x in item]
    if style == 'geojson':
        return list(item)
    raise ValueError('Unknown style')

def geo_interface_to_geojson(geo_interface):
    # type: (dict) -> dict
    """Converts a geo_interface dictionary into a raw GeoJSON dictionary."""
    coords = reformat_coordinates(geo_interface['coordinates'], 'geojson')

    return {'type': geo_interface['type'], 'coordinates': coords}

def wkt_to_geo_interface(wkt):
    # type: (str) -> dict
    """Converts a WKT string to a geo_interface dictionary."""
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

        coords = reformat_coordinates(coords, 'geo_interface')  # type: ignore  # noqa: E501

        # If we only have a simple polygon (no hole), the coordinate array
        # won't be deep enough to satisfy the GeoJSON/geo_interface spec, so
        # we need to enclose it in a list.
        numbers = {float, int}
        if geo_type == 'Polygon' and type(coords[0][0]) in numbers:
            coords = [coords]  # type: ignore
        elif geo_type == 'MultiPolygon' and type(coords[0][0][0]) in numbers:
            coords = [coords]  # type: ignore

    except Exception:
        raise ValueError('{} is not a WKT string'.format(wkt))

    return {'type': geo_type, 'coordinates': coords}

def wkt_to_geojson(wkt):
    # type: (str) -> str
    """Converts a WKT string to serialized GeoJSON."""
    return json.dumps(geo_interface_to_geojson(wkt_to_geo_interface(wkt)))

def parse_geometry_input(geo_thing):
    # type: (...) -> dict
    """Checks to see if the string is geojson or WKT or geo_interface property"""
    error_msg = 'Strings must be valid GeoJSON or WKT or geo_interface property'
    geometry={}
    if isinstance(geo_thing, object):
        try:
            # geo_interface property contains coordinates as tuple type
            if isinstance(geo_thing.get("coordinates"), tuple):
                geom = geo_interface_to_geojson(geo_thing)
            # or assume it is a valid Geo Json obejct
            else:
                geom = geo_thing
        except ValueError:
            raise ValueError(error_msg)
    else:
        wkt_type = geo_thing.split(' ')[0]
        if wkt_type not in wkt_types:
            raise ValueError(error_msg)
        geom = wkt_to_geojson(geo_thing)
    geometry['geometry'] = geom
    return geometry

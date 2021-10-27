# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import base64
from json import JSONEncoder
from typing import Union, cast
from datetime import datetime, date, time, timedelta
from .utils._utils import _FixedOffset



__all__ = ["NULL", "AzureJSONEncoder"]



class _Null(object):
    """To create a Falsy object"""

    def __bool__(self):
        return False

    __nonzero__ = __bool__  # Python2 compatibility


NULL = _Null()
"""
A falsy sentinel object which is supposed to be used to specify attributes
with no data. This gets serialized to `null` on the wire.
"""


def _timedelta_as_isostr(td):
    # type: (timedelta) -> str
    """Converts a datetime.timedelta object into an ISO 8601 formatted string, e.g. 'P4DT12H30M05S'

    Function adapted from the Tin Can Python project: https://github.com/RusticiSoftware/TinCanPython
    """

    # Split seconds to larger units
    seconds = td.total_seconds()
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)

    days, hours, minutes = list(map(int, (days, hours, minutes)))
    seconds = round(seconds, 6)

    # Build date
    date_str = ""
    if days:
        date_str = "%sD" % days

    # Build time
    time_str = "T"

    # Hours
    bigger_exists = date_str or hours
    if bigger_exists:
        time_str += "{:02}H".format(hours)

    # Minutes
    bigger_exists = bigger_exists or minutes
    if bigger_exists:
        time_str += "{:02}M".format(minutes)

    # Seconds
    try:
        if seconds.is_integer():
            seconds_string = "{:02}".format(int(seconds))
        else:
            # 9 chars long w/ leading 0, 6 digits after decimal
            seconds_string = "%09.6f" % seconds
            # Remove trailing zeros
            seconds_string = seconds_string.rstrip("0")
    except AttributeError:  # int.is_integer() raises
        seconds_string = "{:02}".format(seconds)

    time_str += "{}S".format(seconds_string)

    return "P" + date_str + time_str


def _datetime_as_isostr(dt):
    # type: (Union[datetime, date, time, timedelta]) -> str
    """Converts a datetime.(datetime|date|time|timedelta) object into an ISO 8601 formatted string"""
    # First try datetime.datetime
    if hasattr(dt, "year") and hasattr(dt, "hour"):
        dt = cast(datetime, dt)
        # astimezone() fails for naive times in Python 2.7, so make make sure dt is aware (tzinfo is set)
        if not dt.tzinfo:
            iso_formatted = dt.replace(tzinfo=TZ_UTC).isoformat()
        else:
            iso_formatted = dt.astimezone(TZ_UTC).isoformat()
        # Replace the trailing "+00:00" UTC offset with "Z" (RFC 3339: https://www.ietf.org/rfc/rfc3339.txt)
        return iso_formatted.replace("+00:00", "Z")
    # Next try datetime.date or datetime.time
    try:
        dt = cast(Union[date, time], dt)
        return dt.isoformat()
    # Last, try datetime.timedelta
    except AttributeError:
        dt = cast(timedelta, dt)
        return _timedelta_as_isostr(dt)


try:
    from datetime import timezone

    TZ_UTC = timezone.utc  # type: ignore
except ImportError:
    TZ_UTC = _FixedOffset(0)  # type: ignore


class AzureJSONEncoder(JSONEncoder):
    """A JSON encoder that's capable of serializing datetime objects and bytes."""

    def default(self, o):  # pylint: disable=too-many-return-statements
        if isinstance(o, (bytes, bytearray)):
            return base64.b64encode(o).decode()
        try:
            return super(AzureJSONEncoder, self).default(o)
        except TypeError:
            if isinstance(o, (bytes, bytearray)):
                return base64.b64encode(o).decode()
            try:
                # First try datetime.datetime
                if hasattr(o, "year") and hasattr(o, "hour"):
                    # astimezone() fails for naive times in Python 2.7, so make make sure o is aware (tzinfo is set)
                    if not o.tzinfo:
                        iso_formatted = o.replace(tzinfo=TZ_UTC).isoformat()
                    else:
                        iso_formatted = o.astimezone(TZ_UTC).isoformat()
                    # Replace the trailing "+00:00" UTC offset with "Z" (RFC 3339: https://www.ietf.org/rfc/rfc3339.txt)
                    return iso_formatted.replace("+00:00", "Z")
                # Next try datetime.date or datetime.time
                return o.isoformat()
            except AttributeError:
                pass
            # Last, try datetime.timedelta
            try:
                return _timedelta_as_isostr(o)
            except AttributeError:
                # This will be raised when it hits value.total_seconds in the method above
                pass
            return super(AzureJSONEncoder, self).default(o)

def _deserialize(item):
    return item

_SENTINEL = object()

class rest_property:
    def __init__(self, name):
        self._name = name

    def __call__(self, func):
        rest_name = self._name
        def wrapper(self, *args, **kwargs):
            if self._get_rest_name(func.__name__) == _SENTINEL:
                self._set_rest_name(attr_name=func.__name__, rest_name=rest_name)
            return self.__getattr__(func.__name__)
        return wrapper

_MY_MODEL_PROPERTIES = [
    "_attr_name_to_rest_name",
    "_get_rest_name",
    "_set_rest_name",
]


class Model(dict):

    def __eq__(self, other):
        """Compare objects by comparing all attributes."""
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        return super().__eq__(other)

    def __getattr__(self, attr):
        if attr in _MY_MODEL_PROPERTIES:
            return super().__getattribute__(attr)
        if not self.__hasattr__(attr):
            raise AttributeError(
                "{} instance has no attribute '{}'".format(
                    type(self).__name__,
                    attr
                )
            )

        return self.__getitem__(self._get_rest_name(attr))

    def _get_rest_name(self, attr_name):
        if not hasattr(self, "_attr_name_to_rest_name"):
            self._attr_name_to_rest_name = {}
        return self._attr_name_to_rest_name.get(attr_name, _SENTINEL)

    def _set_rest_name(self, attr_name, rest_name):
        if not hasattr(self, "_attr_name_to_rest_name"):
            self._attr_name_to_rest_name = {}
        self._attr_name_to_rest_name[attr_name] = rest_name

    def __setattr__(self, name, value):
        # the properties on the base class
        if name in _MY_MODEL_PROPERTIES:
            super().__setattr__(name, value)
        else:
            self.__setitem__(self._get_rest_name(name), value)

    def __delattr__(self, attr):
        if attr in _MY_MODEL_PROPERTIES:
            return super().__delattr__(attr)
        return self.__delitem__(self._get_rest_name(attr))

    def __hasattr__(self, attr):
        if attr in _MY_MODEL_PROPERTIES:
            return True
        return self._get_rest_name(attr) != _SENTINEL

    def copy(self):
        return Model(self.__dict__)

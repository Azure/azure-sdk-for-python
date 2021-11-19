# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import sys
import logging
import base64
import re
import isodate
from json import JSONEncoder
from typing import Any, Dict, Type, Union, cast, Literal, Optional, ForwardRef
from datetime import datetime, date, time, timedelta
from .utils._utils import _FixedOffset

_LOGGER = logging.getLogger(__name__)

__all__ = ["NULL", "AzureJSONEncoder", "Model", "rest_property"]


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


_VALID_DATE = re.compile(
    r'\d{4}[-]\d{2}[-]\d{2}T\d{2}:\d{2}:\d{2}'
    r'\.?\d*Z?[-+]?[\d{2}]?:?[\d{2}]?')

def _deserialize_datetime(attr: str) -> datetime:
    """Deserialize ISO-8601 formatted string into Datetime object.

    :param str attr: response string to be deserialized.
    :rtype: ~datetime.datetime
    """
    attr = attr.upper()
    match = _VALID_DATE.match(attr)
    if not match:
        raise ValueError("Invalid datetime string: " + attr)

    check_decimal = attr.split('.')
    if len(check_decimal) > 1:
        decimal_str = ""
        for digit in check_decimal[1]:
            if digit.isdigit():
                decimal_str += digit
            else:
                break
        if len(decimal_str) > 6:
            attr = attr.replace(decimal_str, decimal_str[0:6])

    date_obj = isodate.parse_datetime(attr)
    test_utc = date_obj.utctimetuple()
    if test_utc.tm_year > 9999 or test_utc.tm_year < 1:
        raise OverflowError("Hit max or min date")
    return date_obj

def _deserialize_date(attr: str) -> date:
    """Deserialize ISO-8601 formatted string into Date object.
    :param str attr: response string to be deserialized.
    :rtype: Date
    """
    # This must NOT use defaultmonth/defaultday. Using None ensure this raises an exception.
    return isodate.parse_date(attr, defaultmonth=None, defaultday=None)

def _deserialize_time(attr: str) -> time:
    """Deserialize ISO-8601 formatted string into time object.

    :param str attr: response string to be deserialized.
    :rtype: datetime.time
    """
    return isodate.parse_time(attr)


_DESERIALIZE_MAPPING = {
    datetime: _deserialize_datetime,
    date: _deserialize_date,
    time: _deserialize_time,
}

def _get_model(module_name: str, model_name: str):
    module_end = module_name.rsplit('.', 1)[0]
    module = sys.modules[module_end]
    models = {k: v for k, v in module.__dict__.items() if isinstance(v, type)}
    if model_name not in models:
        _LOGGER.warning("Can not find model name in models, will not deserialize")
        return model_name
    return models[model_name]

def _deserialize(obj: Any, deserialization_type, module_name: str) -> Any:
    try:
        if deserialization_type.__origin__ == Literal:
            if obj not in deserialization_type.__args__:
                raise ValueError("Not one of the literal values")
            return obj
    except AttributeError:
        pass

    try:
        # right now, assuming we don't have unions (since we're getting rid of the only)
        # union we used to have in msrest models, which was union of str and enum
        if any(a for a in deserialization_type.__args__ if a == type(None)):
            if obj is None:
                return obj
            return _deserialize(
                obj,
                next(a for  a in deserialization_type.__args__ if a != type(None)),
                module_name
            )
    except (AttributeError):
        pass
    if isinstance(deserialization_type, str) or type(deserialization_type) == ForwardRef:
        try:
            model_name = deserialization_type.__forward_arg__
        except AttributeError:
            model_name = deserialization_type
        deserialization_type = _get_model(module_name, model_name)

    try:
        # i'm a dict-like thing
        return {
            _deserialize(k, deserialization_type.__args__[0], module_name): _deserialize(v, deserialization_type.__args__[1], module_name)
            for k, v in obj.items()
        }
    except (AttributeError, IndexError):
        pass

    if type(obj) in [list, set, tuple]:
        try:
            if len(deserialization_type.__args__) > 1:
                if len(deserialization_type.__args__) > len(obj):
                    raise ValueError("There are more type hints than elements in the iterable.")
                if len(deserialization_type.__args__) < len(obj):
                    raise ValueError("There are more type hints than elements in the iterable.")
                return type(obj)(
                    _deserialize(entry, dt, module_name)
                    for entry, dt in zip(obj, deserialization_type.__args__)
                )
            return type(obj)(
                _deserialize(entry, deserialization_type.__args__[0], module_name)
                for entry in obj
            )
        except (TypeError, IndexError, AttributeError, SyntaxError):
            pass

    try:
        return deserialization_type(obj)
    except Exception:
        return _DESERIALIZE_MAPPING.get(deserialization_type, lambda x: x)(obj)

class Model(dict):

    def __eq__(self, other):
        """Compare objects by comparing all attributes."""
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        return super().__eq__(other)

    def copy(self):
        return Model(self.__dict__)

class rest_property:
    def __init__(self, name: Optional[str] = None):
        self._deserialization_type = None
        self._rest_name = name
        self._module = None

    def __get__(self, obj: Model, type=None):
        return _deserialize(obj.__getitem__(self._rest_name), self._deserialization_type, self._module)

    def __set__(self, obj: Model, value) -> None:
        obj.__setitem__(self._rest_name, value)

    def __delete__(self, obj) -> None:
        obj.__delitem__(self._rest_name)

    def __call__(self, func):
        try:
            self._deserialization_type = func.__annotations__['return']
        except KeyError:
            raise TypeError(f"You need to add a response type annotation to the property {func.__name__}.")
        if not self._rest_name:
            self._rest_name = func.__name__
        self._module = func.__module__
        return self

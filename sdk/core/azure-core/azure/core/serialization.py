# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import functools
import sys
import logging
import base64
import re
import isodate
from json import JSONEncoder
from typing import Any, Callable, Dict, List, Union, cast, Literal, Optional, ForwardRef
from datetime import datetime, date, time, timedelta
from .utils._utils import _FixedOffset

_LOGGER = logging.getLogger(__name__)

__all__ = ["NULL", "AzureJSONEncoder", "Model", "rest_field", "rest_discriminator"]


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

_UNSET = object()

class Model(dict):
    def __init__(self, *args, **kwargs):
        class_name = self.__class__.__name__
        if len(args) > 1:
            raise TypeError(f"{class_name}.__init__() takes 2 positional arguments but {len(args) + 1} were given")
        if "_data" in kwargs:
            raise TypeError(f"{class_name}.__init__() got some positional-only arguments passed as keyword arguments: '_data'")
        if args:
            non_rest_entries = [a for a in args[0] if a not in self._attr_to_rest_name.values() and a in self._attr_to_rest_name]
            if non_rest_entries:
                raise TypeError(
                    f"{class_name}.__init__() got the following unexpected entries: '{', '.join(non_rest_entries)}'"
                )
            super().__init__(args[0])
        else:
            non_attr_kwargs = [k for k in kwargs if k not in self._attr_to_rest_name]
            if non_attr_kwargs:
                # actual type errors only throw the first wrong keyword arg they see, so following that.
                raise TypeError(
                    f"{class_name}.__init__() got an unexpected keyword argument '{non_attr_kwargs[0]}'"
                )
            super().__init__({
                self._attr_to_rest_name[k]: v for k, v in kwargs.items()
            })

    def __eq__(self, other):
        """Compare objects by comparing all attributes."""
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        return super().__eq__(other)

    def copy(self):
        return Model(self.__dict__)

    def __new__(cls, *args: Any, **kwargs: Any):
        # we know the last three classes in mro are going to be 'Model', 'dict', and 'object'
        attr_to_rest_field: Dict[str, _RestField] = { # map attribute name to rest_field property
            k: v
            for mro_class in cls.__mro__[:-3][::-1] # ignore model, dict, and object parents, and reverse the mro order
            for k, v in mro_class.__dict__.items() if k[0] != "_" and hasattr(v, "_type")
        }
        for attr, rest_field in attr_to_rest_field.items():
            rest_field._module = cls.__module__
            if not rest_field._type:
                rest_field._type = rest_field._get_deserialize_callable_from_annotation(cls.__annotations__.get(attr, None))
            if not rest_field._rest_name:
                rest_field._rest_name = attr
        cls._attr_to_rest_name = {
            k: v._rest_name
            for k, v in attr_to_rest_field.items()
        }

        return super().__new__(cls, *args, **kwargs)

class _RestField:
    def __init__(
        self,
        *,
        name: Optional[str] = None,
        type: Optional[Callable] = None,
        is_discriminator: bool = False,
        readonly: bool = False
    ):
        self._type = type
        self._rest_name = name
        self._module: Optional[str] = None
        self._is_discriminator = is_discriminator
        self._readonly = readonly

    def __get__(self, obj: Model, type=None):
        # by this point, type and rest_name will have a value bc we default
        # them in __new__ of the Model class
        return cast(Callable, self._type)(obj.__getitem__(self._rest_name))

    def __set__(self, obj: Model, value) -> None:
        obj.__setitem__(self._rest_name, value)

    def __delete__(self, obj) -> None:
        obj.__delitem__(self._rest_name)

    def _get_deserialize_callable_from_annotation(self, annotation: Any) -> Callable[[Any], Any]:
        default: Callable = lambda x: x
        if not annotation:
            return default

        # is it a literal?
        try:
            if annotation.__origin__ == Literal:
                return default
        except AttributeError:
            pass

        # is it optional?
        try:
            # right now, assuming we don't have unions, since we're getting rid of the only
            # union we used to have in msrest models, which was union of str and enum
            if any(a for a in annotation.__args__ if a == type(None)):

                if_obj_deserializer = self._get_deserialize_callable_from_annotation(
                    next(a for  a in annotation.__args__ if a != type(None)),
                )
                def _deserialize_with_optional(if_obj_deserializer: Callable, obj):
                    if obj is None:
                        return obj
                    return if_obj_deserializer(obj)

                return functools.partial(_deserialize_with_optional, if_obj_deserializer)
        except (AttributeError):
            pass


        # is it a forward ref / in quotes?
        if isinstance(annotation, str) or type(annotation) == ForwardRef:
            try:
                model_name = annotation.__forward_arg__  # type: ignore
            except AttributeError:
                model_name = annotation
            if self._module is not None:
                annotation = _get_model(self._module, model_name)

        try:
            if annotation._name == "Dict":
                key_deserializer = self._get_deserialize_callable_from_annotation(annotation.__args__[0])
                value_deserializer = self._get_deserialize_callable_from_annotation(annotation.__args__[1])
                def _deserialize_dict(
                    key_deserializer: Callable,
                    value_deserializer: Callable,
                    obj: Dict[Any, Any]
                ):
                    return {
                        key_deserializer(k): value_deserializer(v)
                        for k, v in obj.items()
                    }
                return functools.partial(
                    _deserialize_dict,
                    key_deserializer,
                    value_deserializer,
                )
        except (AttributeError, IndexError):
            pass
        try:
            if annotation._name in ["List", "Set", "Tuple", "Sequence"]:
                if len(annotation.__args__) > 1:
                    def _deserialize_multiple_sequence(
                        entry_deserializers: List[Callable],
                        obj
                    ):
                        return type(obj)(
                            deserializer(entry)
                            for entry, deserializer in zip(obj, entry_deserializers)
                        )
                    entry_deserializers = [
                        self._get_deserialize_callable_from_annotation(dt)
                        for dt in annotation.__args__
                    ]
                    return functools.partial(
                        _deserialize_multiple_sequence,
                        entry_deserializers
                    )
                deserializer = self._get_deserialize_callable_from_annotation(annotation.__args__[0])
                def _deserialize_sequence(
                    deserializer: Callable,
                    obj,
                ):
                    return type(obj)(
                        deserializer(entry) for entry in obj
                    )
                return functools.partial(
                    _deserialize_sequence,
                    deserializer
                )
        except (TypeError, IndexError, AttributeError, SyntaxError):
            pass

        def _deserialize(
            annotation,
            deserializer_from_mapping,
            obj,
        ):
            try:
                return annotation(**obj)
            except Exception:
                pass

            try:
                return annotation(*obj)
            except Exception:
                pass

            try:
                return annotation(obj)
            except Exception:
                pass
            return deserializer_from_mapping(obj)
        return functools.partial(
            _deserialize,
            annotation,
            _DESERIALIZE_MAPPING.get(annotation, lambda x: x)
        )

def rest_field(*, name: Optional[str] = None, type: Optional[Callable] = None, readonly: bool = False) -> Any:
    return _RestField(name=name, type=type, readonly=readonly)

def rest_discriminator(*, name: Optional[str] = None, type: Optional[Callable] = None) -> Any:
    return _RestField(name=name, type=type, is_discriminator=True)

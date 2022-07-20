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
import typing
from datetime import datetime, date, time, timedelta
from .utils._utils import _FixedOffset
from collections.abc import MutableMapping
from azure.core.exceptions import DeserializationError
import copy

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
    # type: (typing.Union[datetime, date, time, timedelta]) -> str
    """Converts a datetime.(datetime|date|time|timedelta) object into an ISO 8601 formatted string"""
    # First try datetime.datetime
    if hasattr(dt, "year") and hasattr(dt, "hour"):
        dt = typing.cast(datetime, dt)
        # astimezone() fails for naive times in Python 2.7, so make make sure dt is aware (tzinfo is set)
        if not dt.tzinfo:
            iso_formatted = dt.replace(tzinfo=TZ_UTC).isoformat()
        else:
            iso_formatted = dt.astimezone(TZ_UTC).isoformat()
        # Replace the trailing "+00:00" UTC offset with "Z" (RFC 3339: https://www.ietf.org/rfc/rfc3339.txt)
        return iso_formatted.replace("+00:00", "Z")
    # Next try datetime.date or datetime.time
    try:
        dt = typing.cast(typing.Union[date, time], dt)
        return dt.isoformat()
    # Last, try datetime.timedelta
    except AttributeError:
        dt = typing.cast(timedelta, dt)
        return _timedelta_as_isostr(dt)


try:
    from datetime import timezone

    TZ_UTC = timezone.utc  # type: ignore
except ImportError:
    TZ_UTC = _FixedOffset(0)  # type: ignore

def _serialize_bytes(o) -> str:
    return base64.b64encode(o).decode()

def _serialize_datetime(o):
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

def _is_readonly(p):
    try:
        return p._readonly
    except AttributeError:
        return False

class AzureJSONEncoder(JSONEncoder):
    """A JSON encoder that's capable of serializing datetime objects and bytes."""

    def default(self, o):  # pylint: disable=too-many-return-statements
        if _is_model(o):
            readonly_props = [p._rest_name for p in o._attr_to_rest_field.values() if _is_readonly(p)]
            return {k: v for k, v in o.items() if k not in readonly_props}
        if isinstance(o, (bytes, bytearray)):
            return base64.b64encode(o).decode()
        try:
            return super(AzureJSONEncoder, self).default(o)
        except TypeError:
            if isinstance(o, (bytes, bytearray)):
                return _serialize_bytes(o)
            try:
                # First try datetime.datetime
                return _serialize_datetime(o)
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

def _deserialize_datetime(attr: typing.Union[str, datetime]) -> datetime:
    """Deserialize ISO-8601 formatted string into Datetime object.

    :param str attr: response string to be deserialized.
    :rtype: ~datetime.datetime
    """
    if isinstance(attr, datetime):
        # i'm already deserialized
        return attr
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

def _deserialize_date(attr: typing.Union[str, date]) -> date:
    """Deserialize ISO-8601 formatted string into Date object.
    :param str attr: response string to be deserialized.
    :rtype: Date
    """
    # This must NOT use defaultmonth/defaultday. Using None ensure this raises an exception.
    if isinstance(attr, date):
        return attr
    return isodate.parse_date(attr, defaultmonth=None, defaultday=None)

def _deserialize_time(attr: typing.Union[str, time]) -> time:
    """Deserialize ISO-8601 formatted string into time object.

    :param str attr: response string to be deserialized.
    :rtype: datetime.time
    """
    if isinstance(attr, time):
        return attr
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

class _MyMutableMapping(MutableMapping):

    def __init__(self, data: typing.Dict[str, typing.Any]) -> None:
        self._data = copy.deepcopy(data)

    def __contains__(self, key: str) -> bool:  # type: ignore
        return key in self._data

    def __getitem__(self, key: str) -> typing.Any:
        return self._data.__getitem__(key)

    def __setitem__(self, key: str, value: typing.Any) -> None:
        self._data.__setitem__(key, value)

    def __delitem__(self, key: str) -> None:
        self._data.__delitem__(key)

    def __iter__(self) -> typing.Iterator[typing.Any]:
        return self._data.__iter__()

    def __len__(self) -> int:
        return self._data.__len__()

    def __ne__(self, other: typing.Any) -> bool:
        return not self.__eq__(other)

    def keys(self) -> typing.KeysView:
        return self._data.keys()

    def values(self) -> typing.ValuesView:
        return self._data.values()

    def items(self) -> typing.ItemsView:
        return self._data.items()

    def get(self, key: str, default: typing.Any = None) -> typing.Any:
        try:
            return self[key]
        except KeyError:
            return default

    @typing.overload  # type: ignore
    def pop(self, key: str) -> typing.Any:
        ...

    @typing.overload
    def pop(self, key: str, default: typing.Any) -> typing.Any:
        ...

    def pop(self, key: typing.Any, default: typing.Any = _UNSET) -> typing.Any:
        if default is _UNSET:
            return self._data.pop(key)
        return self._data.pop(key, default)

    def popitem(self) -> typing.Tuple[str, typing.Any]:
        return self._data.popitem()

    def clear(self) -> None:
        self._data.clear()

    def update(self, *args: typing.Any, **kwargs: typing.Any) -> None:
        self._data.update(*args, **kwargs)

    @typing.overload  # type: ignore
    def setdefault(self, key: str) -> typing.Any:
        ...

    @typing.overload
    def setdefault(self, key: str, default: typing.Any) -> typing.Any:
        ...

    def setdefault(self, key: typing.Any, default: typing.Any = _UNSET) -> typing.Any:
        if default is _UNSET:
            return self._data.setdefault(key)
        return self._data.setdefault(key, default)

    def __eq__(self, other: typing.Any) -> bool:
        try:
            other_model = self.__class__(other)
        except Exception:
            return False
        return self._data == other_model._data

    def __repr__(self) -> str:
        return str(self._data)

def _is_model(obj: typing.Any) -> bool:
    return getattr(obj, "_is_model", False)

def _serialize(o):
    if isinstance(o, (bytes, bytearray)):
        return _serialize_bytes(o)
    try:
        # First try datetime.datetime
        return _serialize_datetime(o)
    except AttributeError:
        pass
    # Last, try datetime.timedelta
    try:
        return _timedelta_as_isostr(o)
    except AttributeError:
        # This will be raised when it hits value.total_seconds in the method above
        pass
    return o

def _get_rest_field(attr_to_rest_field: typing.Dict[str, "_RestField"], rest_name: str) -> typing.Optional["_RestField"]:
    try:
        return next(rf for rf in attr_to_rest_field.values() if rf._rest_name == rest_name)
    except StopIteration:
        return None


def _create_value(rest_field: typing.Optional["_RestField"], value: typing.Any) -> typing.Any:
    return _deserialize(rest_field._type, value) if (rest_field and rest_field._is_model) else _serialize(value)

class Model(_MyMutableMapping):
    _is_model = True
    def __init__(self, *args, **kwargs):
        class_name = self.__class__.__name__
        if len(args) > 1:
            raise TypeError(f"{class_name}.__init__() takes 2 positional arguments but {len(args) + 1} were given")
        dict_to_pass = {
            rest_field._rest_name: rest_field._default
            for rest_field in self._attr_to_rest_field.values()
            if rest_field._default is not _UNSET
        }
        if args:
            dict_to_pass.update({
                k: _create_value(_get_rest_field(self._attr_to_rest_field, k), v)
                for k, v in args[0].items()
            })
        else:
            non_attr_kwargs = [k for k in kwargs if k not in self._attr_to_rest_field]
            if non_attr_kwargs:
                # actual type errors only throw the first wrong keyword arg they see, so following that.
                raise TypeError(
                    f"{class_name}.__init__() got an unexpected keyword argument '{non_attr_kwargs[0]}'"
                )
            dict_to_pass.update({
                self._attr_to_rest_field[k]._rest_name: _serialize(v) for k, v in kwargs.items()
            })
        super().__init__(dict_to_pass)

    def copy(self):
        return Model(self.__dict__)

    def __new__(cls, *args: typing.Any, **kwargs: typing.Any):
        # we know the last three classes in mro are going to be 'Model', 'dict', and 'object'
        attr_to_rest_field: typing.Dict[str, _RestField] = { # map attribute name to rest_field property
            k: v
            for mro_class in cls.__mro__[:-3][::-1] # ignore model, dict, and object parents, and reverse the mro order
            for k, v in mro_class.__dict__.items() if k[0] != "_" and hasattr(v, "_type")
        }
        for attr, rest_field in attr_to_rest_field.items():
            rest_field._module_input = cls.__module__
            if not rest_field._type:
                rest_field._type = rest_field._get_deserialize_callable_from_annotation(cls.__annotations__.get(attr, None))
            if not rest_field._rest_name_input:
                rest_field._rest_name_input = attr
        cls._attr_to_rest_field: typing.Dict[str, _RestField] = {
            k: v
            for k, v in attr_to_rest_field.items()
        }

        return super().__new__(cls)

def _deserialize(deserializer: typing.Optional[typing.Callable[[typing.Any], typing.Any]], value: typing.Any):
    try:
        return deserializer(value) if deserializer else value
    except Exception as e:
        raise DeserializationError() from e

class _RestField:
    def __init__(
        self,
        *,
        name: typing.Optional[str] = None,
        type: typing.Optional[typing.Callable] = None,
        is_discriminator: bool = False,
        readonly: bool = False,
        default: typing.Any = _UNSET,
    ):
        self._type = type
        self._rest_name_input = name
        self._module_input: typing.Optional[str] = None
        self._is_discriminator = is_discriminator
        self._readonly = readonly
        self._is_model = False
        self._default = default

    @property
    def _rest_name(self) -> str:
        if self._rest_name_input is None:
            raise ValueError("Rest name was never set")
        return self._rest_name_input

    @property
    def _module(self) -> str:
        if self._module_input is None:
            raise ValueError("Module was never set")
        return self._module_input

    def __get__(self, obj: Model, type=None):
        # by this point, type and rest_name will have a value bc we default
        # them in __new__ of the Model class
        item = obj.get(self._rest_name)
        if item is None:
            return item
        return _deserialize(self._type, _serialize(item))

    def __set__(self, obj: Model, value) -> None:
        if value is None:
            # we want to wipe out entries if users set attr to None
            try:
                obj.__delitem__(self._rest_name)
            except KeyError:
                pass
            return
        if self._is_model and not _is_model(value):
            obj.__setitem__(self._rest_name, _deserialize(self._type, value))
        obj.__setitem__(self._rest_name, _serialize(value))

    def _get_deserialize_callable_from_annotation(self, annotation: typing.Any) -> typing.Optional[typing.Callable[[typing.Any], typing.Any]]:
        if not annotation or annotation in [int, float]:
            return None

        try:
            if _is_model(_get_model(self._module, annotation)):
                self._is_model = True
                def _deserialize_model(model_deserializer: typing.Optional[typing.Callable], obj):
                    if _is_model(obj):
                        return obj
                    return _deserialize(model_deserializer, obj)
                return functools.partial(_deserialize_model, _get_model(self._module, annotation))
        except Exception:
            pass

        # is it a literal?
        try:
            if annotation.__origin__ == typing.Literal:
                return None
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
                def _deserialize_with_optional(if_obj_deserializer: typing.Optional[typing.Callable], obj):
                    if obj is None:
                        return obj
                    return _deserialize(if_obj_deserializer, obj)

                return functools.partial(_deserialize_with_optional, if_obj_deserializer)
        except (AttributeError):
            pass


        # is it a forward ref / in quotes?
        if isinstance(annotation, str) or type(annotation) == typing.ForwardRef:
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
                    key_deserializer: typing.Optional[typing.Callable],
                    value_deserializer: typing.Optional[typing.Callable],
                    obj: typing.Dict[typing.Any, typing.Any]
                ):
                    if obj is None:
                        return obj
                    return {
                        _deserialize(key_deserializer, k): _deserialize(value_deserializer, v)
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
                        entry_deserializers: typing.List[typing.Optional[typing.Callable]],
                        obj
                    ):
                        if obj is None:
                            return obj
                        return type(obj)(
                            _deserialize(deserializer, entry)
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
                    deserializer: typing.Optional[typing.Callable],
                    obj,
                ):
                    if obj is None:
                        return obj
                    return type(obj)(
                        _deserialize(deserializer, entry) for entry in obj
                    )
                return functools.partial(
                    _deserialize_sequence,
                    deserializer
                )
        except (TypeError, IndexError, AttributeError, SyntaxError):
            pass

        def _deserialize_default(
            annotation,
            deserializer_from_mapping,
            obj,
        ):
            if obj is None:
                return obj
            try:
                return annotation(obj)
            except Exception:
                pass
            return _deserialize(deserializer_from_mapping, obj)
        return functools.partial(
            _deserialize_default,
            annotation,
            _DESERIALIZE_MAPPING.get(annotation)
        )

def rest_field(
    *,
    name: typing.Optional[str] = None,
    type: typing.Optional[typing.Callable] = None,
    readonly: bool = False,
    default: typing.Any = _UNSET,
) -> typing.Any:
    return _RestField(name=name, type=type, readonly=readonly, default=default)

def rest_discriminator(*, name: typing.Optional[str] = None, type: typing.Optional[typing.Callable] = None) -> typing.Any:
    return _RestField(name=name, type=type, is_discriminator=True)

# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: disable=protected-access, arguments-differ, signature-differs, broad-except
# pyright: reportGeneralTypeIssues=false

import functools
import sys
import logging
import base64
import re
import copy
import typing
from datetime import datetime, date, time, timedelta, timezone
from json import JSONEncoder
import isodate
from azure.core.exceptions import DeserializationError
from azure.core import CaseInsensitiveEnumMeta
from azure.core.pipeline import PipelineResponse
from azure.core.serialization import NULL as AzureCoreNull

if sys.version_info >= (3, 9):
    from collections.abc import MutableMapping
else:
    from typing import MutableMapping

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

TZ_UTC = timezone.utc


def _timedelta_as_isostr(td: timedelta) -> str:
    """Converts a datetime.timedelta object into an ISO 8601 formatted string, e.g. 'P4DT12H30M05S'

    Function adapted from the Tin Can Python project: https://github.com/RusticiSoftware/TinCanPython

    :param timedelta td: The timedelta to convert
    :rtype: str
    :return: ISO8601 version of this timedelta
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


def _datetime_as_isostr(dt: typing.Union[datetime, date, time, timedelta]) -> str:
    """Converts a datetime.(datetime|date|time|timedelta) object into an ISO 8601 formatted string

    :param timedelta dt: The date object to convert
    :rtype: str
    :return: ISO8601 version of this datetime
    """
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
        return p._readonly  # pylint: disable=protected-access
    except AttributeError:
        return False


class AzureJSONEncoder(JSONEncoder):
    """A JSON encoder that's capable of serializing datetime objects and bytes."""

    def default(self, o):  # pylint: disable=too-many-return-statements
        if _is_model(o):
            readonly_props = [
                p._rest_name for p in o._attr_to_rest_field.values() if _is_readonly(p)
            ]  # pylint: disable=protected-access
            return {k: v for k, v in o.items() if k not in readonly_props}
        if isinstance(o, (bytes, bytearray)):
            return base64.b64encode(o).decode()
        if o is AzureCoreNull:
            return None
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


_VALID_DATE = re.compile(r"\d{4}[-]\d{2}[-]\d{2}T\d{2}:\d{2}:\d{2}" + r"\.?\d*Z?[-+]?[\d{2}]?:?[\d{2}]?")


def _deserialize_datetime(attr: typing.Union[str, datetime]) -> datetime:
    """Deserialize ISO-8601 formatted string into Datetime object.

    :param str attr: response string to be deserialized.
    :rtype: ~datetime.datetime
    :returns: The datetime object from that input
    """
    if isinstance(attr, datetime):
        # i'm already deserialized
        return attr
    attr = attr.upper()
    match = _VALID_DATE.match(attr)
    if not match:
        raise ValueError("Invalid datetime string: " + attr)

    check_decimal = attr.split(".")
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
    :rtype: date
    :returns: The date object from that input
    """
    # This must NOT use defaultmonth/defaultday. Using None ensure this raises an exception.
    if isinstance(attr, date):
        return attr
    return isodate.parse_date(attr, defaultmonth=None, defaultday=None)


def _deserialize_time(attr: typing.Union[str, time]) -> time:
    """Deserialize ISO-8601 formatted string into time object.

    :param str attr: response string to be deserialized.
    :rtype: datetime.time
    :returns: The time object from that input
    """
    if isinstance(attr, time):
        return attr
    return isodate.parse_time(attr)


def deserialize_bytes(attr):
    if isinstance(attr, (bytes, bytearray)):
        return attr
    return bytes(base64.b64decode(attr))


def deserialize_duration(attr):
    if isinstance(attr, timedelta):
        return attr
    return isodate.parse_duration(attr)


_DESERIALIZE_MAPPING = {
    datetime: _deserialize_datetime,
    date: _deserialize_date,
    time: _deserialize_time,
    bytes: deserialize_bytes,
    timedelta: deserialize_duration,
    typing.Any: lambda x: x,
}


def _get_model(module_name: str, model_name: str):
    models = {k: v for k, v in sys.modules[module_name].__dict__.items() if isinstance(v, type)}
    module_end = module_name.rsplit(".", 1)[0]
    module = sys.modules[module_end]
    models.update({k: v for k, v in module.__dict__.items() if isinstance(v, type)})
    if isinstance(model_name, str):
        model_name = model_name.split(".")[-1]
    if model_name not in models:
        return model_name
    return models[model_name]


_UNSET = object()


class _MyMutableMapping(MutableMapping[str, typing.Any]):  # pylint: disable=unsubscriptable-object
    def __init__(self, data: typing.Dict[str, typing.Any]) -> None:
        self._data = copy.deepcopy(data)

    def __contains__(self, key: typing.Any) -> bool:
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

    def keys(self) -> typing.KeysView[str]:
        return self._data.keys()

    def values(self) -> typing.ValuesView[typing.Any]:
        return self._data.values()

    def items(self) -> typing.ItemsView[str, typing.Any]:
        return self._data.items()

    def get(self, key: str, default: typing.Any = None) -> typing.Any:
        try:
            return self[key]
        except KeyError:
            return default

    @typing.overload  # type: ignore
    def pop(self, key: str) -> typing.Any:  # pylint: disable=no-member
        ...

    @typing.overload
    def pop(self, key: str, default: typing.Any) -> typing.Any:
        ...

    def pop(self, key: str, default: typing.Any = _UNSET) -> typing.Any:
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

    def setdefault(self, key: str, default: typing.Any = _UNSET) -> typing.Any:
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


def _get_rest_field(
    attr_to_rest_field: typing.Dict[str, "_RestField"], rest_name: str
) -> typing.Optional["_RestField"]:
    try:
        return next(rf for rf in attr_to_rest_field.values() if rf._rest_name == rest_name)
    except StopIteration:
        return None


def _create_value(rf: typing.Optional["_RestField"], value: typing.Any) -> typing.Any:
    return _deserialize(rf._type, value) if (rf and rf._is_model) else _serialize(value)


class Model(_MyMutableMapping):
    _is_model = True

    def __init__(self, *args: typing.Any, **kwargs: typing.Any) -> None:
        class_name = self.__class__.__name__
        if len(args) > 1:
            raise TypeError(f"{class_name}.__init__() takes 2 positional arguments but {len(args) + 1} were given")
        dict_to_pass = {
            rest_field._rest_name: rest_field._default
            for rest_field in self._attr_to_rest_field.values()
            if rest_field._default is not _UNSET
        }
        if args:
            dict_to_pass.update(
                {k: _create_value(_get_rest_field(self._attr_to_rest_field, k), v) for k, v in args[0].items()}
            )
        else:
            non_attr_kwargs = [k for k in kwargs if k not in self._attr_to_rest_field]
            if non_attr_kwargs:
                # actual type errors only throw the first wrong keyword arg they see, so following that.
                raise TypeError(f"{class_name}.__init__() got an unexpected keyword argument '{non_attr_kwargs[0]}'")
            dict_to_pass.update({self._attr_to_rest_field[k]._rest_name: _serialize(v) for k, v in kwargs.items()})
        super().__init__(dict_to_pass)

    def copy(self) -> "Model":
        return Model(self.__dict__)

    def __new__(cls, *args: typing.Any, **kwargs: typing.Any) -> "Model":  # pylint: disable=unused-argument
        # we know the last three classes in mro are going to be 'Model', 'dict', and 'object'
        mros = cls.__mro__[:-3][::-1]  # ignore model, dict, and object parents, and reverse the mro order
        attr_to_rest_field: typing.Dict[str, _RestField] = {  # map attribute name to rest_field property
            k: v for mro_class in mros for k, v in mro_class.__dict__.items() if k[0] != "_" and hasattr(v, "_type")
        }
        annotations = {
            k: v
            for mro_class in mros
            if hasattr(mro_class, "__annotations__")  # pylint: disable=no-member
            for k, v in mro_class.__annotations__.items()  # pylint: disable=no-member
        }
        for attr, rf in attr_to_rest_field.items():
            rf._module = cls.__module__
            if not rf._type:
                rf._type = rf._get_deserialize_callable_from_annotation(annotations.get(attr, None))
            if not rf._rest_name_input:
                rf._rest_name_input = attr
        cls._attr_to_rest_field: typing.Dict[str, _RestField] = dict(attr_to_rest_field.items())

        return super().__new__(cls)  # pylint: disable=no-value-for-parameter

    def __init_subclass__(cls, discriminator: typing.Optional[str] = None) -> None:
        for base in cls.__bases__:
            if hasattr(base, "__mapping__"):  # pylint: disable=no-member
                base.__mapping__[discriminator or cls.__name__] = cls  # type: ignore  # pylint: disable=no-member

    @classmethod
    def _get_discriminator(cls) -> typing.Optional[str]:
        for v in cls.__dict__.values():
            if isinstance(v, _RestField) and v._is_discriminator:  # pylint: disable=protected-access
                return v._rest_name  # pylint: disable=protected-access
        return None

    @classmethod
    def _deserialize(cls, data):
        if not hasattr(cls, "__mapping__"):  # pylint: disable=no-member
            return cls(data)
        discriminator = cls._get_discriminator()
        mapped_cls = cls.__mapping__.get(data.get(discriminator), cls)  # pylint: disable=no-member
        if mapped_cls == cls:
            return cls(data)
        return mapped_cls._deserialize(data)  # pylint: disable=protected-access


def _get_deserialize_callable_from_annotation(  # pylint: disable=too-many-return-statements, too-many-statements
    annotation: typing.Any, module: typing.Optional[str], rf: typing.Optional["_RestField"] = None
) -> typing.Optional[typing.Callable[[typing.Any], typing.Any]]:
    if not annotation or annotation in [int, float]:
        return None

    try:
        if module and _is_model(_get_model(module, annotation)):
            if rf:
                rf._is_model = True

            def _deserialize_model(model_deserializer: typing.Optional[typing.Callable], obj):
                if _is_model(obj):
                    return obj
                return _deserialize(model_deserializer, obj)

            return functools.partial(_deserialize_model, _get_model(module, annotation))
    except Exception:
        pass

    # is it a literal?
    try:
        if sys.version_info >= (3, 8):
            from typing import Literal  # pylint: disable=no-name-in-module, ungrouped-imports
        else:
            from typing_extensions import Literal  # type: ignore  # pylint: disable=ungrouped-imports

        if annotation.__origin__ == Literal:
            return None
    except AttributeError:
        pass

    if getattr(annotation, "__origin__", None) is typing.Union:

        def _deserialize_with_union(union_annotation, obj):
            for t in union_annotation.__args__:
                try:
                    return _deserialize(t, obj, module)
                except DeserializationError:
                    pass
            raise DeserializationError()

        return functools.partial(_deserialize_with_union, annotation)

    # is it optional?
    try:
        # right now, assuming we don't have unions, since we're getting rid of the only
        # union we used to have in msrest models, which was union of str and enum
        if any(a for a in annotation.__args__ if a == type(None)):

            if_obj_deserializer = _get_deserialize_callable_from_annotation(
                next(a for a in annotation.__args__ if a != type(None)), module, rf
            )

            def _deserialize_with_optional(if_obj_deserializer: typing.Optional[typing.Callable], obj):
                if obj is None:
                    return obj
                return _deserialize_with_callable(if_obj_deserializer, obj)

            return functools.partial(_deserialize_with_optional, if_obj_deserializer)
    except AttributeError:
        pass

    # is it a forward ref / in quotes?
    if isinstance(annotation, (str, typing.ForwardRef)):
        try:
            model_name = annotation.__forward_arg__  # type: ignore
        except AttributeError:
            model_name = annotation
        if module is not None:
            annotation = _get_model(module, model_name)

    try:
        if annotation._name == "Dict":
            key_deserializer = _get_deserialize_callable_from_annotation(annotation.__args__[0], module, rf)
            value_deserializer = _get_deserialize_callable_from_annotation(annotation.__args__[1], module, rf)

            def _deserialize_dict(
                key_deserializer: typing.Optional[typing.Callable],
                value_deserializer: typing.Optional[typing.Callable],
                obj: typing.Dict[typing.Any, typing.Any],
            ):
                if obj is None:
                    return obj
                return {
                    _deserialize(key_deserializer, k, module): _deserialize(value_deserializer, v, module)
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
                    entry_deserializers: typing.List[typing.Optional[typing.Callable]], obj
                ):
                    if obj is None:
                        return obj
                    return type(obj)(
                        _deserialize(deserializer, entry, module)
                        for entry, deserializer in zip(obj, entry_deserializers)
                    )

                entry_deserializers = [
                    _get_deserialize_callable_from_annotation(dt, module, rf) for dt in annotation.__args__
                ]
                return functools.partial(_deserialize_multiple_sequence, entry_deserializers)
            deserializer = _get_deserialize_callable_from_annotation(annotation.__args__[0], module, rf)

            def _deserialize_sequence(
                deserializer: typing.Optional[typing.Callable],
                obj,
            ):
                if obj is None:
                    return obj
                return type(obj)(_deserialize(deserializer, entry, module) for entry in obj)

            return functools.partial(_deserialize_sequence, deserializer)
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
            return _deserialize_with_callable(annotation, obj)
        except Exception:
            pass
        return _deserialize_with_callable(deserializer_from_mapping, obj)

    return functools.partial(_deserialize_default, annotation, _DESERIALIZE_MAPPING.get(annotation))


def _deserialize_with_callable(
    deserializer: typing.Optional[typing.Callable[[typing.Any], typing.Any]], value: typing.Any
):
    try:
        if value is None:
            return None
        if deserializer is None:
            return value
        if isinstance(deserializer, CaseInsensitiveEnumMeta):
            try:
                return deserializer(value)
            except ValueError:
                # for unknown value, return raw value
                return value
        if isinstance(deserializer, type) and issubclass(deserializer, Model):
            return deserializer._deserialize(value)
        return typing.cast(typing.Callable[[typing.Any], typing.Any], deserializer)(value)
    except Exception as e:
        raise DeserializationError() from e


def _deserialize(deserializer: typing.Any, value: typing.Any, module: typing.Optional[str] = None) -> typing.Any:
    if isinstance(value, PipelineResponse):
        value = value.http_response.json()
    deserializer = _get_deserialize_callable_from_annotation(deserializer, module)
    return _deserialize_with_callable(deserializer, value)


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
        self._module: typing.Optional[str] = None
        self._is_discriminator = is_discriminator
        self._readonly = readonly
        self._is_model = False
        self._default = default

    @property
    def _rest_name(self) -> str:
        if self._rest_name_input is None:
            raise ValueError("Rest name was never set")
        return self._rest_name_input

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

    def _get_deserialize_callable_from_annotation(
        self, annotation: typing.Any
    ) -> typing.Optional[typing.Callable[[typing.Any], typing.Any]]:
        return _get_deserialize_callable_from_annotation(annotation, self._module, self)


def rest_field(
    *,
    name: typing.Optional[str] = None,
    type: typing.Optional[typing.Callable] = None,
    readonly: bool = False,
    default: typing.Any = _UNSET,
) -> typing.Any:
    return _RestField(name=name, type=type, readonly=readonly, default=default)


def rest_discriminator(
    *, name: typing.Optional[str] = None, type: typing.Optional[typing.Callable] = None
) -> typing.Any:
    return _RestField(name=name, type=type, is_discriminator=True)

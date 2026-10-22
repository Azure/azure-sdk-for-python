# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: disable=protected-access
import base64
from functools import partial
from json import JSONEncoder
from typing import Dict, List, Optional, Union, cast, Any, Type, Callable, Tuple
from datetime import datetime, date, time, timedelta
from datetime import timezone


__all__ = [
    "NULL",
    "CoreJSONEncoder",
    "is_generated_model",
    "attribute_list",
    "TypeHandlerRegistry",
]
TZ_UTC = timezone.utc


class _Null:
    """To create a Falsy object"""

    def __bool__(self) -> bool:
        return False


NULL = _Null()
"""
A falsy sentinel object which is supposed to be used to specify attributes
with no data. This gets serialized to `null` on the wire.
"""


def _timedelta_as_isostr(td: timedelta) -> str:
    """Converts a datetime.timedelta object into an ISO 8601 formatted string, e.g. 'P4DT12H30M05S'

    Function adapted from the Tin Can Python project: https://github.com/RusticiSoftware/TinCanPython

    :param td: The timedelta object to convert
    :type td: datetime.timedelta
    :return: An ISO 8601 formatted string representing the timedelta object
    :rtype: str
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


def _datetime_as_isostr(dt: Union[datetime, date, time, timedelta]) -> str:
    """Converts a datetime.(datetime|date|time|timedelta) object into an ISO 8601 formatted string.

    :param dt: The datetime object to convert
    :type dt: datetime.datetime or datetime.date or datetime.time or datetime.timedelta
    :return: An ISO 8601 formatted string representing the datetime object
    :rtype: str
    """
    # First try datetime.datetime
    if hasattr(dt, "year") and hasattr(dt, "hour"):
        dt = cast(datetime, dt)
        # astimezone() fails for naive times in Python 2.7, so make make sure dt is aware (tzinfo is set)
        if not dt.tzinfo:
            iso_formatted = dt.replace(tzinfo=timezone.utc).isoformat()
        else:
            iso_formatted = dt.astimezone(timezone.utc).isoformat()
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


class TypeHandlerRegistry:
    """A registry for custom serializers and deserializers for specific types or conditions."""

    def __init__(self) -> None:
        self._serializer_types: Dict[Type, Callable] = {}
        self._deserializer_types: Dict[Type, Callable] = {}
        self._serializer_predicates: List[Tuple[Callable[[Any], bool], Callable]] = []
        self._deserializer_predicates: List[Tuple[Callable[[Any], bool], Callable]] = []

        self._serializer_cache: Dict[Type, Optional[Callable]] = {}
        self._deserializer_cache: Dict[Type, Optional[Callable]] = {}

    def register_serializer(
        self, condition: Union[Type, Callable[[Any], bool]]
    ) -> Callable[[Callable[[Any], Dict[str, Any]]], Callable[[Any], Dict[str, Any]]]:
        """Decorator to register a serializer.

        The handler function is expected to take a single argument, the object to serialize,
        and return a dictionary representation of that object.

        Examples:

        .. code-block:: python

            @registry.register_serializer(CustomModel)
            def serialize_single_type(value: CustomModel) -> dict:
                return value.to_dict()

            @registry.register_serializer(lambda x: isinstance(x, BaseModel))
            def serialize_with_condition(value: BaseModel) -> dict:
                return value.to_dict()

            # Called manually for a specific type
            def custom_serializer(value: CustomModel) -> Dict[str, Any]:
                return {"custom": value.custom}

            registry.register_serializer(CustomModel)(custom_serializer)

        :param condition: A type or a callable predicate function that takes an object and returns a bool.
        :type condition: Union[Type, Callable[[Any], bool]]
        :return: A decorator that registers the handler function.
        :rtype: Callable[[Callable[[Any], Dict[str, Any]]], Callable[[Any], Dict[str, Any]]]
        :raises TypeError: If the condition is neither a type nor a callable.
        """

        def decorator(handler_func: Callable[[Any], Dict[str, Any]]) -> Callable[[Any], Dict[str, Any]]:
            if isinstance(condition, type):
                self._serializer_types[condition] = handler_func
            elif callable(condition):
                self._serializer_predicates.append((condition, handler_func))
            else:
                raise TypeError("Condition must be a type or a callable predicate function.")

            self._serializer_cache.clear()
            return handler_func

        return decorator

    def register_deserializer(
        self, condition: Union[Type, Callable[[Any], bool]]
    ) -> Callable[[Callable[[Type, Dict[str, Any]], Any]], Callable[[Type, Dict[str, Any]], Any]]:
        """Decorator to register a deserializer.

        The handler function is expected to take two arguments: the target type and the data dictionary,
        and return an instance of the target type.

        Examples:

        .. code-block:: python

            @registry.register_deserializer(CustomModel)
            def deserialize_single_type(cls: Type[CustomModel], data: dict) -> CustomModel:
                return cls(**data)

            @registry.register_deserializer(lambda t: issubclass(t, BaseModel))
            def deserialize_with_condition(cls: Type[BaseModel], data: dict) -> BaseModel:
                return cls(**data)

            # Called manually for a specific type
            def custom_deserializer(cls: Type[CustomModel], data: Dict[str, Any]) -> CustomModel:
                return cls(custom=data["custom"])

            registry.register_deserializer(CustomModel)(custom_deserializer)

        :param condition: A type or a callable predicate function that takes an object and returns a bool.
        :type condition: Union[Type, Callable[[Any], bool]]
        :return: A decorator that registers the handler function.
        :rtype: Callable[[Callable[[Type, Dict[str, Any]], Any]], Callable[[Type, Dict[str, Any]], Any]]
        :raises TypeError: If the condition is neither a type nor a callable.
        """

        def decorator(handler_func: Callable[[Type, Dict[str, Any]], Any]) -> Callable[[Type, Dict[str, Any]], Any]:
            if isinstance(condition, type):
                self._deserializer_types[condition] = handler_func
            elif callable(condition):
                self._deserializer_predicates.append((condition, handler_func))
            else:
                raise TypeError("Condition must be a type or a callable predicate function.")

            self._deserializer_cache.clear()
            return handler_func

        return decorator

    def get_serializer(self, obj: Any) -> Optional[Callable[[Any], Dict[str, Any]]]:
        """Gets the appropriate serializer for an object.

        It first checks the type dictionary for a direct type match.
        If no match is found, it iterates through the predicate list to find a match.

        Results of the lookup are cached for performance based on the object's type.

        :param obj: The object to serialize.
        :type obj: any
        :return: The serializer function if found, otherwise None.
        :rtype: Optional[Callable[[Any], Dict[str, Any]]]
        """
        obj_type = type(obj)
        if obj_type in self._serializer_cache:
            return self._serializer_cache[obj_type]

        handler = self._serializer_types.get(type(obj))
        if not handler:
            for predicate, pred_handler in self._serializer_predicates:
                if predicate(obj):
                    handler = pred_handler
                    break

        self._serializer_cache[obj_type] = handler
        return handler

    def get_deserializer(self, cls: Type) -> Optional[Callable[[Dict[str, Any]], Any]]:
        """Gets the appropriate deserializer for a class.

        It first checks the type dictionary for a direct type match.
        If no match is found, it iterates through the predicate list to find a match.

        Results of the lookup are cached for performance based on the class.

        :param cls: The class to deserialize.
        :type cls: type
        :return: A deserializer function bound to the specified class that takes a dictionary and returns
            an instance of that class, or None if no deserializer is found.
        :rtype: Optional[Callable[[Dict[str, Any]], Any]]
        """
        if cls in self._deserializer_cache:
            return self._deserializer_cache[cls]

        handler = self._deserializer_types.get(cls)
        if not handler:
            for predicate, pred_handler in self._deserializer_predicates:
                if predicate(cls):
                    handler = pred_handler
                    break

        self._deserializer_cache[cls] = partial(handler, cls) if handler else None
        return self._deserializer_cache[cls]


class CoreJSONEncoder(JSONEncoder):
    """A JSON encoder that's capable of serializing datetime objects and bytes."""

    def default(self, o: Any) -> Any:
        """Override the default method to handle datetime and bytes serialization.

        :param o: The object to serialize.
        :type o: Any
        :return: A JSON-serializable representation of the object.
        :rtype: Any
        """
        if isinstance(o, (bytes, bytearray)):
            return base64.b64encode(o).decode()
        try:
            return _datetime_as_isostr(o)
        except AttributeError:
            pass
        return super(CoreJSONEncoder, self).default(o)


def is_generated_model(obj: Any) -> bool:
    """Check if the object is a generated SDK model.

    :param obj: The object to check.
    :type obj: any
    :return: True if the object is a generated SDK model, False otherwise.
    :rtype: bool
    """
    return bool(getattr(obj, "_is_model", False) or hasattr(obj, "_attribute_map"))


def _get_flattened_attribute(obj: Any) -> Optional[str]:
    """Get the name of the flattened attribute in a generated TypeSpec model if one exists.

    :param any obj: The object to check.
    :return: The name of the flattened attribute if it exists, otherwise None.
    :rtype: Optional[str]
    """
    flattened_items = None
    try:
        flattened_items = getattr(obj, next(a for a in dir(obj) if "__flattened_items" in a), None)
    except StopIteration:
        return None

    if flattened_items is None:
        return None

    for k, v in obj._attr_to_rest_field.items():
        try:
            if set(v._class_type._attr_to_rest_field.keys()).intersection(set(flattened_items)):
                return k
        except AttributeError:
            # if the attribute does not have _class_type, it is not a typespec generated model
            continue
    return None


def attribute_list(obj: Any) -> List[str]:
    """Get a list of attribute names for a generated SDK model.

    :param obj: The object to get attributes from.
    :type obj: any
    :return: A list of attribute names.
    :rtype: List[str]
    """
    if not is_generated_model(obj):
        raise TypeError("Object is not a generated SDK model.")
    if hasattr(obj, "_attribute_map"):
        return list(obj._attribute_map.keys())
    flattened_attribute = _get_flattened_attribute(obj)
    retval: List[str] = []
    for attr_name, rest_field in obj._attr_to_rest_field.items():
        if flattened_attribute == attr_name:
            retval.extend(attribute_list(rest_field._class_type))
        else:
            retval.append(attr_name)
    return retval

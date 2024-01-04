# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from binascii import hexlify
from typing import Callable, Dict, Optional, Union, Any, Mapping, Type, Tuple
from uuid import UUID
from datetime import datetime
from math import isnan
from enum import Enum

from azure.core import MatchConditions

from ._entity import EdmType, TableEntity
from ._common_conversion import _encode_base64, _to_utc_datetime
from ._error import _ERROR_VALUE_TOO_LARGE, _ERROR_TYPE_NOT_SUPPORTED


def _get_match_condition(etag, match_condition):
    if match_condition == MatchConditions.IfNotModified:
        if not etag:
            raise ValueError("IfNotModified must be specified with etag.")
        return match_condition
    if match_condition == MatchConditions.Unconditionally:
        if etag:
            raise ValueError("Etag is not supported for an Unconditional operation.")
        return MatchConditions.IfPresent
    raise ValueError(f"Unsupported match condition: {match_condition}")


def _prepare_key(keyvalue: str) -> str:
    """Duplicate the single quote char to escape.

    :param keyvalue: A key value in table entity.
    :type keyvalue: str
    :return: A key value in table entity.
    :rtype: str
    """
    try:
        return keyvalue.replace("'", "''")
    except AttributeError as exc:
        raise TypeError("PartitionKey or RowKey must be of type string.") from exc


def _parameter_filter_substitution(parameters: Optional[Dict[str, str]], query_filter: str) -> str:
    """Replace user defined parameters in filter.

    :param parameters: User defined parameters
    :type parameters: dict[str, str]
    :param str query_filter: Filter for querying
    :return: A query filter replaced by user defined parameters.
    :rtype: str
    """
    if parameters:
        filter_strings = query_filter.split(" ")
        for index, word in enumerate(filter_strings):
            if word[0] == "@":
                val = parameters[word[1:]]
                if val in [True, False]:
                    filter_strings[index] = str(val).lower()
                elif isinstance(val, (float)):
                    filter_strings[index] = str(val)
                elif isinstance(val, int):
                    if val.bit_length() <= 32:
                        filter_strings[index] = str(val)
                    else:
                        filter_strings[index] = f"{str(val)}L"
                elif isinstance(val, datetime):
                    filter_strings[index] = f"datetime'{_to_utc_datetime(val)}'"
                elif isinstance(val, UUID):
                    filter_strings[index] = f"guid'{str(val)}'"
                elif isinstance(val, bytes):
                    v = str(hexlify(val))
                    if v[0] == "b":  # Python 3 adds a 'b' and quotations, python 2.7 does neither
                        v = v[2:-1]
                    filter_strings[index] = f"X'{v}'"
                else:
                    filter_strings[index] = f"'{_prepare_key(val)}'"
        return " ".join(filter_strings)
    return query_filter


def _to_entity_binary(value):
    return EdmType.BINARY, _encode_base64(value)


def _to_entity_bool(value):
    return None, value


def _to_entity_datetime(value):
    if isinstance(value, str):
        # Pass a serialized datetime straight through
        return EdmType.DATETIME, value
    try:
        # Check is this is a 'round-trip' datetime, and if so
        # pass through the original value.
        if value.tables_service_value:
            return EdmType.DATETIME, value.tables_service_value
    except AttributeError:
        pass
    return EdmType.DATETIME, _to_utc_datetime(value)


def _to_entity_float(value):
    if isinstance(value, str):
        # Pass a serialized value straight through
        return EdmType.DOUBLE, value
    if isnan(value):
        return EdmType.DOUBLE, "NaN"
    if value == float("inf"):
        return EdmType.DOUBLE, "Infinity"
    if value == float("-inf"):
        return EdmType.DOUBLE, "-Infinity"
    return EdmType.DOUBLE, value


def _to_entity_guid(value):
    return EdmType.GUID, str(value)


def _to_entity_int32(value):
    value = int(value)
    if value >= 2**31 or value < -(2**31):
        raise TypeError(_ERROR_VALUE_TOO_LARGE.format(str(value), EdmType.INT32))
    return None, value


def _to_entity_int64(value):
    int_value = int(value)
    if int_value >= 2**63 or int_value < -(2**63):
        raise TypeError(_ERROR_VALUE_TOO_LARGE.format(str(value), EdmType.INT64))
    return EdmType.INT64, str(value)


def _to_entity_str(value):
    return EdmType.STRING, str(value)


def _to_entity_none(value):  # pylint: disable=unused-argument
    return None, None


# Conversion from Python type to a function which returns a tuple of the
# type string and content string.
_PYTHON_TO_ENTITY_CONVERSIONS: Dict[Type, Callable[[Any], Tuple[Optional[EdmType], Any]]] = {
    int: _to_entity_int32,
    bool: _to_entity_bool,
    datetime: _to_entity_datetime,
    float: _to_entity_float,
    UUID: _to_entity_guid,
    Enum: _to_entity_str,
    str: _to_entity_str,
    bytes: _to_entity_binary,
}

# cspell:ignore Odatatype

# Conversion from Edm type to a function which returns a tuple of the
# type string and content string. These conversions are only used when the
# full EdmProperty tuple is specified. As a result, in this case we ALWAYS add
# the Odatatype tag, even for field types where it's not necessary. This is why
# boolean and int32 have special processing below, as we would not normally add the
# Odatatype tags for these to keep payload size minimal.
# This is also necessary for CLI compatibility.
_EDM_TO_ENTITY_CONVERSIONS: Dict[EdmType, Callable[[Any], Tuple[Optional[EdmType], Any]]] = {
    EdmType.BINARY: _to_entity_binary,
    EdmType.BOOLEAN: lambda v: (EdmType.BOOLEAN, v),
    EdmType.DATETIME: _to_entity_datetime,
    EdmType.DOUBLE: _to_entity_float,
    EdmType.GUID: _to_entity_guid,
    EdmType.INT32: lambda v: (EdmType.INT32, _to_entity_int32(v)[1]),  # Still using the int32 validation
    EdmType.INT64: _to_entity_int64,
    EdmType.STRING: _to_entity_str,
}


def _add_entity_properties(source: Union[TableEntity, Mapping[str, Any]]) -> Dict[str, Any]:
    """Converts an entity object to json to send.
    The entity format is:
    {
       "Address":"Mountain View",
       "Age":23,
       "AmountDue":200.23,
       "CustomerCode@odata.type":"Edm.Guid",
       "CustomerCode":"c9da6455-213d-42c9-9a79-3e9149a57833",
       "CustomerSince@odata.type":"Edm.DateTime",
       "CustomerSince":"2008-07-10T00:00:00",
       "IsActive":true,
       "NumberOfOrders@odata.type":"Edm.Int64",
       "NumberOfOrders":"255",
       "PartitionKey":"my_partition_key",
       "RowKey":"my_row_key"
    }

    :param source: A table entity.
    :type source: ~azure.data.tables.TableEntity or Mapping[str, Any]
    :return: An entity with property's metadata in JSON format.
    :rtype: dict
    """

    properties = {}

    to_send = dict(source)  # shallow copy

    # set properties type for types we know if value has no type info.
    # if value has type info, then set the type to value.type
    for name, value in to_send.items():
        if value is None:
            continue
        mtype: Optional[EdmType] = None
        if isinstance(value, Enum):
            convert = _PYTHON_TO_ENTITY_CONVERSIONS[str]
            mtype, value = convert(value)
        elif isinstance(value, datetime):
            mtype, value = _to_entity_datetime(value)
        elif isinstance(value, tuple):
            if value[0] is None:
                continue
            convert = _EDM_TO_ENTITY_CONVERSIONS[EdmType(value[1])]
            mtype, value = convert(value[0])
        else:
            try:
                convert = _PYTHON_TO_ENTITY_CONVERSIONS[type(value)]
            except KeyError:
                raise TypeError(_ERROR_TYPE_NOT_SUPPORTED.format(type(value))) from None
            mtype, value = convert(value)

        # form the property node
        properties[name] = value
        if mtype:
            properties[name + "@odata.type"] = mtype.value

    # generate the entity_body
    return properties


def serialize_iso(attr: Optional[Union[str, datetime]]) -> Optional[str]:
    """Serialize Datetime object into ISO-8601 formatted string.

    :param attr: Object to be serialized.
    :type attr: str or ~datetime.datetime or None
    :return: A ISO-8601 formatted string or None
    :rtype: str or None
    :raises ValueError: When unable to serialize the input object.
    :raises TypeError: When ISO-8601 object is an invalid datetime object.
    """
    if not attr:
        return None
    if isinstance(attr, str):
        # Pass a string through unaltered
        return attr
    try:
        utc = attr.utctimetuple()
        if utc.tm_year > 9999 or utc.tm_year < 1:
            raise OverflowError("Hit max or min date")

        date = f"{utc.tm_year:04}-{utc.tm_mon:02}-{utc.tm_mday:02}T{utc.tm_hour:02}:{utc.tm_min:02}:{utc.tm_sec:02}"
        return date + "Z"
    except (ValueError, OverflowError) as err:
        raise ValueError("Unable to serialize datetime object.") from err
    except AttributeError as err:
        raise TypeError("ISO-8601 object must be valid datetime object.") from err

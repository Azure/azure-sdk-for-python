# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from uuid import UUID
from datetime import datetime
from math import isnan
from enum import Enum
import sys
import uuid
import isodate

from azure.core import MatchConditions
from azure.core.exceptions import raise_with_traceback

from ._entity import EdmType, EntityProperty
from ._models import TablePayloadFormat
from ._common_conversion import _to_str, _encode_base64, _to_utc_datetime
from ._error import _ERROR_VALUE_TOO_LARGE, _ERROR_TYPE_NOT_SUPPORTED


_SUPPORTED_API_VERSIONS = ["2019-02-02", "2019-07-07"]


def _get_match_headers(kwargs, match_param, etag_param):
    if_match = None
    if_none_match = None
    match_condition = kwargs.pop(match_param, None)
    if match_condition == MatchConditions.IfNotModified:
        if_match = kwargs.pop(etag_param, None)
        if not if_match:
            raise ValueError(
                "'{}' specified without '{}'.".format(match_param, etag_param)
            )
    elif match_condition == MatchConditions.IfPresent:
        if_match = "*"
    elif match_condition == MatchConditions.IfModified:
        if_none_match = kwargs.pop(etag_param, None)
        if not if_none_match:
            raise ValueError(
                "'{}' specified without '{}'.".format(match_param, etag_param)
            )
    elif match_condition == MatchConditions.IfMissing:
        if_none_match = "*"
    elif match_condition == MatchConditions.Unconditionally:
        if_none_match = "*"
    elif match_condition is None:
        if kwargs.get(etag_param):
            raise ValueError(
                "'{}' specified without '{}'.".format(etag_param, match_param)
            )
    else:
        raise TypeError("Invalid match condition: {}".format(match_condition))
    return if_match, if_none_match


def get_api_version(kwargs, default):
    # type: (Dict[str, Any]) -> str
    api_version = kwargs.pop("api_version", None)
    if api_version and api_version not in _SUPPORTED_API_VERSIONS:
        versions = "\n".join(_SUPPORTED_API_VERSIONS)
        raise ValueError(
            "Unsupported API version '{}'. Please select from:\n{}".format(
                api_version, versions
            )
        )
    return api_version or default


if sys.version_info < (3,):

    def _new_boundary():
        return str(uuid.uuid1())


else:

    def _new_boundary():
        return str(uuid.uuid1()).encode("utf-8")


_DEFAULT_ACCEPT_HEADER = ("Accept", TablePayloadFormat.JSON_MINIMAL_METADATA)
_DEFAULT_CONTENT_TYPE_HEADER = ("Content-Type", "application/json")
_DEFAULT_PREFER_HEADER = ("Prefer", "return-no-content")
_SUB_HEADERS = ["If-Match", "Prefer", "Accept", "Content-Type", "DataServiceVersion"]


def _get_entity_path(table_name, partition_key, row_key):
    return "/{0}(PartitionKey='{1}',RowKey='{2}')".format(
        _to_str(table_name),
        _to_str(partition_key.replace("'", "''")),
        _to_str(row_key.replace("'", "''")),
    )


def _update_storage_table_header(request):
    """ add additional headers for storage table request. """

    # set service version
    request.headers["DataServiceVersion"] = "3.0;NetFx"
    request.headers["MaxDataServiceVersion"] = "3.0"


def _to_entity_binary(value):
    return EdmType.BINARY, _encode_base64(value)


def _to_entity_bool(value):
    return None, value


def _to_entity_datetime(value):
    return EdmType.DATETIME, _to_utc_datetime(value)


def _to_entity_float(value):
    if isnan(value):
        return EdmType.DOUBLE, "NaN"
    if value == float("inf"):
        return EdmType.DOUBLE, "Infinity"
    if value == float("-inf"):
        return EdmType.DOUBLE, "-Infinity"
    return None, value


def _to_entity_guid(value):
    return EdmType.GUID, str(value)


def _to_entity_int32(value):
    value = int(value)
    if value >= 2 ** 31 or value < -(2 ** 31):
        raise TypeError(_ERROR_VALUE_TOO_LARGE.format(str(value), EdmType.INT32))
    return None, value


def _to_entity_int64(value):
    if sys.version_info < (3,):
        ivalue = int(value)
    else:
        ivalue = int(value)
    if ivalue >= 2 ** 63 or ivalue < -(2 ** 63):
        raise TypeError(_ERROR_VALUE_TOO_LARGE.format(str(value), EdmType.INT64))
    return EdmType.INT64, str(value)


def _to_entity_int(value):
    ivalue = int(value)
    if ivalue.bit_length() <= 32:
        return _to_entity_int32(value)
    if ivalue.bit_length() <= 64:
        return _to_entity_int64(value)
    raise TypeError(_ERROR_VALUE_TOO_LARGE.format(str(value), EdmType.INT64))


def _to_entity_str(value):
    return EdmType.STRING, value


def _to_entity_none(value):  # pylint: disable=unused-argument
    return None, None


# Conversion from Python type to a function which returns a tuple of the
# type string and content string.
_PYTHON_TO_ENTITY_CONVERSIONS = {
    int: _to_entity_int32,
    bool: _to_entity_bool,
    datetime: _to_entity_datetime,
    float: _to_entity_float,
    UUID: _to_entity_guid,
    Enum: _to_entity_str,
}
try:
    _PYTHON_TO_ENTITY_CONVERSIONS.update(
        {
            unicode: _to_entity_str,
            str: _to_entity_binary,
            long: _to_entity_int32,
        }
    )
except NameError:
    _PYTHON_TO_ENTITY_CONVERSIONS.update(
        {
            str: _to_entity_str,
            bytes: _to_entity_binary,
        }
    )

# Conversion from Edm type to a function which returns a tuple of the
# type string and content string.
_EDM_TO_ENTITY_CONVERSIONS = {
    EdmType.BINARY: _to_entity_binary,
    EdmType.BOOLEAN: _to_entity_bool,
    EdmType.DATETIME: _to_entity_datetime,
    EdmType.DOUBLE: _to_entity_float,
    EdmType.GUID: _to_entity_guid,
    EdmType.INT32: _to_entity_int32,
    EdmType.INT64: _to_entity_int64,
    EdmType.STRING: _to_entity_str,
}


def _add_entity_properties(source):
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
       "PartitionKey":"mypartitionkey",
       "RowKey":"myrowkey"
    }
    """

    properties = {}

    to_send = dict(source)  # shallow copy
    to_send.pop("_metadata", None)

    # set properties type for types we know if value has no type info.
    # if value has type info, then set the type to value.type
    for name, value in to_send.items():
        mtype = ""

        if isinstance(value, Enum):
            try:
                conv = _PYTHON_TO_ENTITY_CONVERSIONS.get(unicode)
            except NameError:
                conv = _PYTHON_TO_ENTITY_CONVERSIONS.get(str)
            mtype, value = conv(value)
        elif isinstance(value, EntityProperty):
            conv = _EDM_TO_ENTITY_CONVERSIONS.get(value.type)
            if conv is None:
                raise TypeError(_ERROR_TYPE_NOT_SUPPORTED.format(value.type))
            mtype, value = conv(value.value)
        else:
            conv = _PYTHON_TO_ENTITY_CONVERSIONS.get(type(value))
            if conv is None and value is not None:
                raise TypeError(_ERROR_TYPE_NOT_SUPPORTED.format(type(value)))
            if value is None:
                conv = _to_entity_none

            mtype, value = conv(value)

        # form the property node
        if value is not None:
            properties[name] = value
            if mtype:
                properties[name + "@odata.type"] = mtype.value

    # generate the entity_body
    return properties


def serialize_iso(attr):
    """Serialize Datetime object into ISO-8601 formatted string.

    :param Datetime attr: Object to be serialized.
    :rtype: str
    :raises ValueError: If format is invalid.
    """
    if not attr:
        return None
    if isinstance(attr, str):
        attr = isodate.parse_datetime(attr)
    try:
        utc = attr.utctimetuple()
        if utc.tm_year > 9999 or utc.tm_year < 1:
            raise OverflowError("Hit max or min date")

        date = "{:04}-{:02}-{:02}T{:02}:{:02}:{:02}".format(
            utc.tm_year, utc.tm_mon, utc.tm_mday, utc.tm_hour, utc.tm_min, utc.tm_sec
        )
        return date + "Z"
    except (ValueError, OverflowError) as err:
        msg = "Unable to serialize datetime object."
        raise_with_traceback(ValueError, msg, err)
    except AttributeError as err:
        msg = "ISO-8601 object must be valid Datetime object."
        raise_with_traceback(TypeError, msg, err)

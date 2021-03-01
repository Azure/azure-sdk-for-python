# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from typing import TYPE_CHECKING
from uuid import UUID
import logging
import datetime

from azure.core.exceptions import ResourceExistsError

from ._entity import EntityProperty, EdmType, TableEntity
from ._common_conversion import _decode_base64_to_bytes
from ._error import TableErrorCode

if TYPE_CHECKING:
    from datetime import datetime
    from azure.core.exceptions import AzureError


_LOGGER = logging.getLogger(__name__)

try:
    from urllib.parse import quote
except ImportError:
    from urllib2 import quote  # type: ignore

if TYPE_CHECKING:
    from typing import (  # pylint: disable=ungrouped-imports
        Union,
        Optional,
        Any,
        Iterable,
        Dict,
        List,
        Type,
        Tuple,
    )


def url_quote(url):
    return quote(url)


def get_enum_value(value):
    if value is None or value in ["None", ""]:
        return None
    try:
        return value.value
    except AttributeError:
        return value


def _deserialize_table_creation(response, _, headers):
    if response.status_code == 204:
        error_code = TableErrorCode.table_already_exists
        error = ResourceExistsError(
            message="Table already exists\nRequestId:{}\nTime:{}\nErrorCode:{}".format(
                headers["x-ms-request-id"], headers["Date"], error_code
            ),
            response=response,
        )
        error.error_code = error_code
        error.additional_info = {}
        raise error
    return headers


def _from_entity_binary(value):
    return EntityProperty(_decode_base64_to_bytes(value))


def _from_entity_int32(value):
    return EntityProperty(int(value))


def _from_entity_int64(value):
    return EntityProperty(int(value), EdmType.INT64)


zero = datetime.timedelta(0)  # same as 00:00


class Timezone(datetime.tzinfo):
    def utcoffset(self, dt):
        return zero

    def dst(self, dt):
        return zero

    def tzname(self, dt):
        return


def _from_entity_datetime(value):
    # Cosmos returns this with a decimal point that throws an error on deserialization
    value = clean_up_dotnet_timestamps(value)

    try:
        return datetime.datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%fZ").replace(
            tzinfo=Timezone()
        )
    except ValueError:
        return datetime.datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ").replace(
            tzinfo=Timezone()
        )


def clean_up_dotnet_timestamps(value):
    # .NET has more decimal places than Python supports in datetime objects, this truncates
    # values after 6 decimal places.
    value = value.split(".")
    ms = ""
    if len(value) == 2:
        ms = value[-1].replace("Z", "")
        if len(ms) > 6:
            ms = ms[:6]
        ms = ms + "Z"
        return ".".join([value[0], ms])

    return value[0]



def _from_entity_guid(value):
    return UUID(value)


def _from_entity_str(value):
    return EntityProperty(value=value, type=EdmType.STRING)


_EDM_TYPES = [
    EdmType.BINARY,
    EdmType.INT64,
    EdmType.GUID,
    EdmType.DATETIME,
    EdmType.STRING,
    EdmType.INT32,
    EdmType.DOUBLE,
    EdmType.BOOLEAN,
]

_ENTITY_TO_PYTHON_CONVERSIONS = {
    EdmType.BINARY: _from_entity_binary,
    EdmType.INT32: _from_entity_int32,
    EdmType.INT64: _from_entity_int64,
    EdmType.DOUBLE: float,
    EdmType.DATETIME: _from_entity_datetime,
    EdmType.GUID: _from_entity_guid,
    EdmType.STRING: _from_entity_str,
}


def _convert_to_entity(entry_element):
    """Convert json response to entity.
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
    entity = TableEntity()

    properties = {}
    edmtypes = {}
    odata = {}

    for name, value in entry_element.items():
        if name.startswith("odata."):
            odata[name[6:]] = value
        elif name.endswith("@odata.type"):
            edmtypes[name[:-11]] = value
        else:
            properties[name] = value

    # Partition key is a known property
    partition_key = properties.pop("PartitionKey", None)
    if partition_key:
        entity["PartitionKey"] = partition_key

    # Row key is a known property
    row_key = properties.pop("RowKey", None)
    if row_key:
        entity["RowKey"] = row_key

    # Timestamp is a known property
    timestamp = properties.pop("Timestamp", None)
    if timestamp:
        # entity['Timestamp'] = _from_entity_datetime(timestamp)
        entity["Timestamp"] = timestamp

    for name, value in properties.items():
        mtype = edmtypes.get(name)

        # Add type for Int32
        if isinstance(value, int) and mtype is None:
            mtype = EdmType.INT32

            if value >= 2 ** 31 or value < (-(2 ** 31)):
                mtype = EdmType.INT64

        # Add type for String
        try:
            if isinstance(value, unicode) and mtype is None:
                mtype = EdmType.STRING
        except NameError:
            if isinstance(value, str) and mtype is None:
                mtype = EdmType.STRING

        # no type info, property should parse automatically
        if not mtype:
            entity[name] = value
        elif mtype in [EdmType.STRING, EdmType.INT32]:
            entity[name] = value
        else:  # need an object to hold the property
            conv = _ENTITY_TO_PYTHON_CONVERSIONS.get(mtype)
            if conv is not None:
                new_property = conv(value)
            else:
                new_property = EntityProperty(mtype, value)
            entity[name] = new_property

    # extract etag from entry
    etag = odata.get("etag")
    if timestamp and not etag:
        etag = "W/\"datetime'" + url_quote(timestamp) + "'\""
    entity["etag"] = etag

    entity._set_metadata()  # pylint: disable=protected-access
    return entity


def _extract_etag(response):
    """ Extracts the etag from the response headers. """
    if response and response.headers:
        return response.headers.get("etag")

    return None


def _extract_continuation_token(continuation_token):
    """Extract list entity continuation headers from token.

    :param dict(str,str) continuation_token: The listing continuation token.
    :returns: The next partition key and next row key in a tuple
    :rtype: (str,str)
    """
    if not continuation_token:
        return None, None
    try:
        return continuation_token.get("PartitionKey"), continuation_token.get("RowKey")
    except AttributeError:
        raise ValueError("Invalid continuation token format.")


def _normalize_headers(headers):
    normalized = {}
    for key, value in headers.items():
        if key.startswith("x-ms-"):
            key = key[5:]
        normalized[key.lower().replace("-", "_")] = get_enum_value(value)
    return normalized


def _return_headers_and_deserialized(
    response, deserialized, response_headers
):  # pylint: disable=unused-argument
    return _normalize_headers(response_headers), deserialized


def _return_context_and_deserialized(
    response, deserialized, response_headers
):  # pylint: disable=unused-argument
    return response.http_response.location_mode, deserialized, response_headers


def _trim_service_metadata(metadata):
    # type: (dict[str,str] -> None)
    return {
        "date": metadata.pop("date", None),
        "etag": metadata.pop("etag", None),
        "version": metadata.pop("version", None),
    }

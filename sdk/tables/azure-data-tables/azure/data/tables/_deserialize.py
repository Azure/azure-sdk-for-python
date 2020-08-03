# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: disable=unused-argument
from typing import (  # pylint: disable=unused-import
    Union, Optional, Any, Iterable, Dict, List, Type, Tuple,
    TYPE_CHECKING
)
import logging
import datetime
from uuid import UUID
# from azure.core.exceptions import ResourceExistsError

from azure.core.exceptions import (
    HttpResponseError,
    ResourceNotFoundError,
    ResourceModifiedError,
    ResourceExistsError,
    ClientAuthenticationError,
    DecodeError)
from azure.core.pipeline.policies import ContentDecodePolicy

from ._shared import url_quote
from ._entity import EntityProperty, EdmType, TableEntity
from ._shared._common_conversion import _decode_base64_to_bytes
from ._generated.models import TableProperties


from ._shared.models import TableErrorCode, UserDelegationKey, get_enum_value


if TYPE_CHECKING:
    from datetime import datetime
    from azure.core.exceptions import AzureError

from ._shared._error import _to_utc_datetime

_LOGGER = logging.getLogger(__name__)


def deserialize_metadata(response, _, headers):
    return {k[10:]: v for k, v in response.headers.items() if k.startswith("x-ms-meta-")}


def deserialize_table_properties(response, obj, headers):
    metadata = deserialize_metadata(response, obj, headers)
    table_properties = TableProperties(
        metadata=metadata,
        **headers
    )
    return table_properties


def deserialize_table_creation(response, _, headers):
    if response.status_code == 204:
        error_code = TableErrorCode.table_already_exists
        error = ResourceExistsError(
            message="Table already exists\nRequestId:{}\nTime:{}\nErrorCode:{}".format(
                headers['x-ms-request-id'],
                headers['Date'],
                error_code
            ),
            response=response)
        error.error_code = error_code
        error.additional_info = {}
        raise error
    return headers


def _from_entity_binary(value):
    return EntityProperty(EdmType.BINARY, _decode_base64_to_bytes(value))


def _from_entity_int32(value):
    return EntityProperty(EdmType.INT32, int(value))


zero = datetime.timedelta(0)  # same as 00:00


class Timezone(datetime.tzinfo):  # pylint: disable : W0223

    def utcoffset(self, dt):
        return zero

    def dst(self, dt):
        return zero

    def tzname(self, dt):
        return


def _from_entity_datetime(value):
    # # TODO: Fix this
    return datetime.datetime.strptime(value, '%Y-%m-%dT%H:%M:%SZ'). \
        replace(tzinfo=Timezone())


def _from_entity_guid(value):
    return UUID(value)


_EDM_TYPES = [EdmType.BINARY, EdmType.INT64, EdmType.GUID, EdmType.DATETIME,
              EdmType.STRING, EdmType.INT32, EdmType.DOUBLE, EdmType.BOOLEAN]

_ENTITY_TO_PYTHON_CONVERSIONS = {
    EdmType.BINARY: _from_entity_binary,
    EdmType.INT32: _from_entity_int32,
    EdmType.INT64: int,
    EdmType.DOUBLE: float,
    EdmType.DATETIME: _from_entity_datetime,
    EdmType.GUID: _from_entity_guid,
}


def _convert_to_entity(entry_element):
    ''' Convert json response to entity.
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
    '''
    entity = TableEntity()

    properties = {}
    edmtypes = {}
    odata = {}

    for name, value in entry_element.items():
        if name.startswith('odata.'):
            odata[name[6:]] = value
        elif name.endswith('@odata.type'):
            edmtypes[name[:-11]] = value
        else:
            properties[name] = value

    # Partition key is a known property
    partition_key = properties.pop('PartitionKey', None)
    if partition_key:
        entity['PartitionKey'] = partition_key

    # Row key is a known property
    row_key = properties.pop('RowKey', None)
    if row_key:
        entity['RowKey'] = row_key

    # Timestamp is a known property
    timestamp = properties.pop('Timestamp', None)
    if timestamp:
        # TODO: verify change here
        # entity['Timestamp'] = _from_entity_datetime(timestamp)
        entity['Timestamp'] = timestamp

    for name, value in properties.items():
        mtype = edmtypes.get(name)

        # Add type for Int32
        if type(value) is int:  # pylint:disable=C0123
            mtype = EdmType.INT32

        # no type info, property should parse automatically
        if not mtype:
            entity[name] = value
        else:  # need an object to hold the property
            conv = _ENTITY_TO_PYTHON_CONVERSIONS.get(mtype)
            if conv is not None:
                new_property = conv(value)
            else:
                new_property = EntityProperty(mtype, value)
            entity[name] = new_property

    # extract etag from entry
    etag = odata.get('etag')
    if timestamp and not etag:
        etag = 'W/"datetime\'' + url_quote(timestamp) + '\'"'
    entity['etag'] = etag

    entity._set_metadata()  # pylint: disable = W0212
    return entity


def _extract_etag(response):
    """ Extracts the etag from the response headers. """
    if response and response.headers:
        return response.headers.get('etag')

    return None


def normalize_headers(headers):
    normalized = {}
    for key, value in headers.items():
        if key.startswith('x-ms-'):
            key = key[5:]
        normalized[key.lower().replace('-', '_')] = get_enum_value(value)
    return normalized


def deserialize_metadata(response, obj, headers):  # pylint: disable=unused-argument
    raw_metadata = {k: v for k, v in response.headers.items() if k.startswith("x-ms-meta-")}
    return {k[10:]: v for k, v in raw_metadata.items()}


def return_headers_and_deserialized(response, deserialized, response_headers):  # pylint: disable=unused-argument
    return normalize_headers(response_headers), deserialized


def return_context_and_deserialized(response, deserialized, response_headers):  # pylint: disable=unused-argument
    return response.http_response.location_mode, deserialized, response_headers


def process_table_error(storage_error):
    raise_error = HttpResponseError
    error_code = storage_error.response.headers.get('x-ms-error-code')
    error_message = storage_error.message
    additional_data = {}
    try:
        error_body = ContentDecodePolicy.deserialize_from_http_generics(storage_error.response)
        if isinstance(error_body, dict):
            for info in error_body['odata.error']:
                if info == 'code':
                    error_code = error_body['odata.error'][info]
                elif info == 'message':
                    error_message = error_body['odata.error'][info]['value']
                else:
                    additional_data[info.tag] = info.text
        else:
            if error_body:
                for info in error_body.iter():
                    if info.tag.lower().find('code') != -1:
                        error_code = info.text
                    elif info.tag.lower().find('message') != -1:
                        error_message = info.text
                    else:
                        additional_data[info.tag] = info.text
    except DecodeError:
        pass

    try:
        if error_code:
            error_code = TableErrorCode(error_code)
            if error_code in [TableErrorCode.condition_not_met]:
                raise_error = ResourceModifiedError
            if error_code in [TableErrorCode.invalid_authentication_info,
                              TableErrorCode.authentication_failed]:
                raise_error = ClientAuthenticationError
            if error_code in [TableErrorCode.resource_not_found,
                              TableErrorCode.table_not_found,
                              TableErrorCode.entity_not_found,
                              ResourceNotFoundError]:
                raise_error = ResourceNotFoundError
            if error_code in [TableErrorCode.resource_already_exists,
                              TableErrorCode.table_already_exists,
                              TableErrorCode.account_already_exists,
                              TableErrorCode.entity_already_exists,
                              ResourceExistsError]:
                raise_error = ResourceExistsError
    except ValueError:
        # Got an unknown error code
        pass

    try:

        error_message += "\nErrorCode:{}".format(error_code.value)
    except AttributeError:
        error_message += "\nErrorCode:{}".format(error_code)
    for name, info in additional_data.items():
        error_message += "\n{}:{}".format(name, info)

    error = raise_error(message=error_message, response=storage_error.response)
    error.error_code = error_code
    error.additional_info = additional_data
    raise error

# -------------------------------------------------------------------------
# Copyright (c) Microsoft.  All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# --------------------------------------------------------------------------
import base64
import sys
import types
import uuid
from plistlib import _decode_base64
from uuid import UUID
from datetime import datetime
from json import (
    dumps,
)
from math import (
    isnan,
)

from azure.table._entity import EdmType, EntityProperty
from azure.table._shared._error import _ERROR_VALUE_TOO_LARGE, _ERROR_TYPE_NOT_SUPPORTED, \
    _ERROR_CANNOT_SERIALIZE_VALUE_TO_ENTITY
from azure.table._models import TablePayloadFormat
from azure.table._shared._common_conversion import _encode_base64, _to_str
from azure.table._shared.parser import _to_utc_datetime
from dateutil.parser import parse
from numpy.core import long
from numpy.core import int64
from pyparsing import unicode

if sys.version_info < (3,):
    def _new_boundary():
        return str(uuid.uuid1())
else:
    def _new_boundary():
        return str(uuid.uuid1()).encode('utf-8')

_DEFAULT_ACCEPT_HEADER = ('Accept', TablePayloadFormat.JSON_MINIMAL_METADATA)
_DEFAULT_CONTENT_TYPE_HEADER = ('Content-Type', 'application/json')
_DEFAULT_PREFER_HEADER = ('Prefer', 'return-no-content')
_SUB_HEADERS = ['If-Match', 'Prefer', 'Accept', 'Content-Type', 'DataServiceVersion']


def _get_entity_path(table_name, partition_key, row_key):
    return '/{0}(PartitionKey=\'{1}\',RowKey=\'{2}\')'.format(
        _to_str(table_name),
        _to_str(partition_key.replace('\'', '\'\'')),
        _to_str(row_key.replace('\'', '\'\'')))


def _update_storage_table_header(request):
    ''' add additional headers for storage table request. '''

    # set service version
    request.headers['DataServiceVersion'] = '3.0;NetFx'
    request.headers['MaxDataServiceVersion'] = '3.0'

def _to_entity_binary(value):
    return EdmType.BINARY, _encode_base64(value)


def _string_to_binary(value):
    return base64.b64decode(value)


def _to_entity_bool(value):
    return None, value


def _string_to_bool(value):
    return bool(value)


def _to_entity_datetime(value):
    return EdmType.DATETIME, _to_utc_datetime(value)


def _string_to_datetime(value):
    return parse(value)


def _to_entity_float(value):
    if isnan(value):
        return EdmType.DOUBLE, 'NaN'
    if value == float('inf'):
        return EdmType.DOUBLE, 'Infinity'
    if value == float('-inf'):
        return EdmType.DOUBLE, '-Infinity'
    return None, value


def _string_to_float(value):
    return float(value)


def _to_entity_guid(value):
    return EdmType.GUID, str(value)


def _string_to_guid(value):
    return value

def _to_entity_int32(value):
    if sys.version_info < (3,):
        value = long(value)
    else:
        value = int(value)
    if value >= 2 ** 31 or value < -(2 ** 31):
        raise TypeError(_ERROR_VALUE_TOO_LARGE.format(str(value), EdmType.INT32))
    return None, value


def _string_to_int32(value):
    return int(value)


def _to_entity_int64(value):
    if sys.version_info < (3,):
        ivalue = long(value)
    else:
        ivalue = int(value)
    if ivalue >= 2 ** 63 or ivalue < -(2 ** 63):
        raise TypeError(_ERROR_VALUE_TOO_LARGE.format(str(value), EdmType.INT64))
    return EdmType.INT64, str(value)


def _string_to_int64(value):
    return int64(value)


def _to_entity_str(value):
    return None, value


def _to_entity_none(value):
    return None, None


# Conversion from Python type to a function which returns a tuple of the
# type string and content string.
_PYTHON_TO_ENTITY_CONVERSIONS = {
    int: _to_entity_int64,
    bool: _to_entity_bool,
    datetime: _to_entity_datetime,
    float: _to_entity_float,
    str: _to_entity_str,
    bytes: _to_entity_binary,
    UUID: _to_entity_guid
}

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

_EDM_TO_TYPE_CONVERSIONS = {
    EdmType.BINARY: _string_to_binary,
    EdmType.BOOLEAN: _string_to_bool,
    EdmType.DATETIME: _string_to_datetime,
    EdmType.DOUBLE: _string_to_float,
    EdmType.GUID: _string_to_guid,
    EdmType.INT32: _string_to_int32,
    EdmType.INT64: _string_to_int64,
    EdmType.STRING: _to_entity_str,
}

if sys.version_info < (3,):
    _PYTHON_TO_ENTITY_CONVERSIONS.update({
        long: _to_entity_int64,
        types.NoneType: _to_entity_none,
        unicode: _to_entity_str,
    })


def _add_entity_properties(source):
    ''' Adds entity properties to entity to send.
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

    properties = {}

    # set properties type for types we know if value has no type info.
    # if value has type info, then set the type to value.type
    for name, value in source.items():
        mtype = ''

        if isinstance(value, EntityProperty):
            conv = _EDM_TO_ENTITY_CONVERSIONS.get(value.type)
            if conv is None:
                raise TypeError(
                    _ERROR_TYPE_NOT_SUPPORTED.format(value.type))
            mtype, value = conv(value.value)
        else:
            conv = _PYTHON_TO_ENTITY_CONVERSIONS.get(type(value))
            if conv is None and sys.version_info >= (3,) and value is None:
                conv = _to_entity_none
            if conv is None:
                raise TypeError(
                    _ERROR_CANNOT_SERIALIZE_VALUE_TO_ENTITY.format(
                        type(value).__name__))
            mtype, value = conv(value)

        # form the property node
        properties[name] = value
        if mtype:
            properties[name + '@odata.type'] = mtype

    # generate the entity_body
    return properties


def _convert_entity_to_properties(source):
    properties = {}

    # set properties type for types we know if value has no type info.
    # if value has type info, then set the type to value.type
    for name, value in source.items():
        mtype = ''
        ntype = name + '@odata.type'
        if ntype in source:
            conv = _EDM_TO_TYPE_CONVERSIONS.get(source[ntype])
            new_value = conv(value)
            properties[name] = new_value
        else:  # form the property node
            properties[name] = value

    return properties


def _convert_table_to_json(table_name):
    '''
    Create json to send for a given table name. Since json format for table is
    the same as entity and the only difference is that table has only one
    property 'TableName', so we just call _convert_entity_to_json.

    table_name:
        the name of the table
    '''
    return _add_entity_properties({'TableName': table_name})


def _convert_batch_to_json(batch_requests):
    '''
    Create json to send for an array of batch requests.

    batch_requests:
        an array of requests
    '''
    batch_boundary = b'batch_' + _new_boundary()
    changeset_boundary = b'changeset_' + _new_boundary()

    body = [b'--' + batch_boundary + b'\n',
            b'Content-Type: multipart/mixed; boundary=',
            changeset_boundary + b'\n\n']

    content_id = 1

    # Adds each request body to the POST data.
    for _, request in batch_requests:
        body.append(b'--' + changeset_boundary + b'\n')
        body.append(b'Content-Type: application/http\n')
        body.append(b'Content-Transfer-Encoding: binary\n\n')
        body.append(request.method.encode('utf-8'))
        body.append(b' ')
        body.append(request.path.encode('utf-8'))
        body.append(b' HTTP/1.1\n')
        body.append(b'Content-ID: ')
        body.append(str(content_id).encode('utf-8') + b'\n')
        content_id += 1

        for name, value in request.headers.items():
            if name in _SUB_HEADERS:
                body.append(name.encode('utf-8') + b': ')
                body.append(value.encode('utf-8') + b'\n')

        # Add different headers for different request types.
        if not request.method == 'DELETE':
            body.append(b'Content-Length: ')
            body.append(str(len(request.body)).encode('utf-8'))
            body.append(b'\n\n')
            body.append(request.body + b'\n')

        body.append(b'\n')

    body.append(b'--' + changeset_boundary + b'--' + b'\n')
    body.append(b'--' + batch_boundary + b'--')

    return b''.join(body), 'multipart/mixed; boundary=' + batch_boundary.decode('utf-8')

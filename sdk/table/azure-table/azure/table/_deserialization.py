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
from uuid import UUID
from dateutil import parser
from azure.table._shared import url_quote
from azure.table._entity import EntityProperty, EdmType, Entity
from azure.table._shared._common_conversion import _decode_base64_to_bytes


def _get_continuation_from_response_headers(response):
    marker = {}
    for name, value in response.headers.items():
        if name.startswith('x-ms-continuation'):
            marker[name[len('x-ms-continuation') + 1:]] = value
    return marker


# Tables of conversions to and from entity types.  We support specific
# datatypes, and beyond that the user can use an EntityProperty to get
# custom data type support.

def _from_entity_binary(value):
    return EntityProperty(EdmType.BINARY, _decode_base64_to_bytes(value))


def _from_entity_int32(value):
    return EntityProperty(EdmType.INT32, int(value))


def _from_entity_datetime(value):
    return parser.parse(value)


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
    entity = Entity()

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
        entity['Timestamp'] = _from_entity_datetime(timestamp)

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
    if timestamp:
        etag = 'W/"datetime\'' + url_quote(timestamp) + '\'"'
    entity['etag'] = etag

    return entity


def _extract_etag(response):
    ''' Extracts the etag from the response headers. '''
    if response and response.headers:
        return response.headers.get('etag')

    return None

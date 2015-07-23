#-------------------------------------------------------------------------
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
#--------------------------------------------------------------------------
import sys
import types

from datetime import datetime
from dateutil import parser
from dateutil.tz import tzutc
from time import time
from wsgiref.handlers import format_date_time
from .._common_models import (
    WindowsAzureData,
)
from .._common_serialization import (
    _create_entry,
    _etree_entity_feed_namespaces,
    _make_etree_ns_attr_name,
    _get_etree_tag_name_without_ns,
    xml_escape,
    ETree,
    _ETreeXmlToObject,
)
from .._common_conversion import (
    _decode_base64_to_bytes,
    _encode_base64,
)
from .._common_error import (
    _ERROR_CANNOT_SERIALIZE_VALUE_TO_ENTITY,
)
from .._serialization import _update_storage_header
from .models import (
    Entity,
    EntityProperty,
    Table,
    TableSharedAccessPermissions,
)


def _update_storage_table_header(request, content_type='application/atom+xml'):
    ''' add additional headers for storage table request. '''

    request = _update_storage_header(request)
    if content_type:
        for name, _ in request.headers:
            if name.lower() == 'content-type':
                break
        else:
            request.headers.append(('Content-Type', content_type))
    request.headers.append(('DataServiceVersion', '2.0;NetFx'))
    request.headers.append(('MaxDataServiceVersion', '2.0;NetFx'))
    current_time = format_date_time(time())
    request.headers.append(('x-ms-date', current_time))
    request.headers.append(('Date', current_time))
    return request.headers


def _to_python_bool(value):
    if value.lower() == 'true':
        return True
    return False


def _to_entity_int(data):
    int_max = (2 << 30) - 1
    if data > (int_max) or data < (int_max + 1) * (-1):
        return 'Edm.Int64', str(data)
    else:
        return 'Edm.Int32', str(data)


def _to_entity_bool(value):
    if value:
        return 'Edm.Boolean', 'true'
    return 'Edm.Boolean', 'false'


def _to_entity_datetime(value):
    # Azure expects the date value passed in to be UTC.
    # Azure will always return values as UTC.
    # If a date is passed in without timezone info, it is assumed to be UTC.
    if value.tzinfo:
        value = value.astimezone(tzutc())
    return 'Edm.DateTime', value.strftime('%Y-%m-%dT%H:%M:%SZ')


def _to_entity_float(value):
    return 'Edm.Double', str(value)


def _to_entity_property(value):
    if value.type == 'Edm.Binary':
        return value.type, _encode_base64(value.value)

    return value.type, str(value.value)


def _to_entity_none(value):
    return None, None


def _to_entity_str(value):
    return 'Edm.String', value


# Tables of conversions to and from entity types.  We support specific
# datatypes, and beyond that the user can use an EntityProperty to get
# custom data type support.

def _from_entity_binary(value):
    return EntityProperty('Edm.Binary', _decode_base64_to_bytes(value))


def _from_entity_int(value):
    return int(value)


def _from_entity_datetime(value):
    # Note that Azure always returns UTC datetime, and dateutil parser
    # will set the tzinfo on the date it returns
    return parser.parse(value)

_ENTITY_TO_PYTHON_CONVERSIONS = {
    'Edm.Binary': _from_entity_binary,
    'Edm.Int32': _from_entity_int,
    'Edm.Int64': _from_entity_int,
    'Edm.Double': float,
    'Edm.Boolean': _to_python_bool,
    'Edm.DateTime': _from_entity_datetime,
}

# Conversion from Python type to a function which returns a tuple of the
# type string and content string.
_PYTHON_TO_ENTITY_CONVERSIONS = {
    int: _to_entity_int,
    bool: _to_entity_bool,
    datetime: _to_entity_datetime,
    float: _to_entity_float,
    EntityProperty: _to_entity_property,
    str: _to_entity_str,
}

if sys.version_info < (3,):
    _PYTHON_TO_ENTITY_CONVERSIONS.update({
        long: _to_entity_int,
        types.NoneType: _to_entity_none,
        unicode: _to_entity_str,
    })


def _convert_entity_to_xml(source):
    ''' Converts an entity object to xml to send.

    The entity format is:
    <entry xmlns:d="http://schemas.microsoft.com/ado/2007/08/dataservices" xmlns:m="http://schemas.microsoft.com/ado/2007/08/dataservices/metadata" xmlns="http://www.w3.org/2005/Atom">
      <title />
      <updated>2008-09-18T23:46:19.3857256Z</updated>
      <author>
        <name />
      </author>
      <id />
      <content type="application/xml">
        <m:properties>
          <d:Address>Mountain View</d:Address>
          <d:Age m:type="Edm.Int32">23</d:Age>
          <d:AmountDue m:type="Edm.Double">200.23</d:AmountDue>
          <d:BinaryData m:type="Edm.Binary" m:null="true" />
          <d:CustomerCode m:type="Edm.Guid">c9da6455-213d-42c9-9a79-3e9149a57833</d:CustomerCode>
          <d:CustomerSince m:type="Edm.DateTime">2008-07-10T00:00:00</d:CustomerSince>
          <d:IsActive m:type="Edm.Boolean">true</d:IsActive>
          <d:NumOfOrders m:type="Edm.Int64">255</d:NumOfOrders>
          <d:PartitionKey>mypartitionkey</d:PartitionKey>
          <d:RowKey>myrowkey1</d:RowKey>
          <d:Timestamp m:type="Edm.DateTime">0001-01-01T00:00:00</d:Timestamp>
        </m:properties>
      </content>
    </entry>
    '''

    # construct the entity body included in <m:properties> and </m:properties>
    entity_body = '<m:properties xml:space="preserve">{properties}</m:properties>'

    if isinstance(source, WindowsAzureData):
        source = vars(source)

    properties_str = ''

    # set properties type for types we know if value has no type info.
    # if value has type info, then set the type to value.type
    for name, value in source.items():
        mtype = ''
        conv = _PYTHON_TO_ENTITY_CONVERSIONS.get(type(value))
        if conv is None and sys.version_info >= (3,) and value is None:
            conv = _to_entity_none
        if conv is None:
            raise TypeError(
                _ERROR_CANNOT_SERIALIZE_VALUE_TO_ENTITY.format(
                    type(value).__name__))

        mtype, value = conv(value)

        # form the property node
        properties_str += ''.join(['<d:', name])
        if value is None:
            properties_str += ' m:null="true" />'
        else:
            if mtype:
                properties_str += ''.join([' m:type="', mtype, '"'])
            properties_str += ''.join(['>',
                                      xml_escape(value), '</d:', name, '>'])

    if sys.version_info < (3,):
        if isinstance(properties_str, unicode):
            properties_str = properties_str.encode('utf-8')

    # generate the entity_body
    entity_body = entity_body.format(properties=properties_str)
    xmlstr = _create_entry(entity_body)
    return xmlstr


def _convert_table_to_xml(table_name):
    '''
    Create xml to send for a given table name. Since xml format for table is
    the same as entity and the only difference is that table has only one
    property 'TableName', so we just call _convert_entity_to_xml.

    table_name:
        the name of the table
    '''
    return _convert_entity_to_xml({'TableName': table_name})


def _convert_response_to_entity(response):
    if response is None:
        return response

    root = ETree.fromstring(response.body)

    return _convert_etree_element_to_entity(root)


def _convert_etree_element_to_entity(entry_element):
    ''' Convert xml response to entity.

    The format of entity:
    <entry xmlns:d="http://schemas.microsoft.com/ado/2007/08/dataservices" xmlns:m="http://schemas.microsoft.com/ado/2007/08/dataservices/metadata" xmlns="http://www.w3.org/2005/Atom">
      <title />
      <updated>2008-09-18T23:46:19.3857256Z</updated>
      <author>
        <name />
      </author>
      <id />
      <content type="application/xml">
        <m:properties>
          <d:Address>Mountain View</d:Address>
          <d:Age m:type="Edm.Int32">23</d:Age>
          <d:AmountDue m:type="Edm.Double">200.23</d:AmountDue>
          <d:BinaryData m:type="Edm.Binary" m:null="true" />
          <d:CustomerCode m:type="Edm.Guid">c9da6455-213d-42c9-9a79-3e9149a57833</d:CustomerCode>
          <d:CustomerSince m:type="Edm.DateTime">2008-07-10T00:00:00</d:CustomerSince>
          <d:IsActive m:type="Edm.Boolean">true</d:IsActive>
          <d:NumOfOrders m:type="Edm.Int64">255</d:NumOfOrders>
          <d:PartitionKey>mypartitionkey</d:PartitionKey>
          <d:RowKey>myrowkey1</d:RowKey>
          <d:Timestamp m:type="Edm.DateTime">0001-01-01T00:00:00</d:Timestamp>
        </m:properties>
      </content>
    </entry>
    '''
    entity = Entity()

    properties = entry_element.findall('./atom:content/m:properties', _etree_entity_feed_namespaces)
    for prop in properties:
        for p in prop:
            name = _get_etree_tag_name_without_ns(p.tag)
            value = p.text or ''
            mtype = p.attrib.get(_make_etree_ns_attr_name(_etree_entity_feed_namespaces['m'], 'type'), None)
            isnull = p.attrib.get(_make_etree_ns_attr_name(_etree_entity_feed_namespaces['m'], 'null'), None)

            # if not isnull and no type info, then it is a string and we just
            # need the str type to hold the property.
            if not isnull and not mtype:
                _set_entity_attr(entity, name, value)
            elif isnull == 'true':
                if mtype:
                    property = EntityProperty(mtype, None)
                else:
                    property = EntityProperty('Edm.String', None)
            else:  # need an object to hold the property
                conv = _ENTITY_TO_PYTHON_CONVERSIONS.get(mtype)
                if conv is not None:
                    property = conv(value)
                else:
                    property = EntityProperty(mtype, value)
                _set_entity_attr(entity, name, property)


    # extract id, updated and name value from feed entry and set them of
    # rule.
    for name, value in _ETreeXmlToObject.get_entry_properties_from_element(
        entry_element, True).items():
        if name in ['etag']:
            _set_entity_attr(entity, name, value)

    return entity


def _set_entity_attr(entity, name, value):
    try:
        setattr(entity, name, value)
    except UnicodeEncodeError:
        # Python 2 doesn't support unicode attribute names, so we'll
        # add them and access them directly through the dictionary
        entity.__dict__[name] = value


def _convert_etree_element_to_table(entry_element):
    ''' Converts the xml element to table class.
    '''
    table = Table()
    name_element = entry_element.find('./atom:content/m:properties/d:TableName', _etree_entity_feed_namespaces)
    if name_element is not None:
        table.name = name_element.text

    for name_element, value in _ETreeXmlToObject.get_entry_properties_from_element(
        entry_element, False).items():
        setattr(table, name_element, value)

    return table

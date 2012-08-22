#-------------------------------------------------------------------------
# Copyright 2011 Microsoft Corporation
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
import datetime
import base64
import hashlib
import hmac
import urllib2
from xml.dom import minidom
import types
from datetime import datetime

from azure import (_create_entry, METADATA_NS, _parse_response_for_dict, 
                          _get_entry_properties, WindowsAzureError,
                          _get_child_nodes, _get_child_nodesNS, 
                          WindowsAzureConflictError, 
                          WindowsAzureMissingResourceError, _list_of, 
                          DEV_TABLE_HOST, TABLE_SERVICE_HOST_BASE, DEV_BLOB_HOST, 
                          BLOB_SERVICE_HOST_BASE, DEV_QUEUE_HOST, 
                          QUEUE_SERVICE_HOST_BASE, WindowsAzureData, 
                          _get_children_from_path, xml_escape,
                          _ERROR_CANNOT_SERIALIZE_VALUE_TO_ENTITY)
import azure
                         

#x-ms-version for storage service.
X_MS_VERSION = '2011-08-18'

class EnumResultsBase:
    ''' base class for EnumResults. '''
    def __init__(self):
        self.prefix = ''
        self.marker = ''
        self.max_results = 0
        self.next_marker = ''

class ContainerEnumResults(EnumResultsBase):
    ''' Blob Container list. '''

    def __init__(self):
        EnumResultsBase.__init__(self)
        self.containers = _list_of(Container)

    def __iter__(self):
        return iter(self.containers)

    def __len__(self):
        return len(self.containers)

    def __getitem__(self, index):
        return self.containers[index]

class Container(WindowsAzureData):
    ''' Blob container class. '''

    def __init__(self):
        self.name = ''
        self.url = ''
        self.properties = Properties()
        self.metadata = {}

class Properties(WindowsAzureData):
    ''' Blob container's properties class. '''

    def __init__(self):
        self.last_modified = ''
        self.etag = ''

class RetentionPolicy(WindowsAzureData):
    ''' RetentionPolicy in service properties. '''

    def __init__(self):
        self.enabled = False
        self.__dict__['days'] = None

    def get_days(self):        
        #convert days to int value
        return int(self.__dict__['days'])

    def set_days(self, value):
        ''' set default days if days is set to empty. '''
        self.__dict__['days'] = value

    days = property(fget=get_days, fset=set_days)

class Logging(WindowsAzureData):
    ''' Logging class in service properties. '''

    def __init__(self):
        self.version = '1.0'
        self.delete = False
        self.read = False
        self.write = False
        self.retention_policy = RetentionPolicy()

class Metrics(WindowsAzureData):
    ''' Metrics class in service properties. '''

    def __init__(self):
        self.version = '1.0'
        self.enabled = False
        self.include_apis = None
        self.retention_policy = RetentionPolicy()

class StorageServiceProperties(WindowsAzureData):
    ''' Storage Service Propeties class. '''

    def __init__(self):
        self.logging = Logging()
        self.metrics = Metrics()

class AccessPolicy(WindowsAzureData):
    ''' Access Policy class in service properties. '''

    def __init__(self):
        self.start = ''
        self.expiry = ''
        self.permission = ''

class SignedIdentifier(WindowsAzureData):
    ''' Signed Identifier class for service properties. '''

    def __init__(self):
        self.id = ''
        self.access_policy = AccessPolicy()

class SignedIdentifiers(WindowsAzureData):
    ''' SignedIdentifier list. '''
    
    def __init__(self):
        self.signed_identifiers = _list_of(SignedIdentifier) 

    def __iter__(self):
        return iter(self.signed_identifiers)

    def __len__(self):
        return len(self.signed_identifiers)

    def __getitem__(self, index):
        return self.signed_identifiers[index]

class BlobEnumResults(EnumResultsBase):
    ''' Blob list.'''

    def __init__(self):
        EnumResultsBase.__init__(self)
        self.blobs = _list_of(Blob)

    def __iter__(self):
        return iter(self.blobs)

    def __len__(self):
        return len(self.blobs)

    def __getitem__(self, index):
        return self.blobs[index]

class BlobResult(str):

    def __new__(cls, blob, properties):
        return str.__new__(cls, blob)

    def __init__(self, blob, properties):
        self.properties = properties

class Blob(WindowsAzureData):
    ''' Blob class. '''

    def __init__(self):
        self.name = ''
        self.snapshot = ''
        self.url = ''
        self.properties = BlobProperties()
        self.metadata = {}
        self.blob_prefix = BlobPrefix()

class BlobProperties(WindowsAzureData):
    ''' Blob Properties '''

    def __init__(self):
        self.last_modified = ''
        self.etag = ''
        self.content_length = 0
        self.content_type = ''
        self.content_encoding = ''
        self.content_language = ''
        self.content_md5 = ''
        self.xms_blob_sequence_number = 0
        self.blob_type = ''
        self.lease_status = ''

class BlobPrefix(WindowsAzureData):
    ''' BlobPrefix in Blob. '''

    def __init__(self):
        self.name = ''

class BlobBlock(WindowsAzureData):
    ''' BlobBlock class '''

    def __init__(self, id=None, size=None):
        self.id = id
        self.size = size

class BlobBlockList(WindowsAzureData):
    ''' BlobBlockList class '''

    def __init__(self):
        self.committed_blocks = []
        self.uncommitted_blocks = []

class PageRange(WindowsAzureData):
    ''' Page Range for page blob. '''

    def __init__(self):
        self.start = 0
        self.end = 0

class PageList:
    ''' Page list for page blob. '''

    def __init__(self):
        self.page_ranges = _list_of(PageRange)

    def __iter__(self):
        return iter(self.page_ranges)

    def __len__(self):
        return len(self.page_ranges)

    def __getitem__(self, index):
        return self.page_ranges[index]

class QueueEnumResults(EnumResultsBase):
    ''' Queue list'''

    def __init__(self):
        EnumResultsBase.__init__(self)
        self.queues = _list_of(Queue)

    def __iter__(self):
        return iter(self.queues)

    def __len__(self):
        return len(self.queues)

    def __getitem__(self, index):
        return self.queues[index]

class Queue(WindowsAzureData):
    ''' Queue class '''

    def __init__(self):
        self.name = ''
        self.url = ''
        self.metadata = {}

class QueueMessagesList(WindowsAzureData):
    ''' Queue message list. '''

    def __init__(self):
        self.queue_messages = _list_of(QueueMessage)

    def __iter__(self):
        return iter(self.queue_messages)

    def __len__(self):
        return len(self.queue_messages)

    def __getitem__(self, index):
        return self.queue_messages[index]

class QueueMessage(WindowsAzureData):
    ''' Queue message class. '''

    def __init__(self):
        self.message_id = ''
        self.insertion_time = ''
        self.expiration_time = ''
        self.pop_receipt = ''
        self.time_next_visible = ''
        self.dequeue_count = ''
        self.message_text = ''

class Entity(WindowsAzureData):
    ''' Entity class. The attributes of entity will be created dynamically. '''
    pass

class EntityProperty(WindowsAzureData):
    ''' Entity property. contains type and value.  '''

    def __init__(self, type=None, value=None):
        self.type = type
        self.value = value

class Table(WindowsAzureData):
    ''' Only for intellicens and telling user the return type. '''
    pass

def _update_storage_header(request):
    ''' add addtional headers for storage request. '''

    #if it is PUT, POST, MERGE, DELETE, need to add content-lengt to header.
    if request.method in ['PUT', 'POST', 'MERGE', 'DELETE']:
            request.headers.append(('Content-Length', str(len(request.body))))  

    #append addtional headers base on the service
    request.headers.append(('x-ms-version', X_MS_VERSION))

    #append x-ms-meta name, values to header
    for name, value in request.headers:
        if 'x-ms-meta-name-values' in name and value:
            for meta_name, meta_value in value.iteritems():
                request.headers.append(('x-ms-meta-' + meta_name, meta_value))
            request.headers.remove((name, value))
            break
    return request

def _update_storage_blob_header(request, account_name, account_key):
    ''' add additional headers for storage blob request. '''

    request = _update_storage_header(request)
    current_time = datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
    request.headers.append(('x-ms-date', current_time))
    request.headers.append(('Content-Type', 'application/octet-stream Charset=UTF-8'))  
    request.headers.append(('Authorization', _sign_storage_blob_request(request, account_name, account_key)))

    return request.headers

def _update_storage_queue_header(request, account_name, account_key):
    ''' add additional headers for storage queue request. '''
    return _update_storage_blob_header(request, account_name, account_key)

def _update_storage_table_header(request):
    ''' add additional headers for storage table request. '''

    request = _update_storage_header(request)
    for name, value in request.headers:
        if name.lower() == 'content-type':
            break;
    else:
        request.headers.append(('Content-Type', 'application/atom+xml'))  
    request.headers.append(('DataServiceVersion', '2.0;NetFx'))
    request.headers.append(('MaxDataServiceVersion', '2.0;NetFx'))
    current_time = datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
    request.headers.append(('x-ms-date', current_time))
    request.headers.append(('Date', current_time))
    return request.headers

def _sign_storage_blob_request(request, account_name, account_key):
    ''' 
    Returns the signed string for blob request which is used to set Authorization header. 
    This is also used to sign queue request.
    '''

    uri_path = request.path.split('?')[0]

    #method to sign
    string_to_sign = request.method + '\n'

    #get headers to sign
    headers_to_sign = ['content-encoding', 'content-language', 'content-length', 
                        'content-md5', 'content-type', 'date', 'if-modified-since', 
                        'if-match', 'if-none-match', 'if-unmodified-since', 'range']
    for header in headers_to_sign:
        for name, value in request.headers:
            if value and name.lower() == header:
                string_to_sign += value + '\n'
                break
        else:
            string_to_sign += '\n'

    #get x-ms header to sign
    x_ms_headers = []
    for name, value in request.headers:
        if 'x-ms' in name:
            x_ms_headers.append((name.lower(), value))                
    x_ms_headers.sort()
    for name, value in x_ms_headers:
            if value:
                string_to_sign += ''.join([name, ':', value, '\n'])

    #get account_name and uri path to sign  
    string_to_sign += '/' + account_name + uri_path

    #get query string to sign if it is not table service
    query_to_sign = request.query
    query_to_sign.sort()

    current_name = ''
    for name, value in query_to_sign:
        if value:
            if current_name != name:
                string_to_sign += '\n' + name + ':' + value
            else:
                string_to_sign += '\n' + ',' + value

    #sign the request
    decode_account_key = base64.b64decode(account_key)
    signed_hmac_sha256 = hmac.HMAC(decode_account_key, string_to_sign, hashlib.sha256)
    auth_string = 'SharedKey ' + account_name + ':' + base64.b64encode(signed_hmac_sha256.digest())
    return auth_string

def _sign_storage_table_request(request, account_name, account_key):
    uri_path = request.path.split('?')[0]

    string_to_sign = request.method + '\n'
    headers_to_sign = ['content-md5', 'content-type', 'date']
    for header in headers_to_sign:
        for name, value in request.headers:
            if value and name.lower() == header:
                string_to_sign += value + '\n'
                break
        else:
            string_to_sign += '\n'

    #get account_name and uri path to sign     
    string_to_sign += ''.join(['/', account_name, uri_path])

    for name, value in request.query:
        if name == 'comp' and uri_path == '/':
            string_to_sign += '?comp=' + value
            break

    #sign the request
    decode_account_key = base64.b64decode(account_key)
    signed_hmac_sha256 = hmac.HMAC(decode_account_key, string_to_sign, hashlib.sha256)
    auth_string = 'SharedKey ' + account_name + ':' + base64.b64encode(signed_hmac_sha256.digest())
    return auth_string

def _to_python_bool(value):
    if value.lower() == 'true':
        return True
    return False
    
def _to_entity_int(data):
    int_max = (2 << 30) - 1
    import sys
    if data > (int_max) or data < (int_max + 1)*(-1):
        return 'Edm.Int64', str(data)
    else:
        return 'Edm.Int32', str(data)

def _to_entity_bool(value):
    if value:
        return 'Edm.Boolean', 'true'
    return 'Edm.Boolean', 'false'

def _to_entity_datetime(value):
    return 'Edm.DateTime', value.strftime('%Y-%m-%dT%H:%M:%S')

def _to_entity_float(value):
    return 'Edm.Double', str(value)

def _to_entity_property(value):
    return value.type, str(value.value)

def _to_entity_none(value):
    return '', ''

def _to_entity_str(value):
    return 'Edm.String', value


# Tables of conversions to and from entity types.  We support specific 
# datatypes, and beyond that the user can use an EntityProperty to get
# custom data type support.

def _from_entity_int(value):
    return int(value)

def _from_entity_datetime(value):
    if value.endswith('Z'):
        return datetime.strptime(value, '%Y-%m-%dT%H:%M:%SZ')   
    else:
        return datetime.strptime(value, '%Y-%m-%dT%H:%M:%S')   

_ENTITY_TO_PYTHON_CONVERSIONS = {
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
    long: _to_entity_int,
    bool: _to_entity_bool,
    datetime: _to_entity_datetime,
    float: _to_entity_float,
    EntityProperty: _to_entity_property,
    types.NoneType: _to_entity_none,
    str: _to_entity_str,
    unicode: _to_entity_str,
}

def convert_entity_to_xml(source):
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

    #construct the entity body included in <m:properties> and </m:properties>
    entity_body = '<m:properties>{properties}</m:properties>'

    if isinstance(source, WindowsAzureData):
        source = vars(source)

    properties_str = ''
    
    #set properties type for types we know if value has no type info.
    #if value has type info, then set the type to value.type
    for name, value in source.iteritems():
        mtype = ''
        conv = _PYTHON_TO_ENTITY_CONVERSIONS.get(type(value))
        if conv is None:
            raise WindowsAzureError(_ERROR_CANNOT_SERIALIZE_VALUE_TO_ENTITY % type(value).__name__)

        mtype, value = conv(value)
        
        #form the property node
        properties_str += ''.join(['<d:', name])
        if value == '':
            properties_str += ' m:null="true" />'
        else:
            if mtype:
                properties_str += ''.join([' m:type="', mtype, '"'])
            properties_str += ''.join(['>', xml_escape(value), '</d:', name, '>'])

    #generate the entity_body
    entity_body = entity_body.format(properties=properties_str)
    xmlstr = _create_entry(entity_body)
    return xmlstr

def convert_table_to_xml(table_name):
    ''' 
    Create xml to send for a given table name. Since xml format for table is 
    the same as entity and the only difference is that table has only one 
    property 'TableName', so we just call convert_entity_to_xml.

    table_name: the name of the table
    '''
    return convert_entity_to_xml({'TableName': table_name})

def convert_block_list_to_xml(block_id_list):
    '''
    Convert a block list to xml to send.

    block_id_list: a str list containing the block ids that are used in put_block_list. 
    Only get block from latest blocks. 
    '''
    if block_id_list is None:
        return ''
    xml = '<?xml version="1.0" encoding="utf-8"?><BlockList>'
    for value in block_id_list:
        xml += '<Latest>%s</Latest>' % base64.b64encode(value)
 
    return xml+'</BlockList>'

def _create_blob_result(response):
    blob_properties = _parse_response_for_dict(response)
    return BlobResult(response.body, blob_properties)

def convert_response_to_block_list(response):
    '''
    Converts xml response to block list class.
    '''
    blob_block_list = BlobBlockList()
    
    xmldoc = minidom.parseString(response.body)
    for xml_block in _get_children_from_path(xmldoc, 'BlockList', 'CommittedBlocks', 'Block'):
        xml_block_id = base64.b64decode(_get_child_nodes(xml_block, 'Name')[0].firstChild.nodeValue)
        xml_block_size = int(_get_child_nodes(xml_block, 'Size')[0].firstChild.nodeValue)
        blob_block_list.committed_blocks.append(BlobBlock(xml_block_id, xml_block_size))  

    for xml_block in _get_children_from_path(xmldoc, 'BlockList', 'UncommittedBlocks', 'Block'):
        xml_block_id = base64.b64decode(_get_child_nodes(xml_block, 'Name')[0].firstChild.nodeValue)
        xml_block_size = int(_get_child_nodes(xml_block, 'Size')[0].firstChild.nodeValue)
        blob_block_list.uncommitted_blocks.append(BlobBlock(xml_block_id, xml_block_size))

    return blob_block_list

def _remove_prefix(name):
    colon = name.find(':')
    if colon != -1:
        return name[colon + 1:]
    return name

def _convert_response_to_entity(response):
    if response is None:
        return response
    return _convert_xml_to_entity(response.body)
        
def _convert_xml_to_entity(xmlstr):
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
    xmldoc = minidom.parseString(xmlstr)
    
    xml_properties = None
    for entry in _get_child_nodes(xmldoc, 'entry'):
        for content in _get_child_nodes(entry, 'content'):
            xml_properties = _get_child_nodesNS(content, METADATA_NS, 'properties') # TODO: Namespace
                
    if not xml_properties:
        return None

    entity = Entity()
    #extract each property node and get the type from attribute and node value
    for xml_property in xml_properties[0].childNodes:
        if xml_property.firstChild:
            name = _remove_prefix(xml_property.nodeName)
            #exclude the Timestamp since it is auto added by azure when inserting 
            #entity. We don't want this to mix with real properties
            if name in ['Timestamp']:
                continue
            value = xml_property.firstChild.nodeValue
            
            isnull = xml_property.getAttributeNS(METADATA_NS, 'null')
            mtype = xml_property.getAttributeNS(METADATA_NS, 'type')


            #if not isnull and no type info, then it is a string and we just need the str type to hold the property.
            if not isnull and not mtype:
                setattr(entity, name, value)
            elif isnull == 'true':
                if mtype:
                    property = EntityProperty(mtype, None)
                else:
                    property = EntityProperty('Edm.String', None)
            else: #need an object to hold the property
                conv = _ENTITY_TO_PYTHON_CONVERSIONS.get(mtype)
                if conv is not None:
                    property = conv(value)
                else:
                    property = EntityProperty(mtype, value)
                setattr(entity, name, property)

        #extract id, updated and name value from feed entry and set them of rule.
    for name, value in _get_entry_properties(xmlstr, True).iteritems():
        if name in ['etag']:
            setattr(entity, name, value)

    return entity

def _convert_xml_to_table(xmlstr):
    ''' Converts the xml response to table class
    Simply call convert_xml_to_entity and extract the table name, and add updated and author info
    '''
    table = Table()
    entity = _convert_xml_to_entity(xmlstr)
    setattr(table, 'name', entity.TableName)
    for name, value in _get_entry_properties(xmlstr, False).iteritems():
       setattr(table, name, value)
    return table

def _storage_error_handler(http_error):
    ''' Simple error handler for storage service. Will add more specific cases '''
    if http_error.status == 409:
        raise WindowsAzureConflictError(azure._ERROR_CONFLICT)
    elif http_error.status == 404:
        raise WindowsAzureMissingResourceError(azure._ERROR_NOT_FOUND)
    else:
        raise WindowsAzureError(azure._ERROR_UNKNOWN % http_error.message)

# make these available just from storage.
from blobservice import BlobService
from queueservice import QueueService
from tableservice import TableService
from cloudstorageaccount import CloudStorageAccount
from sharedaccesssignature import SharedAccessSignature, SharedAccessPolicy, Permission, WebResource
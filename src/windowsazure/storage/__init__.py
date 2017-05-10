#------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. 
#
# This source code is subject to terms and conditions of the Apache License, 
# Version 2.0. A copy of the license can be found in the License.html file at 
# the root of this distribution. If you cannot locate the Apache License, 
# Version 2.0, please send an email to vspython@microsoft.com. By using this 
# source code in any fashion, you are agreeing to be bound by the terms of the 
# Apache License, Version 2.0.
#
# You must not remove this notice, or any other, from this software.
#------------------------------------------------------------------------------
import datetime
import base64
import hashlib
import hmac
import urllib2
from xml.dom import minidom
import types
from datetime import datetime

from windowsazure import (remove_xmltag_namespace, create_entry, normalize_xml, 
                          get_entry_properties, html_encode, WindowsAzureError)
                         

X_MS_VERSION = '2011-08-18'

#------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. 
#
# This source code is subject to terms and conditions of the Apache License, 
# Version 2.0. A copy of the license can be found in the License.html file at 
# the root of this distribution. If you cannot locate the Apache License, 
# Version 2.0, please send an email to vspython@microsoft.com. By using this 
# source code in any fashion, you are agreeing to be bound by the terms of the 
# Apache License, Version 2.0.
#
# You must not remove this notice, or any other, from this software.
#------------------------------------------------------------------------------

from windowsazure import WindowsAzureData, DEV_ACCOUNT_NAME

class EnumResultsBase:
    def __init__(self):
        self.prefix = ''
        self.marker = ''
        self.max_results = 0
        self.next_marker = ''

class ContainerEnumResults(EnumResultsBase):
    def __init__(self):
        EnumResultsBase.__init__(self)
        self.containers = []   
    def __iter__(self):
        return iter(self.containers)
    def __len__(self):
        return len(self.containers)
    def __getitem__(self, index):
        return self.containers[index]

class Container(WindowsAzureData):
    def __init__(self):
        self.name = ''
        self.url = ''
        self.properties = Properties()
        self.metadata = Metadata()

class Properties(WindowsAzureData):
    def __init__(self):
        self.last_modified = ''
        self.etag = ''

class Metadata(WindowsAzureData):
    def __init__(self):
        self.metadata_name = ''

class RetentionPolicy(WindowsAzureData):
    def __init__(self):
        self.enabled = False
        self.__dict__['days'] = None

    def get_days(self):
        return self.__dict__['days']

    def set_days(self, value):
        if value == '':
            self.__dict__['days'] = 10
        else:
            self.__dict__['days'] = value

    days = property(fget=get_days, fset=set_days)

class Logging(WindowsAzureData):
    def __init__(self):
        self.version = '1.0'
        self.delete = False
        self.read = False
        self.write = False
        self.retention_policy = RetentionPolicy()

class Metrics(WindowsAzureData):
    def __init__(self):
        self.version = '1.0'
        self.enabled = False
        self.include_apis = None
        self.retention_policy = RetentionPolicy()

class StorageServiceProperties(WindowsAzureData):
    def __init__(self):
        self.logging = Logging()
        self.metrics = Metrics()

class AccessPolicy(WindowsAzureData):
    def __init__(self):
        self.start = ''
        self.expiry = ''
        self.permission = ''

class SignedIdentifier(WindowsAzureData):
    def __init__(self):
        self.id = ''
        self.access_policy = AccessPolicy()

class SignedIdentifiers(WindowsAzureData):
    def __init__(self):
        self.signed_identifiers = []
    def __iter__(self):
        return self.signed_identifiers

class BlobEnumResults(EnumResultsBase):
    def __init__(self):
        EnumResultsBase.__init__(self)
        self.blobs = []
    def __iter__(self):
        return iter(self.blobs)
    def __len__(self):
        return len(self.blobs)
    def __getitem__(self, index):
        return self.blobs[index]

class Blob(WindowsAzureData):
    def __init__(self):
        self.name = ''
        self.snapshot = ''
        self.url = ''
        self.properties = BlobProperties()
        self.metadata = Metadata()
        self.blob_prefix = BlobPrefix()

class BlobProperties(WindowsAzureData):
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
    def __init__(self):
        self.name = ''

class BlobBlock(WindowsAzureData):
    def __init__(self, id=None, size=None):
        self.id = id
        self.size = size

class BlobBlockList(WindowsAzureData):
    def __init__(self):
        self.committed_blocks = []
        self.uncommitted_blocks = []

class BlockList(WindowsAzureData):
    def __init__(self):
        self.committed = []
        self.uncommitted = []
        self.latest = []

class PageRange(WindowsAzureData):
    def __init__(self):
        self.start = 0
        self.end = 0

class PageList:
    def __init__(self):
        self.page_ranges = []
    def __iter__(self):
        return self.page_ranges

class QueueEnumResults(EnumResultsBase):
    def __init__(self):
        EnumResultsBase.__init__(self)
        self.queues = []        
    def __iter__(self):
        return iter(self.queues)
    def __len__(self):
        return len(self.queues)
    def __getitem__(self, index):
        return self.queues[index]

class Queue(WindowsAzureData):
    def __init__(self):
        self.name = ''
        self.url = ''
        self.metadata = Metadata()

class QueueMessageList:
    def __init__(self):
        self.queue_messages = []
    def __iter__(self):
        return iter(self.queue_messages)
    def __len__(self):
        return len(self.queue_messages)
    def __getitem__(self, index):
        return self.queue_messages[index]

class QueueMessage(WindowsAzureData):
    def __init__(self):
        self.message_id = ''
        self.insertion_time = ''
        self.expiration_time = ''
        self.pop_receipt = ''
        self.time_next_visible = ''
        self.dequeue_count = ''
        self.message_text = ''

class TableEnumResult(EnumResultsBase):
    def __init__():
        EnumResultsBase.__init__(self)
        self.tables = []
    def __iter__(self):
        return iter(self.tables)
    def __len__(self):
        return len(self.tables)
    def __getitem__(self, index):
        return self.tables[index]

class Entity(WindowsAzureData):
    pass

class EntityProperty(WindowsAzureData):
    def __init__(self, type=None, value=None):
        self.type = type
        self.value = value
    pass

class Table(WindowsAzureData):
    pass

def _update_storage_header(request):
    if request.method in ['PUT', 'POST', 'MERGE', 'DELETE']:
            request.header.append(('Content-Length', str(len(request.body))))  

    #append addtional headers base on the service
    request.header.append(('x-ms-version', X_MS_VERSION))

    #append x-ms-meta name, values to header
    for name, value in request.header:
        if 'x-ms-meta-name-values' in name and value:
            for meta_name, meta_value in value.iteritems():
                request.header.append(('x-ms-meta-' + meta_name, meta_value))
            request.header.remove((name, value))
            break
    return request

def _update_storage_blob_header(request, account_name, account_key):
    request = _update_storage_header(request)
    current_time = datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
    request.header.append(('x-ms-date', current_time))
    request.header.append(('Content-Type', 'application/octet-stream Charset=UTF-8'))  
    request.header.append(('Authorization', _sign_storage_blob_request(request, account_name, account_key)))

    return request.header

def _update_storage_queue_header(request, account_name, account_key):
    return _update_storage_blob_header(request, account_name, account_key)

def _update_storage_table_header(request, account_name, account_key):
    request = _update_storage_header(request)
    for name, value in request.header:
        if name.lower() == 'content-type':
            break;
    else:
        request.header.append(('Content-Type', 'application/atom+xml'))  
    request.header.append(('DataServiceVersion', '2.0;NetFx'))
    request.header.append(('MaxDataServiceVersion', '2.0;NetFx'))
    current_time = datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
    request.header.append(('x-ms-date', current_time))
    request.header.append(('Date', current_time))
    request.header.append(('Authorization', _sign_storage_table_request(request, account_name, account_key)))
    return request.header

def _sign_storage_blob_request(request, account_name, account_key):
    uri_path = request.uri.split('?')[0]

    x_ms_headers = []
    for name, value in request.header:
        if 'x-ms' in name:
            x_ms_headers.append((name.lower(), value))                
    x_ms_headers.sort()
    #method to sign
    string_to_sign = request.method + '\n'

    #get headers to sign
    headers_to_sign = ['content-encoding', 'content-Language', 'content-length', 
                        'content-md5', 'content-type', 'date', 'if-modified-since', 
                        'if-Match', 'if-none-match', 'if-unmodified-since', 'range']
    for header in headers_to_sign:
        for name, value in request.header:
            if value and name.lower() == header:
                string_to_sign += value + '\n'
                find_header = True  #remove
                break
        else:
            string_to_sign += '\n'

    #get x-ms header to sign if it is not storage table
    x_ms_headers = []
    for name, value in request.header:
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
    uri_path = request.uri.split('?')[0]

    string_to_sign = request.method + '\n'
    headers_to_sign = ['content-md5', 'content-type', 'date']
    for header in headers_to_sign:
        for name, value in request.header:
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

def convert_entity_to_xml(source, use_local_storage=True):

    entity_body = '<m:properties>{properties}</m:properties>'

    if type(source) is types.InstanceType or isinstance(source, WindowsAzureData):
        source = vars(source)

    properties_str = ''
    
    for name, value in source.iteritems():
        mtype = ''
        if type(value) is types.IntType:
            mtype = 'Edm.Int32'
        elif type(value) is types.FloatType:
            mtype = 'Edm.Double'
        elif type(value) is types.BooleanType:
            mtype = 'Edm.Boolean'
        elif isinstance(value, datetime):
            mtype = 'Edm.DateTime'
            value = value.strftime('%Y-%m-%dT%H:%M:%S')
        elif isinstance(value, EntityProperty):
            mtype = value.type
            value = value.value

        properties_str += ''.join(['<d:', name])
        if mtype:
            properties_str += ''.join([' m:type="', mtype, '"'])
        properties_str += ''.join(['>', str(value), '</d:', name, '>'])

    entity_body = entity_body.format(properties=properties_str)
    xmlstr = create_entry(entity_body)
    return xmlstr

def convert_table_to_xml(table_name):
    return convert_entity_to_xml({'TableName': table_name})

def convert_block_list_to_xml(block_list):
    if block_list is None:
        return ''
    xml = '<?xml version="1.0" encoding="utf-8"?><BlockList>'
    for value in block_list.latest:
        xml += '<Latest>%s</Latest>' % base64.b64encode(value)
    for value in block_list.committed:
        xml += '<Committed>%s</Commited>' % base64.b64encode(value)
    for value in block_list.uncommitted:
        xml += '<Uncommitted>%s</Uncommitted>' % base64.b64encode(value)
    return xml+'</BlockList>'

def convert_xml_to_block_list(xmlstr):
    xmlstr = normalize_xml(xmlstr)
    blob_block_list = BlobBlockList()
    
    xmldoc = minidom.parseString(xmlstr)
    
    xml_committed_blocks_list = xmldoc.getElementsByTagName('CommittedBlocks')
    for xml_committed_blocks in xml_committed_blocks_list:
        xml_blocks = xml_committed_blocks.getElementsByTagName('Block')
        for xml_block in xml_blocks:
            xml_block_id = base64.b64decode(xml_block.getElementsByTagName('Name')[0].firstChild.nodeValue)
            xml_block_size = int(xml_block.getElementsByTagName('Size')[0].firstChild.nodeValue)
            blob_block_list.committed_blocks.append(BlobBlock(xml_block_id, xml_block_size))  
                         
    xml_uncommitted_blocks_list = xmldoc.getElementsByTagName('UncommittedBlocks')
    for xml_uncommitted_blocks in xml_uncommitted_blocks_list:
        xml_blocks = xml_uncommitted_blocks.getElementsByTagName('Block')
        for xml_block in xml_blocks:
            xml_block_id = base64.b64decode(xml_block.getElementsByTagName('Name')[0].firstChild.nodeValue)
            xml_block_size = int(xml_block.getElementsByTagName('Size')[0].firstChild.nodeValue)
            blob_block_list.uncommitted_blocks.append(BlobBlock(xml_block_id, xml_block_size))

    return blob_block_list

def convert_xml_to_entity(xmlstr):
    xmlstr = normalize_xml(xmlstr)
    xmlstr = remove_xmltag_namespace(xmlstr)
    xmldoc = minidom.parseString(xmlstr)
    xml_properties = xmldoc.getElementsByTagName('properties')
    
    if not xml_properties:
        return None

    entity = Entity()
    for xml_property in xml_properties[0].childNodes:
        if xml_property.firstChild:
            name = xml_property.nodeName
            if name in ['Timestamp']:
                continue
            value = xml_property.firstChild.nodeValue
            
            isnull = xml_property.getAttribute('null')
            mtype = xml_property.getAttribute('type')
            property = EntityProperty()
            if not isnull and not mtype:
                setattr(entity, name, value)
            else:
                setattr(property, 'value', value)
                if isnull:
                    setattr(property, 'isnull', str(isnull))            
                if mtype:
                    setattr(property, 'type', str(mtype))
                setattr(entity, name, property)

    return entity

def convert_xml_to_table(xmlstr):
    xmlstr = normalize_xml(xmlstr)
    xmlstr = remove_xmltag_namespace(xmlstr)
    table = Table()
    entity = convert_xml_to_entity(xmlstr)
    setattr(table, 'name', entity.TableName)
    for name, value in get_entry_properties(xmlstr, ['updated', 'name']).iteritems():
       setattr(table, name, value)
    return table

def _storage_error_handler(http_error):
    if http_error.status == 409:
        raise WindowsAzureError('Conflict')
    elif http_error.status == 404:
        raise WindowsAzureError('Not Found')
    else:
        raise WindowsAzureError('Unknown Error')
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
import threading
import types

from datetime import datetime
from dateutil import parser
from dateutil.tz import tzutc
from time import sleep, time
from wsgiref.handlers import format_date_time
from azure.common import (
    WindowsAzureError,
)
from ._internal import (
    WindowsAzureData,
    METADATA_NS,
    url_quote,
    xml_escape,
    _create_entry,
    _decode_base64_to_text,
    _decode_base64_to_bytes,
    _encode_base64,
    _general_error_handler,
    _list_of,
    _parse_response_for_dict,
    _sign_string,
    _unicode_type,
    _ERROR_CANNOT_SERIALIZE_VALUE_TO_ENTITY,
    _etree_entity_feed_namespaces,
    _make_etree_ns_attr_name,
    _get_etree_tag_name_without_ns,
    _get_etree_text,
    ETree,
    _ETreeXmlToObject,
    BLOB_SERVICE_HOST_BASE,
    TABLE_SERVICE_HOST_BASE,
    QUEUE_SERVICE_HOST_BASE,
)


__author__ = 'Microsoft Corp. <ptvshelp@microsoft.com>'
__version__ = '0.20.0'

# x-ms-version for storage service.
X_MS_VERSION = '2014-02-14'


from .models import (
    EnumResultsBase,
    ContainerEnumResults,
    Container,
    Properties,
    RetentionPolicy,
    Logging,
    HourMetrics,
    MinuteMetrics,
    StorageServiceProperties,
    AccessPolicy,
    SignedIdentifier,
    SignedIdentifiers,
    BlobEnumResults,
    BlobResult,
    Blob,
    BlobProperties,
    BlobPrefix,
    BlobBlock,
    BlobBlockList,
    PageRange,
    PageList,
    QueueEnumResults,
    Queue,
    QueueMessagesList,
    QueueMessage,
    Entity,
    EntityProperty,
    Table,
    ContainerSharedAccessPermissions,
    BlobSharedAccessPermissions,
    TableSharedAccessPermissions,
    QueueSharedAccessPermissions,
)


def _parse_blob_enum_results_list(response):
    respbody = response.body
    return_obj = BlobEnumResults()
    enum_results = ETree.fromstring(respbody)

    for child in enum_results.findall('./Blobs/Blob'):
        return_obj.blobs.append(_ETreeXmlToObject.fill_instance_element(child, Blob))

    for child in enum_results.findall('./Blobs/BlobPrefix'):
        return_obj.prefixes.append(
            _ETreeXmlToObject.fill_instance_element(child, BlobPrefix))

    for name, value in vars(return_obj).items():
        if name == 'blobs' or name == 'prefixes':
            continue
        value = _ETreeXmlToObject.fill_data_member(enum_results, name, value)
        if value is not None:
            setattr(return_obj, name, value)

    return return_obj


def _update_storage_header(request):
    ''' add additional headers for storage request. '''
    if request.body:
        assert isinstance(request.body, bytes)

    # if it is PUT, POST, MERGE, DELETE, need to add content-length to header.
    if request.method in ['PUT', 'POST', 'MERGE', 'DELETE']:
        request.headers.append(('Content-Length', str(len(request.body))))

    # append addtional headers base on the service
    request.headers.append(('x-ms-version', X_MS_VERSION))

    # append x-ms-meta name, values to header
    for name, value in request.headers:
        if 'x-ms-meta-name-values' in name and value:
            for meta_name, meta_value in value.items():
                request.headers.append(('x-ms-meta-' + meta_name, meta_value))
            request.headers.remove((name, value))
            break
    return request


def _update_storage_blob_header(request, authentication):
    ''' add additional headers for storage blob request. '''

    request = _update_storage_header(request)
    current_time = format_date_time(time())
    request.headers.append(('x-ms-date', current_time))
    request.headers.append(
        ('Content-Type', 'application/octet-stream Charset=UTF-8'))
    authentication.sign_request(request)

    return request.headers


def _update_storage_queue_header(request, authentication):
    return _update_storage_blob_header(request, authentication)


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
            raise WindowsAzureError(
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


def _convert_block_list_to_xml(block_id_list):
    '''
    Convert a block list to xml to send.

    block_id_list:
        a str list containing the block ids that are used in put_block_list.
    Only get block from latest blocks.
    '''
    if block_id_list is None:
        return ''
    xml = '<?xml version="1.0" encoding="utf-8"?><BlockList>'
    for value in block_id_list:
        xml += '<Latest>{0}</Latest>'.format(_encode_base64(value))

    return xml + '</BlockList>'


def _convert_signed_identifiers_to_xml(signed_identifiers):
    if signed_identifiers is None:
        return ''
    xml = '<?xml version="1.0" encoding="utf-8"?><SignedIdentifiers>'
    for signed_identifier in signed_identifiers:
        xml += '<SignedIdentifier>'
        xml += '<Id>{0}</Id>'.format(signed_identifier.id)
        xml += '<AccessPolicy>'
        if signed_identifier.access_policy.start:
            xml += '<Start>{0}</Start>'.format(signed_identifier.access_policy.start)
        if signed_identifier.access_policy.expiry:
            xml += '<Expiry>{0}</Expiry>'.format(signed_identifier.access_policy.expiry)
        if signed_identifier.access_policy.permission:
            xml += '<Permission>{0}</Permission>'.format(signed_identifier.access_policy.permission)
        xml += '</AccessPolicy>'
        xml += '</SignedIdentifier>'

    return xml + '</SignedIdentifiers>'


def _create_blob_result(response):
    blob_properties = _parse_response_for_dict(response)
    return BlobResult(response.body, blob_properties)


def _convert_block_etree_element_to_blob_block(block_element):
    block_id = _decode_base64_to_text(block_element.findtext('./Name', ''))
    block_size = int(block_element.findtext('./Size'))

    return BlobBlock(block_id, block_size)


def _convert_response_to_block_list(response):
    '''
    Converts xml response to block list class.
    '''
    block_list = BlobBlockList()

    list_element = ETree.fromstring(response.body)

    for block_element in list_element.findall('./CommittedBlocks/Block'):
        block = _convert_block_etree_element_to_blob_block(block_element)
        block_list.committed_blocks.append(block)

    for block_element in list_element.findall('./UncommittedBlocks/Block'):
        block = _convert_block_etree_element_to_blob_block(block_element)
        block_list.uncommitted_blocks.append(block)

    return block_list


def _remove_prefix(name):
    colon = name.find(':')
    if colon != -1:
        return name[colon + 1:]
    return name


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


class _BlobChunkDownloader(object):
    def __init__(self, blob_service, container_name, blob_name, blob_size,
                 chunk_size, stream, parallel, max_retries, retry_wait,
                 progress_callback):
        self.blob_service = blob_service
        self.container_name = container_name
        self.blob_name = blob_name
        self.blob_size = blob_size
        self.chunk_size = chunk_size
        self.stream = stream
        self.stream_start = stream.tell() if parallel else None
        self.stream_lock = threading.Lock() if parallel else None
        self.progress_callback = progress_callback
        self.progress_total = 0
        self.progress_lock = threading.Lock() if parallel else None
        self.max_retries = max_retries
        self.retry_wait = retry_wait

    def get_chunk_offsets(self):
        index = 0
        while index < self.blob_size:
            yield index
            index += self.chunk_size

    def process_chunk(self, chunk_offset):
        chunk_data = self._download_chunk_with_retries(chunk_offset)
        length = len(chunk_data)
        if length > 0:
            self._write_to_stream(chunk_data, chunk_offset)
            self._update_progress(length)

    def _update_progress(self, length):
        if self.progress_callback is not None:
            if self.progress_lock is not None:
                with self.progress_lock:
                    self.progress_total += length
                    total = self.progress_total
            else:
                self.progress_total += length
                total = self.progress_total
            self.progress_callback(total, self.blob_size)

    def _write_to_stream(self, chunk_data, chunk_offset):
        if self.stream_lock is not None:
            with self.stream_lock:
                self.stream.seek(self.stream_start + chunk_offset)
                self.stream.write(chunk_data)
        else:
            self.stream.write(chunk_data)

    def _download_chunk_with_retries(self, chunk_offset):
        range_id = 'bytes={0}-{1}'.format(chunk_offset, chunk_offset + self.chunk_size - 1)
        retries = self.max_retries
        while True:
            try:
                return self.blob_service.get_blob(
                    self.container_name,
                    self.blob_name,
                    x_ms_range=range_id
                )
            except Exception:
                if retries > 0:
                    retries -= 1
                    sleep(self.retry_wait)
                else:
                    raise


class _BlobChunkUploader(object):
    def __init__(self, blob_service, container_name, blob_name, blob_size,
                 chunk_size, stream, parallel, max_retries, retry_wait,
                 progress_callback, x_ms_lease_id):
        self.blob_service = blob_service
        self.container_name = container_name
        self.blob_name = blob_name
        self.blob_size = blob_size
        self.chunk_size = chunk_size
        self.stream = stream
        self.stream_start = stream.tell() if parallel else None
        self.stream_lock = threading.Lock() if parallel else None
        self.progress_callback = progress_callback
        self.progress_total = 0
        self.progress_lock = threading.Lock() if parallel else None
        self.max_retries = max_retries
        self.retry_wait = retry_wait
        self.x_ms_lease_id = x_ms_lease_id

    def get_chunk_offsets(self):
        index = 0
        if self.blob_size is None:
            # we don't know the size of the stream, so we have no
            # choice but to seek
            while True:
                data = self._read_from_stream(index, 1)
                if not data:
                    break
                yield index
                index += self.chunk_size
        else:
            while index < self.blob_size:
                yield index
                index += self.chunk_size

    def process_chunk(self, chunk_offset):
        size = self.chunk_size
        if self.blob_size is not None:
            size = min(size, self.blob_size - chunk_offset)
        chunk_data = self._read_from_stream(chunk_offset, size)
        return self._upload_chunk_with_retries(chunk_offset, chunk_data)

    def process_all_unknown_size(self):
        assert self.stream_lock is None
        range_ids = []
        index = 0
        while True:
            data = self._read_from_stream(None, self.chunk_size)
            if data:
                index += len(data)
                range_id = self._upload_chunk_with_retries(index, data)
                range_ids.append(range_id)
            else:
                break

        return range_ids

    def _read_from_stream(self, offset, count):
        if self.stream_lock is not None:
            with self.stream_lock:
                self.stream.seek(self.stream_start + offset)
                data = self.stream.read(count)
        else:
            data = self.stream.read(count)
        return data

    def _update_progress(self, length):
        if self.progress_callback is not None:
            if self.progress_lock is not None:
                with self.progress_lock:
                    self.progress_total += length
                    total = self.progress_total
            else:
                self.progress_total += length
                total = self.progress_total
            self.progress_callback(total, self.blob_size)

    def _upload_chunk_with_retries(self, chunk_offset, chunk_data):
        retries = self.max_retries
        while True:
            try:
                range_id = self._upload_chunk(chunk_offset, chunk_data) 
                self._update_progress(len(chunk_data))
                return range_id
            except Exception:
                if retries > 0:
                    retries -= 1
                    sleep(self.retry_wait)
                else:
                    raise


class _BlockBlobChunkUploader(_BlobChunkUploader):
    def _upload_chunk(self, chunk_offset, chunk_data):
        range_id = url_quote(_encode_base64('{0:032d}'.format(chunk_offset)))
        self.blob_service.put_block(
            self.container_name,
            self.blob_name,
            chunk_data,
            range_id,
            x_ms_lease_id=self.x_ms_lease_id
        )
        return range_id


class _PageBlobChunkUploader(_BlobChunkUploader):
    def _upload_chunk(self, chunk_offset, chunk_data):
        range_id = 'bytes={0}-{1}'.format(chunk_offset, chunk_offset + len(chunk_data) - 1)
        self.blob_service.put_page(
            self.container_name,
            self.blob_name,
            chunk_data,
            range_id,
            'update',
            x_ms_lease_id=self.x_ms_lease_id
        )
        return range_id


def _download_blob_chunks(blob_service, container_name, blob_name,
                          blob_size, block_size, stream, max_connections,
                          max_retries, retry_wait, progress_callback):
    downloader = _BlobChunkDownloader(
        blob_service,
        container_name,
        blob_name,
        blob_size,
        block_size,
        stream,
        max_connections > 1,
        max_retries,
        retry_wait,
        progress_callback,
    )

    if progress_callback is not None:
        progress_callback(0, blob_size)

    if max_connections > 1:
        import concurrent.futures
        executor = concurrent.futures.ThreadPoolExecutor(max_connections)
        result = list(executor.map(downloader.process_chunk, downloader.get_chunk_offsets()))
    else:
        for range_start in downloader.get_chunk_offsets():
            downloader.process_chunk(range_start)


def _upload_blob_chunks(blob_service, container_name, blob_name,
                        blob_size, block_size, stream, max_connections,
                        max_retries, retry_wait, progress_callback,
                        x_ms_lease_id, uploader_class):
    uploader = uploader_class(
        blob_service,
        container_name,
        blob_name,
        blob_size,
        block_size,
        stream,
        max_connections > 1,
        max_retries,
        retry_wait,
        progress_callback,
        x_ms_lease_id,
    )

    if progress_callback is not None:
        progress_callback(0, blob_size)

    if max_connections > 1:
        import concurrent.futures
        executor = concurrent.futures.ThreadPoolExecutor(max_connections)
        range_ids = list(executor.map(uploader.process_chunk, uploader.get_chunk_offsets()))
    else:
        if blob_size is not None:
            range_ids = [uploader.process_chunk(start) for start in uploader.get_chunk_offsets()]
        else:
            range_ids = uploader.process_all_unknown_size()

    return range_ids


def _storage_error_handler(http_error):
    ''' Simple error handler for storage service. '''
    return _general_error_handler(http_error)


class StorageSASAuthentication(object):
    def __init__(self, sas_token):
        self.sas_token = sas_token

    def sign_request(self, request):
        if '?' in request.path:
            request.path += '&'
        else:
            request.path += '?'

        request.path += self.sas_token


class _StorageSharedKeyAuthentication(object):
    def __init__(self, account_name, account_key):
        self.account_name = account_name
        self.account_key = account_key

    def _get_headers(self, request, headers_to_sign):
        headers = {
            name.lower() : value for name, value in request.headers if value
        }
        return '\n'.join(headers.get(x, '') for x in headers_to_sign) + '\n'

    def _get_verb(self, request):
        return request.method + '\n'

    def _get_canonicalized_resource(self, request):
        uri_path = request.path.split('?')[0]
        return '/' + self.account_name + uri_path

    def _get_canonicalized_headers(self, request):
        string_to_sign = ''
        x_ms_headers = []
        for name, value in request.headers:
            if name.startswith('x-ms-'):
                x_ms_headers.append((name.lower(), value))
        x_ms_headers.sort()
        for name, value in x_ms_headers:
            if value:
                string_to_sign += ''.join([name, ':', value, '\n'])
        return string_to_sign

    def _add_authorization_header(self, request, string_to_sign):
        signature = _sign_string(self.account_key, string_to_sign)
        auth_string = 'SharedKey ' + self.account_name + ':' + signature
        request.headers.append(('Authorization', auth_string))


class StorageSharedKeyAuthentication(_StorageSharedKeyAuthentication):
    def sign_request(self, request):
        string_to_sign = \
            self._get_verb(request) + \
            self._get_headers(
                request,
                [
                    'content-encoding', 'content-language', 'content-length',
                    'content-md5', 'content-type', 'date', 'if-modified-since',
                    'if-match', 'if-none-match', 'if-unmodified-since', 'range'
                ]
            ) + \
            self._get_canonicalized_headers(request) + \
            self._get_canonicalized_resource(request) + \
            self._get_canonicalized_resource_query(request)

        self._add_authorization_header(request, string_to_sign)

    def _get_canonicalized_resource_query(self, request):
        query_to_sign = request.query
        query_to_sign.sort()

        string_to_sign = ''
        current_name = ''
        for name, value in query_to_sign:
            if value:
                if current_name != name:
                    string_to_sign += '\n' + name + ':' + value
                    current_name = name
                else:
                    string_to_sign += '\n' + ',' + value

        return string_to_sign


class StorageTableSharedKeyAuthentication(_StorageSharedKeyAuthentication):
    def sign_request(self, request):
        string_to_sign = \
            self._get_verb(request) + \
            self._get_headers(
                request,
                ['content-md5', 'content-type', 'date'],
            ) + \
            self._get_canonicalized_resource(request) + \
            self._get_canonicalized_resource_query(request)

        self._add_authorization_header(request, string_to_sign)

    def _get_canonicalized_resource_query(self, request):
        for name, value in request.query:
            if name == 'comp':
                return '?comp=' + value
        return ''


class StorageNoAuthentication(object):
    def sign_request(self, request):
        pass


class StorageConnectionParameters(object):
    '''
    Extract connection parameters from a connection string.
    
    This is based on http://azure.microsoft.com/en-us/documentation/articles/storage-configure-connection-string/ .
       
    NOTE "(Blob|Table|Queue|File)Endpoint" are not supported.
         "SharedAccessSignature" is not supported.
         dev_host, timeout, and sas_token cannot be specified with a connection string.
    '''
    def __init__(self, connection_string = ''):
        connection_params = dict(s.split('=',1) for s in connection_string.split(';'))

        self.account_name = connection_params.get('AccountName', None)
        self.account_key = connection_params.get('AccountKey', None)
        self.protocol = connection_params.get('DefaultEndpointsProtocol', 'https').lower()
        endpoint_suffix = connection_params.get('EndpointSuffix', None)
        self.host_base_blob = BLOB_SERVICE_HOST_BASE if endpoint_suffix is None \
                              else ".blob.{}".format(endpoint_suffix)
        self.host_base_table = TABLE_SERVICE_HOST_BASE if endpoint_suffix is None \
                               else ".table.{}".format(endpoint_suffix)
        self.host_base_queue = QUEUE_SERVICE_HOST_BASE if endpoint_suffix is None \
                               else ".queue.{}".format(endpoint_suffix)


# make these available just from storage.
from .blobservice import BlobService
from .queueservice import QueueService
from .tableservice import TableService
from .cloudstorageaccount import CloudStorageAccount
from .sharedaccesssignature import (
    SharedAccessSignature,
    SharedAccessPolicy,
)

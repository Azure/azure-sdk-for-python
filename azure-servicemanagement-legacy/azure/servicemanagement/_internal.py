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
import ast
import base64
import hashlib
import hmac
import sys
import types
import warnings

if sys.version_info < (3,):
    from cStringIO import StringIO
    from urllib2 import quote as url_quote
    from urllib2 import unquote as url_unquote
    _strtype = basestring
else:
    from io import StringIO
    from urllib.parse import quote as url_quote
    from urllib.parse import unquote as url_unquote
    _strtype = str

from datetime import datetime
from xml.sax.saxutils import escape as xml_escape

from azure.common import (
    WindowsAzureError,
    WindowsAzureConflictError,
    WindowsAzureMissingResourceError,
    WindowsAzureBatchOperationError,
    WindowsAzureAsyncOperationError,
)

#--------------------------------------------------------------------------
# constants

# Live ServiceClient URLs
MANAGEMENT_HOST = 'management.core.windows.net'

# Default timeout for http requests (in secs)
DEFAULT_HTTP_TIMEOUT = 65

# All of our error messages
_ERROR_CONFLICT = 'Conflict ({0})'
_ERROR_NOT_FOUND = 'Not found ({0})'
_ERROR_UNKNOWN = 'Unknown error ({0})'
_ERROR_VALUE_NONE = '{0} should not be None.'
_ERROR_ASYNC_OP_FAILURE = 'Asynchronous operation did not succeed.'
_ERROR_ASYNC_OP_TIMEOUT = 'Timed out waiting for async operation to complete.'

METADATA_NS = 'http://schemas.microsoft.com/ado/2007/08/dataservices/metadata'


class WindowsAzureData(object):

    ''' This is the base of data class.
    It is only used to check whether it is instance or not. '''
    pass


class Feed(object):
    pass


class _Base64String(str):
    pass


class HeaderDict(dict):

    def __getitem__(self, index):
        return super(HeaderDict, self).__getitem__(index.lower())


def _encode_base64(data):
    if isinstance(data, _unicode_type):
        data = data.encode('utf-8')
    encoded = base64.b64encode(data)
    return encoded.decode('utf-8')


def _decode_base64_to_bytes(data):
    if isinstance(data, _unicode_type):
        data = data.encode('utf-8')
    return base64.b64decode(data)


def _decode_base64_to_text(data):
    decoded_bytes = _decode_base64_to_bytes(data)
    return decoded_bytes.decode('utf-8')


# TODO: check if this is used
def _get_readable_id(id_name, id_prefix_to_skip):
    """simplified an id to be more friendly for us people"""
    # id_name is in the form 'https://namespace.host.suffix/name'
    # where name may contain a forward slash!
    pos = id_name.find('//')
    if pos != -1:
        pos += 2
        if id_prefix_to_skip:
            pos = id_name.find(id_prefix_to_skip, pos)
            if pos != -1:
                pos += len(id_prefix_to_skip)
        pos = id_name.find('/', pos)
        if pos != -1:
            return id_name[pos + 1:]
    return id_name


def _create_entry(entry_body):
    ''' Adds common part of entry to a given entry body and return the whole
    xml. '''
    updated_str = datetime.utcnow().isoformat()
    if datetime.utcnow().utcoffset() is None:
        updated_str += '+00:00'

    entry_start = '''<?xml version="1.0" encoding="utf-8" standalone="yes"?>
<entry xmlns:d="http://schemas.microsoft.com/ado/2007/08/dataservices" xmlns:m="http://schemas.microsoft.com/ado/2007/08/dataservices/metadata" xmlns="http://www.w3.org/2005/Atom" >
<title /><updated>{updated}</updated><author><name /></author><id />
<content type="application/xml">
    {body}</content></entry>'''
    return entry_start.format(updated=updated_str, body=entry_body)


def _to_datetime(strtime):
    return datetime.strptime(strtime, "%Y-%m-%dT%H:%M:%S.%f")

_KNOWN_SERIALIZATION_XFORMS = {
    'include_apis': 'IncludeAPIs',
    'message_id': 'MessageId',
    'content_md5': 'Content-MD5',
    'last_modified': 'Last-Modified',
    'cache_control': 'Cache-Control',
    'account_admin_live_email_id': 'AccountAdminLiveEmailId',
    'service_admin_live_email_id': 'ServiceAdminLiveEmailId',
    'subscription_id': 'SubscriptionID',
    'fqdn': 'FQDN',
    'private_id': 'PrivateID',
    'os_virtual_hard_disk': 'OSVirtualHardDisk',
    'logical_disk_size_in_gb': 'LogicalDiskSizeInGB',
    'logical_size_in_gb': 'LogicalSizeInGB',
    'os': 'OS',
    'persistent_vm_downtime_info': 'PersistentVMDowntimeInfo',
    'copy_id': 'CopyId',
    'os_state': 'OSState',
    'vm_image': 'VMImage',
    'vm_images': 'VMImages',
    'os_disk_configuration': 'OSDiskConfiguration',
    'public_ips': 'PublicIPs', 
    'public_ip': 'PublicIP', 
    'supported_os': 'SupportedOS',
    'reserved_ip': 'ReservedIP',
    'reserved_ips': 'ReservedIPs',
    'aad_tenant_id': 'AADTenantID',
    'start_ip_address': 'StartIPAddress',
    'end_ip_address': 'EndIPAddress',
    'operation_id': 'OperationId',
    'operation_object_id': 'OperationObjectId',
    'client_ip': 'ClientIP',
    'status_id': 'ID',
    'virtual_ips': 'VirtualIPs',
    'virtual_ip': 'VirtualIP'
    }


def _get_serialization_name(element_name):
    """converts a Python name into a serializable name"""
    known = _KNOWN_SERIALIZATION_XFORMS.get(element_name)
    if known is not None:
        return known

    if element_name.startswith('x_ms_'):
        return element_name.replace('_', '-')
    if element_name.endswith('_id'):
        element_name = element_name.replace('_id', 'ID')
    for name in ['content_', 'last_modified', 'if_', 'cache_control']:
        if element_name.startswith(name):
            element_name = element_name.replace('_', '-_')

    return ''.join(name.capitalize() for name in element_name.split('_'))

if sys.version_info < (3,):
    _unicode_type = unicode

    def _str(value):
        if isinstance(value, unicode):
            return value.encode('utf-8')

        return str(value)
else:
    _str = str
    _unicode_type = str


def _str_or_none(value):
    if value is None:
        return None

    return _str(value)


def _int_or_none(value):
    if value is None:
        return None

    return str(int(value))


def _bool_or_none(value):
    if value is None:
        return None

    if isinstance(value, bool):
        if value:
            return 'true'
        else:
            return 'false'

    return str(value)


# TODO: check if this is used
def _convert_class_to_xml(source, xml_prefix=True):
    if source is None:
        return ''

    xmlstr = ''
    if xml_prefix:
        xmlstr = '<?xml version="1.0" encoding="utf-8"?>'

    if isinstance(source, list):
        for value in source:
            xmlstr += _convert_class_to_xml(value, False)
    elif isinstance(source, WindowsAzureData):
        class_name = source.__class__.__name__
        xmlstr += '<' + class_name + '>'
        for name, value in vars(source).items():
            if value is not None:
                if isinstance(value, list) or \
                    isinstance(value, WindowsAzureData):
                    xmlstr += _convert_class_to_xml(value, False)
                else:
                    xmlstr += ('<' + _get_serialization_name(name) + '>' +
                               xml_escape(str(value)) + '</' +
                               _get_serialization_name(name) + '>')
        xmlstr += '</' + class_name + '>'
    return xmlstr


def _set_continuation_from_response_headers(feeds, response):
    x_ms_continuation = HeaderDict()
    for name, value in response.headers:
        if 'x-ms-continuation' in name:
            x_ms_continuation[name[len('x-ms-continuation') + 1:]] = value
    if x_ms_continuation:
        setattr(feeds, 'x_ms_continuation', x_ms_continuation)


def _validate_not_none(param_name, param):
    if param is None:
        raise TypeError(_ERROR_VALUE_NONE.format(param_name))


def _get_request_body(request_body):
    '''Converts an object into a request body.  If it's None
    we'll return an empty string, if it's one of our objects it'll
    convert it to XML and return it.  Otherwise we just use the object
    directly'''
    if request_body is None:
        return b''

    # TODO: check if this is used
    if isinstance(request_body, WindowsAzureData):
        request_body = _convert_class_to_xml(request_body)

    if isinstance(request_body, bytes):
        return request_body

    if isinstance(request_body, _unicode_type):
        return request_body.encode('utf-8')

    request_body = str(request_body)
    if isinstance(request_body, _unicode_type):
        return request_body.encode('utf-8')

    return request_body


class _dict_of(dict):

    """a dict which carries with it the xml element names for key,val.
    Used for deserializaion and construction of the lists"""

    def __init__(self, pair_xml_element_name, key_xml_element_name,
                 value_xml_element_name):
        self.pair_xml_element_name = pair_xml_element_name
        self.key_xml_element_name = key_xml_element_name
        self.value_xml_element_name = value_xml_element_name
        super(_dict_of, self).__init__()


class _list_of(list):

    """a list which carries with it the type that's expected to go in it.
    Used for deserializaion and construction of the lists"""

    def __init__(self, list_type, xml_element_name=None):
        self.list_type = list_type
        if xml_element_name is None:
            self.xml_element_name = list_type.__name__
        else:
            self.xml_element_name = xml_element_name
        super(_list_of, self).__init__()


class _scalar_list_of(list):

    """a list of scalar types which carries with it the type that's
    expected to go in it along with its xml element name.
    Used for deserializaion and construction of the lists"""

    def __init__(self, list_type, xml_element_name):
        self.list_type = list_type
        self.xml_element_name = xml_element_name
        super(_scalar_list_of, self).__init__()
        
class _xml_attribute:
    
    """a accessor to XML attributes
    expected to go in it along with its xml element name.
    Used for deserialization and construction"""
    
    def __init__(self, xml_element_name):
        self.xml_element_name = xml_element_name




def _general_error_handler(http_error):
    ''' Simple error handler for azure.'''
    if http_error.status == 409:
        raise WindowsAzureConflictError(
            _ERROR_CONFLICT.format(str(http_error)))
    elif http_error.status == 404:
        raise WindowsAzureMissingResourceError(
            _ERROR_NOT_FOUND.format(str(http_error)))
    else:
        if http_error.respbody is not None:
            raise WindowsAzureError(
                _ERROR_UNKNOWN.format(str(http_error)) + '\n' + \
                    http_error.respbody.decode('utf-8-sig'))
        else:
            raise WindowsAzureError(_ERROR_UNKNOWN.format(str(http_error)))


def _lower(text):
    return text.lower()

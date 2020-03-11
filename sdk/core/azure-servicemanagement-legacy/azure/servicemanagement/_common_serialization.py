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
import sys

from datetime import datetime
from xml.sax.saxutils import escape as xml_escape

from ._common_models import (
    WindowsAzureData,
    HeaderDict,
    _unicode_type,
)


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
    'virtual_ip': 'VirtualIP',
    'recommended_vm_size': 'RecommendedVMSize'
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

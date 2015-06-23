#-------------------------------------------------------------------------
# Copyright (c) 2015 SUSE Linux GmbH.  All rights reserved.
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
from time import sleep
from azure import (WindowsAzureData,
                   WindowsAzureError,
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
                   )

# x-ms-version for files service.
X_MS_VERSION = '2014-02-14'

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

def _update_storage_files_header(request, authentication):
    ''' add/update additional headers for storage files request. '''

    request = _update_storage_header(request)
    current_time = datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
    request.headers.append(('x-ms-date', current_time))
    request.headers.append(
        ('Content-Type', 'application/octet-stream Charset=UTF-8'))
    authentication.sign_request(request)

    return request.headers


class EnumResultsBase(object):

    ''' base class for EnumResults. '''

    def __init__(self):
        self.prefix = u''
        self.marker = u''
        self.max_results = 0
        self.next_marker = u''


class ShareEnumResults(EnumResultsBase):

    ''' Files share list. '''

    def __init__(self):
        EnumResultsBase.__init__(self)
        self.shares = _list_of(Share)

    def __iter__(self):
        return iter(self.shares)

    def __len__(self):
        return len(self.shares)

    def __getitem__(self, index):
        return self.shares[index]


class Properties(WindowsAzureData):

    ''' Files ahre's properties class. '''

    def __init__(self):
        self.last_modified = u''
        self.etag = u''


class Share(WindowsAzureData):

    ''' Share container class. '''

    def __init__(self):
        self.name = u''
        self.url = u''
        self.properties = Properties()
        self.metadata = {}



# make these available just from files.
from azure.files.filesservice import FilesService

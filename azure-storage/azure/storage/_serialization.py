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
from ._common_error import (
    _general_error_handler,
)
from .constants import (
    X_MS_VERSION,
)


def _storage_error_handler(http_error):
    ''' Simple error handler for storage service. '''
    return _general_error_handler(http_error)


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


def _update_storage_header(request):
    ''' add additional headers for storage request. '''
    if request.body:
        assert isinstance(request.body, bytes)

    # if it is PUT, POST, MERGE, DELETE, need to add content-length to header.
    if request.method in ['PUT', 'POST', 'MERGE', 'DELETE']:
        request.headers.append(('Content-Length', str(len(request.body))))

    # append addtional headers based on the service
    request.headers.append(('x-ms-version', X_MS_VERSION))

    # append x-ms-meta name, values to header
    for name, value in request.headers:
        if 'x-ms-meta-name-values' in name and value:
            for meta_name, meta_value in value.items():
                request.headers.append(('x-ms-meta-' + meta_name, meta_value))
            request.headers.remove((name, value))
            break
    return request

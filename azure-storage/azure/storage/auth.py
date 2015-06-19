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
from ._common_conversion import (
    _sign_string,
)


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


class StorageSASAuthentication(object):
    def __init__(self, sas_token):
        self.sas_token = sas_token

    def sign_request(self, request):
        if '?' in request.path:
            request.path += '&'
        else:
            request.path += '?'

        request.path += self.sas_token

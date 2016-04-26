# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft and contributors.  All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#
# See the License for the specific language governing permissions and
# limitations under the License.
# --------------------------------------------------------------------------

import time
import keyring
import ast
import base64
import hmac
import hashlib
import datetime

import requests
from requests.auth import AuthBase
from msrest.authentication import Authentication
from msrest import Serializer

try:
    from urlparse import urlparse, parse_qs

except ImportError:
    from urllib.parse import urlparse, parse_qs

class SharedKeyAuth(AuthBase):

    headers_to_sign = [
        'content-encoding',
        'content-language',
        'content-length',
        'content-md5',
        'content-type',
        'date',
        'if-modified-since',
        'if-match',
        'if-none-match',
        'if-unmodified-since',
        'range']

    def __init__(self, header, account_name, key):
        self._header = header
        self._account_name = account_name
        self._key = key

    def __call__(self, request):

        if not request.headers.get('ocp-date'):
            request.headers['ocp-date'] = Serializer.serialize_rfc(
                datetime.datetime.utcnow())

        url = urlparse(request.url)
        uri_path = url.path
        uri_path = uri_path.replace('%5C', '/')
        uri_path = uri_path.replace('%2F', '/')

        # method to sign
        string_to_sign = request.method + '\n'

        # get headers to sign
        request_header_dict = {
            key.lower(): val for key, val in request.headers.items() if val}

        request_headers = [
            str(request_header_dict.get(x, '')) for x in self.headers_to_sign]

        string_to_sign += '\n'.join(request_headers) + '\n'

        # get ocp- header to sign
        ocp_headers = []
        for name, value in request.headers.items():
            if 'ocp-' in name and value:
                ocp_headers.append((name.lower(), value))

        for name, value in sorted(ocp_headers):
            string_to_sign += "{}:{}\n".format(name, value)

        # get account_name and uri path to sign
        string_to_sign += "/{}{}".format(self._account_name, uri_path)

        # get query string to sign if it is not table service
        query_to_sign = parse_qs(url.query)

        for name in sorted(query_to_sign.keys()):
            value = query_to_sign[name][0]
            if value:
                string_to_sign += "\n{}:{}".format(name, value)

        # sign the request
        auth_string = "SharedKey {}:{}".format(
            self._account_name, self._sign_string(string_to_sign))

        request.headers[self._header] = auth_string

        return request

    def _sign_string(self, string_to_sign):

        _key = self._key.encode('utf-8')
        string_to_sign = string_to_sign.encode('utf-8')

        try:
            key = base64.b64decode(_key)
        except TypeError:
            raise ValueError("Invalid key value: {}".format(self._key))

        signed_hmac_sha256 = hmac.HMAC(key, string_to_sign, hashlib.sha256)
        digest = signed_hmac_sha256.digest()

        return base64.b64encode(digest).decode('utf-8')


class SharedKeyCredentials(Authentication):

    def __init__(self, account_name, key):
        super(SharedKeyCredentials, self).__init__()
        self.auth = SharedKeyAuth(self.header, account_name, key)
    
    def signed_session(self):

        session = super(SharedKeyCredentials, self).signed_session()
        session.auth = self.auth

        return session
    
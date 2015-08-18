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

import logging
import json


DEFAULT_LOG_NAME = 'azure.mgmt.common.filters'
DEFAULT_LOG_LEVEL = logging.DEBUG
DEFAULT_USER_AGENT = ''


class RequestFilter(object):
    '''
    Send the request.
    '''
    def __init__(self, session):
        if session is None:
            raise ValueError('session cannot be None.')

        self._session = session

    def send(self, prepared_request):
        return self._session.send(prepared_request)


class SigningFilter(object):
    '''
    Sign the request.
    '''

    def __init__(self, creds):
        if creds is None:
            raise ValueError('creds cannot be None.')

        self._creds = creds

    def send(self, prepared_request):
        self._creds.sign_request(prepared_request)
        return self.next.send(prepared_request)


class UserAgentFilter(object):
    '''
    Add a user-agent header to the request.
    '''

    def __init__(self, user_agent):
        if user_agent is None:
            raise ValueError('user_agent cannot be None.')

        self._user_agent = user_agent

    def send(self, prepared_request):
        prepared_request.headers['user-agent'] = self._user_agent
        return self.next.send(prepared_request)


class LogFilter(object):
    '''
    Log the request to a standard python logger.
    Example of enabling logging to the console:
        import logging
        logger = logging.getLogger('azure.mgmt.common.filters')
        logger.setLevel(logging.DEBUG)
        logger.addHandler(logging.StreamHandler())
    '''

    def __init__(self, name=DEFAULT_LOG_NAME, level=DEFAULT_LOG_LEVEL):
        if name is None:
            raise ValueError('name cannot be None.')

        if level is None:
            raise ValueError('level cannot be None.')

        self.level = level
        self.logger = logging.getLogger(name)

    def send(self, prepared_request):
        self._log_request(prepared_request)
        response = self.next.send(prepared_request)
        self._log_response(response)
        return response

    @staticmethod
    def _headers_to_string(headers):
        mask_headers = ['authorization']
        headers_raw = []
        for header, value in headers.items():
            if header.lower() in mask_headers:
                value = '*****'
            headers_raw.append('%s: %s' % (header, value))
        return '\n'.join(headers_raw)

    @staticmethod
    def _pretty_print(content):
        try:
            return json.dumps(
                json.loads(content),
                sort_keys=True,
                indent=4,
                separators=(',', ': '),
            )
        except Exception:
            pass
        return content

    def _log_request(self, request):
        if self.logger.isEnabledFor(self.level):
            headers = self._headers_to_string(request.headers)
            msg = ['Request: %s %s\n%s\n' % (request.method, request.url, headers)]
            if request.body:
                msg.append(self._pretty_print(request.body))
            self.logger.log(self.level, '\n'.join(msg))

    def _log_response(self, response):
        if self.logger.isEnabledFor(self.level):
            headers = self._headers_to_string(response.headers)
            msg = ['Response: %s %s\n%s\n' % (response.status_code, response.reason, headers)]
            if response.text:
                msg.append(self._pretty_print(response.text))
            self.logger.log(self.level, '\n'.join(msg))

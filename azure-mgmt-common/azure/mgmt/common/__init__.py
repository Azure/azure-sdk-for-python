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

import os
import requests
import logging
import json
import azure.mgmt.common.filters

__author__ = 'Microsoft Corp. <ptvshelp@microsoft.com>'
__version__ = '0.20.0'


class SubscriptionCloudCredentials(object):
    """
    Contains the credentials and subscription required to connect to a
    azure service 
    """
    def __init__(self, subscription_id, access_token, access_token_type = 'Bearer'):
        if access_token is None:
            raise ValueError('access_token cannot be None.')

        if subscription_id is None:
            raise ValueError('subscription_id cannot be None.')

        self._subscription_id = subscription_id
        self._access_token = access_token
        self._access_token_type = access_token_type

    @property
    def subscription_id(self):
        return self._subscription_id

    @property
    def access_token(self):
        return self._access_token

    @property
    def access_token_type(self):
        return self._access_token_type

    def sign_request(self, request):
        request.headers['Authorization'] = \
            (self.access_token_type + ' ' + self.access_token)


class AzureOperationResponse(object):
    """
    "A standard service response including an HTTP status code and request ID.
    """
    def __init__(self, **kwargs):
        self.request_id = None
        self.status_code = None


class OperationStatusResponse(AzureOperationResponse):
    """
    Represent the response from a long running operation.
    It contains the status of the specified operation, indicating 
    whether it has succeeded, is in progress, or has failed. If the
    operation failed, the error field includes the HTTP
    status code for the failed request, and also includes error
    information regarding the failure.
    """
    def __init__(self, *args, **kwargs):
        super(OperationStatusResponse, self).__init__(*args, **kwargs)
        self.id = None
        self.status = None
        self.http_status_code = None
        self.error = None

    class ErrorDetails:
        """
        If the asynchronous operation failed, the response body
        includes the HTTP status code for the failed request, and also
        includes error information regarding the failure.
        """
        def __init__(self):
            self.code = None
            self.message = None


class OperationStatus(object):
    '''
    The status of an azure long running request.
    The field naming doesn't conform to the python style, so to work with
    the common code-generator, which has defined the same type in C# style
    '''
    InProgress='InProgress'
    Succeeded='Succeeded'
    Failed='Failed'

    '''resourcemanagement.py still uses these'''
    in_progress='InProgress'
    succeeded='Succeeded'
    failed='Failed'


class Service(object):
    """
    Basic service
    """
    def __init__(self, credentials, **kwargs):
        if credentials is None:
            raise ValueError('credentials cannot be None.')

        self._credentials = credentials
        self._user_agent = kwargs.get('user_agent', azure.mgmt.common.filters.DEFAULT_USER_AGENT)
        self._log_name = kwargs.get('log_name', azure.mgmt.common.filters.DEFAULT_LOG_NAME)
        self._log_level = kwargs.get('log_level', azure.mgmt.common.filters.DEFAULT_LOG_LEVEL)
        self._session = kwargs.get('session', requests.Session())
        self._base_uri = kwargs.get('base_uri')
        self._first_filter = None

        self.add_filter(azure.mgmt.common.filters.RequestFilter(self._session))
        self.add_filter(azure.mgmt.common.filters.LogFilter(self._log_name, self._log_level))
        self.add_filter(azure.mgmt.common.filters.SigningFilter(self._credentials))

        if self._user_agent:
            self.add_filter(azure.mgmt.common.filters.UserAgentFilter(self._user_agent))

        filters = kwargs.get('filters')
        if filters:
            for filter in filters:
                self.add_filter(filter)

        #Wire up tracing tools like fiddler
        #The 2 env variables below are what the 'requests' documents to support
        #(http://docs.python-requests.org/en/latest/user/advanced/)
        #However, tests reveal it doesn't populate them to the 'proxies",  
        #so we do it ourselves.
        proxies = {}
        if os.getenv('HTTP_PROXY') is not None:
            proxies['http'] = os.getenv('HTTP_PROXY')
        if os.getenv('HTTPS_PROXY') is not None:
            proxies['https'] = os.getenv('HTTPS_PROXY') 

        if proxies:
            self._session.proxies = proxies
            self._session.verify = False

    @property
    def base_uri(self):
        """
         Gets the URI used as the base for all cloud service requests.
        """
        return self._base_uri

    @property
    def credentials(self):
        """
         Gets subscription credentials which uniquely identify Microsoft Azure
         subscription. The subscription ID forms part of the URI for every
         service call.
        """
        return self._credentials

    def add_filter(self, filter):
        next_filter = self._first_filter
        self._first_filter = filter
        self._first_filter.next = next_filter

    def send_request(self, http_request):
        prepared_request = self._session.prepare_request(http_request)
        response = self._first_filter.send(prepared_request)
        return response

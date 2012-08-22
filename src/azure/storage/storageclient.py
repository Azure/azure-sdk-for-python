#-------------------------------------------------------------------------
# Copyright 2011 Microsoft Corporation
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
import base64
import urllib2
import hmac
import hashlib 
import os


from azure.storage import _storage_error_handler, X_MS_VERSION
from azure.http.httpclient import _HTTPClient
from azure.http import HTTPError
from azure import (_parse_response, WindowsAzureError,
                          DEV_ACCOUNT_NAME, DEV_ACCOUNT_KEY)
import azure

#--------------------------------------------------------------------------
# constants for azure app setting environment variables
AZURE_STORAGE_ACCOUNT = 'AZURE_STORAGE_ACCOUNT'
AZURE_STORAGE_ACCESS_KEY = 'AZURE_STORAGE_ACCESS_KEY'
EMULATED = 'EMULATED'

#--------------------------------------------------------------------------
class _StorageClient(object):
    '''
    This is the base class for BlobManager, TableManager and QueueManager.
    '''

    def __init__(self, account_name=None, account_key=None, protocol='http'):
        if account_name is not None:
            self.account_name = account_name.encode('ascii', 'ignore')
        else:
            self.account_name = None
        if account_key is not None:
            self.account_key = account_key.encode('ascii', 'ignore')
        else:
            self.account_key = None

        self.requestid = None
        self.protocol = protocol
        
        #the app is not run in azure emulator or use default development 
        #storage account and key if app is run in emulator. 
        self.use_local_storage = False

        #check whether it is run in emulator. 
        if os.environ.has_key(EMULATED):
            if os.environ[EMULATED].lower() == 'false':
                self.is_emulated = False
            else:
                self.is_emulated = True
        else:
            self.is_emulated = False

        #get account_name and account key. If they are not set when constructing, 
        #get the account and key from environment variables if the app is not run
        #in azure emulator or use default development storage account and key if 
        #app is run in emulator. 
        if not self.account_name or not self.account_key:
            if self.is_emulated:
                self.account_name = DEV_ACCOUNT_NAME
                self.account_key = DEV_ACCOUNT_KEY
                self.use_local_storage = True
            else:
                if os.environ.has_key(AZURE_STORAGE_ACCOUNT):
                    self.account_name = os.environ[AZURE_STORAGE_ACCOUNT]
                if os.environ.has_key(AZURE_STORAGE_ACCESS_KEY):
                    self.account_key = os.environ[AZURE_STORAGE_ACCESS_KEY]

        if not self.account_name or not self.account_key:
            raise WindowsAzureError(azure._ERROR_STORAGE_MISSING_INFO)
        
        self.x_ms_version = X_MS_VERSION
        self._httpclient = _HTTPClient(service_instance=self, account_key=self.account_key, account_name=self.account_name, x_ms_version=self.x_ms_version, protocol=protocol)
        self._batchclient = None
        self._filter = self._perform_request_worker
    
    def with_filter(self, filter):
        '''Returns a new service which will process requests with the
        specified filter.  Filtering operations can include logging, automatic
        retrying, etc...  The filter is a lambda which receives the HTTPRequest
        and another lambda.  The filter can perform any pre-processing on the
        request, pass it off to the next lambda, and then perform any post-processing
        on the response.'''
        res = type(self)(self.account_name, self.account_key, self.protocol)
        old_filter = self._filter
        def new_filter(request):
            return filter(request, old_filter)
                    
        res._filter = new_filter
        return res

    def _perform_request_worker(self, request):
        return self._httpclient.perform_request(request)

    def _perform_request(self, request):
        ''' Sends the request and return response. Catches HTTPError and hand it to error handler'''

        try:
            if self._batchclient is not None:
                return self._batchclient.insert_request_to_batch(request)
            else:
                resp = self._filter(request)
        except HTTPError as e:
            _storage_error_handler(e)

        return resp
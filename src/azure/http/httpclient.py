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
import os
import types
import base64
import datetime
import time
import hashlib
import hmac
import urllib2
import httplib
import ast
import sys
from xml.dom import minidom

from azure.http import HTTPError, HTTPResponse

class _HTTPClient:
    ''' 
    Takes the request and sends it to cloud service and returns the response.
    '''

    def __init__(self, service_instance, cert_file=None, account_name=None, account_key=None, service_namespace=None, issuer=None, x_ms_version=None, protocol='https'):
        '''
        service_instance: service client instance. 
        cert_file: certificate file name/location. This is only used in hosted service management.
        account_name: the storage account.
        account_key: the storage account access key for storage services or servicebus access key for service bus service.
        service_namespace: the service namespace for service bus.
        issuer: the issuer for service bus service.
        x_ms_version: the x_ms_version for the service.
        '''
        self.service_instance = service_instance
        self.status = None
        self.respheader = None
        self.message = None
        self.cert_file = cert_file
        self.account_name = account_name
        self.account_key = account_key    
        self.service_namespace = service_namespace    
        self.issuer = issuer
        self.x_ms_version = x_ms_version
        self.protocol = protocol

    def get_connection(self, request):
        ''' Create connection for the request. '''
        
        # If on Windows then use winhttp HTTPConnection instead of httplib HTTPConnection due to the 
        # bugs in httplib HTTPSConnection. We've reported the issue to the Python 
        # dev team and it's already fixed for 2.7.4 but we'll need to keep this workaround meanwhile.
        if sys.platform.lower().startswith('win'):
            import azure.http.winhttp
            _connection = azure.http.winhttp._HTTPConnection(request.host, cert_file=self.cert_file, protocol=self.protocol)
        elif self.protocol == 'http':
            _connection = httplib.HTTPConnection(request.host)
        else:
            _connection = httplib.HTTPSConnection(request.host, cert_file=self.cert_file)
        return _connection

    def send_request_headers(self, connection, request_headers):
        for name, value in request_headers:
            if value:
                connection.putheader(name, value)
        connection.endheaders()

    def send_request_body(self, connection, request_body):
        if request_body:
            connection.send(request_body)
        elif (not isinstance(connection, httplib.HTTPSConnection) and 
              not isinstance(connection, httplib.HTTPConnection)):
            connection.send(None)
     
    def perform_request(self, request):
        ''' Sends request to cloud service server and return the response. '''

        connection = self.get_connection(request)
        connection.putrequest(request.method, request.path)
        self.send_request_headers(connection, request.headers)
        self.send_request_body(connection, request.body)

        resp = connection.getresponse()
        self.status = int(resp.status)
        self.message = resp.reason
        self.respheader = headers = resp.getheaders()
        respbody = None
        if resp.length is None:
            respbody = resp.read()
        elif resp.length > 0:
            respbody = resp.read(resp.length)
    
        response = HTTPResponse(int(resp.status), resp.reason, headers, respbody)
        if self.status >= 300:
            raise HTTPError(self.status, self.message, self.respheader, respbody)
        
        return response

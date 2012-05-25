#------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. 
#
# This source code is subject to terms and conditions of the Apache License, 
# Version 2.0. A copy of the license can be found in the License.html file at 
# the root of this distribution. If you cannot locate the Apache License, 
# Version 2.0, please send an email to vspython@microsoft.com. By using this 
# source code in any fashion, you are agreeing to be bound by the terms of the 
# Apache License, Version 2.0.
#
# You must not remove this notice, or any other, from this software.
#------------------------------------------------------------------------------
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

from windowsazure import HTTPError

class _HTTPClient:
    def __init__(self, service_instance, cert_file=None, account_name=None, account_key=None, service_namespace=None, issuer=None, x_ms_version=None, protocol='https'):
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
        if sys.platform.lower().startswith('win'):
            import windowsazure.http.winhttp
            _connection = windowsazure.http.winhttp._HTTPConnection(request.host, cert_file=self.cert_file, protocol=self.protocol)
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
        """Send requst to server"""
        connection = self.get_connection(request)
        connection.putrequest(request.method, request.uri)
        self.send_request_headers(connection, request.header)
        self.send_request_body(connection, request.body)

        resp = connection.getresponse()
        self.status = int(resp.status)
        self.message = resp.reason
        self.respheader = resp.getheaders()
        respbody = None
        if resp.length is None:
            respbody = resp.read()
        elif resp.length > 0:
            respbody = resp.read(resp.length)
    
        print(self.status)
        #print(self.message)
        #print(respbody)
        if self.status >= 300:
            raise HTTPError(self.status, self.message, self.respheader, respbody)
        
        return respbody

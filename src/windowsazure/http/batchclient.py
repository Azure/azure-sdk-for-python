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
import urllib2
from windowsazure.http.httpclient import _HTTPClient
from windowsazure import _Request, _update_request_uri_query, WindowsAzureError, HTTPError
from windowsazure.storage import _update_storage_table_header

class _BatchClient(_HTTPClient):

    def __init__(self, service_instance, account_key, account_name, x_ms_version=None, protocol='http'):
        _HTTPClient.__init__(self, service_instance, account_name=account_name, account_key=account_key, x_ms_version=x_ms_version, protocol=protocol)
        self.is_batch = False
        self.batch_requests = []
        self.batch_table = ''
        self.batch_partition_key = ''
        self.batch_row_keys = []

    def get_request_table(self, request):
        if '(' in request.uri:
            pos = request.uri.find('(')
            return request.uri[1:pos]
        else:
            return request.uri[1:]  

    def get_request_partition_key(self, request):
        if request.method == 'POST':
            pos1 = request.body.find('<d:PartitionKey>')
            pos2 = request.body.find('</d:PartitionKey>')
            if pos1 == -1 or pos2 == -1:
                raise WindowsAzureError('Cannot find partition key in request.')
            return request.body[pos1 + len('<d:PartitionKey>'):pos2]
        else:
            uri = urllib2.unquote(request.uri)
            pos1 = uri.find('PartitionKey=\'')
            pos2 = uri.find('\',', pos1)
            if pos1 == -1 or pos2 == -1:
                raise WindowsAzureError('Cannot find partition key in request.')
            return uri[pos1 + len('PartitionKey=\''):pos2]

    def get_request_row_key(self, request):
        if request.method == 'POST':
            pos1 = request.body.find('<d:RowKey>')
            pos2 = request.body.find('</d:RowKey>')
            if pos1 == -1 or pos2 == -1:
                raise WindowsAzureError('Cannot find row key in request.')
            return request.body[pos1 + len('<d:RowKey>'):pos2]
        else:
            uri = urllib2.unquote(request.uri)
            pos1 = uri.find('RowKey=\'')
            pos2 = uri.find('\')', pos1)
            if pos1 == -1 or pos2 == -1:
                raise WindowsAzureError('Cannot find row key in request.')
            row_key = uri[pos1 + len('RowKey=\''):pos2]
            return row_key

    def validate_request_table(self, request):
        if self.batch_table:
            if self.get_request_table(request) != self.batch_table:
                raise WindowsAzureError('Table should be the same in a batch operations')
        else:
            self.batch_table = self.get_request_table(request)

    def validate_request_partition_key(self, request):
        if self.batch_partition_key:
            if self.get_request_partition_key(request) != self.batch_partition_key:
                raise WindowsAzureError('Partition Key should be the same in a batch operations')
        else:
            self.batch_partition_key = self.get_request_partition_key(request)

    def validate_request_row_key(self, request):
        if self.batch_row_keys:
            if self.get_request_row_key(request) in self.batch_row_keys:
                raise WindowsAzureError('Row Key should not be the same in a batch operations')
        else:
            self.batch_row_keys.append(self.get_request_row_key(request))

    def begin_batch(self):
        self.is_batch = True
        self.batch_table = ''
        self.batch_partition_key = ''
        self.batch_row_keys = []
        self.batch_requests = []

    def insert_request_to_batch(self, request):
        self.validate_request_table(request)
        self.validate_request_partition_key(request)
        self.validate_request_row_key(request)
        self.batch_requests.append(request)

    def commit_batch(self):
        if self.is_batch:
            self.is_batch = False
            resp = self.commit_batch_requests()            
        return resp

    def commit_batch_requests(self):
        batch_boundary = 'batch_a2e9d677-b28b-435e-a89e-87e6a768a431'
        changeset_boundary = 'changeset_8128b620-b4bb-458c-a177-0959fb14c977'
        if self.batch_requests:
            request = _Request()
            request.method = 'POST'
            request.host = self.batch_requests[0].host
            request.uri = '/$batch'
            request.header = [('Content-Type', 'multipart/mixed; boundary=' + batch_boundary),
                              ('Accept', 'application/atom+xml,application/xml'),
                              ('Accept-Charset', 'UTF-8')]
            
            request.body = '--' + batch_boundary + '\n'
            request.body += 'Content-Type: multipart/mixed; boundary=' + changeset_boundary + '\n\n'

            content_id = 1
            for batch_request in self.batch_requests:
                request.body += '--' + changeset_boundary + '\n'
                request.body += 'Content-Type: application/http\n'
                request.body += 'Content-Transfer-Encoding: binary\n\n'

                request.body += batch_request.method + ' http://' + batch_request.host + batch_request.uri + ' HTTP/1.1\n'
                request.body += 'Content-ID: ' + str(content_id) + '\n'
                content_id += 1
                
                if not batch_request.method == 'DELETE':
                    request.body += 'Content-Type: application/atom+xml;type=entry\n'
                    request.body += 'Content-Length: ' + str(len(batch_request.body)) + '\n\n'
                    request.body += batch_request.body + '\n'
                else:
                    find_if_match = False
                    for name, value in batch_request.header:
                        if name == 'If-Match':
                            request.body += name + ': ' + value + '\n\n'
                            find_if_match = True
                            break
                    if not find_if_match:
                        request.body += 'If-Match: *\n\n'

            request.body += '--' + changeset_boundary + '--' + '\n'
            request.body += '--' + batch_boundary + '--' 

            request.uri, request.query = _update_request_uri_query(request)
            request.header = _update_storage_table_header(request, self.account_name, self.account_key)


            resp = self.perform_request(request)
            pos1 = resp.find('HTTP/1.1 ') + len('HTTP/1.1 ')
            pos2 = resp.find(' ', pos1)
            status = resp[pos1:pos2]
            if int(status) >= 300:
                raise HTTPError(status, 'Batch Commit Fail', self.respheader, resp)
            return resp

    def cancel_batch(self):
        self.is_batch = False
        
    
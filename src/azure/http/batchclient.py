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
import urllib2
import azure
from azure.http.httpclient import _HTTPClient
from azure.http import HTTPError, HTTPRequest
from azure import _update_request_uri_query, WindowsAzureError
from azure.storage import _update_storage_table_header

class _BatchClient(_HTTPClient):
    '''
    This is the class that is used for batch operation for storage table service. 
    It only supports one changeset.
    '''

    def __init__(self, service_instance, account_key, account_name, x_ms_version=None, protocol='http'):
        _HTTPClient.__init__(self, service_instance, account_name=account_name, account_key=account_key, x_ms_version=x_ms_version, protocol=protocol)
        self.is_batch = False
        self.batch_requests = []
        self.batch_table = ''
        self.batch_partition_key = ''
        self.batch_row_keys = []

    def get_request_table(self, request):
        '''
        Extracts table name from request.uri. The request.uri has either "/mytable(...)" 
        or "/mytable" format.

        request: the request to insert, update or delete entity
        '''
        if '(' in request.uri:
            pos = request.uri.find('(')
            return request.uri[1:pos]
        else:
            return request.uri[1:]  

    def get_request_partition_key(self, request):
        '''
        Extracts PartitionKey from request.body if it is a POST request or from request.uri if 
        it is not a POST request. Only insert operation request is a POST request and the 
        PartitionKey is in the request body.

        request: the request to insert, update or delete entity
        '''
        if request.method == 'POST':
            pos1 = request.body.find('<d:PartitionKey>')
            pos2 = request.body.find('</d:PartitionKey>')
            if pos1 == -1 or pos2 == -1:
                raise WindowsAzureError(azure._ERROR_CANNOT_FIND_PARTITION_KEY)
            return request.body[pos1 + len('<d:PartitionKey>'):pos2]
        else:
            uri = urllib2.unquote(request.uri)
            pos1 = uri.find('PartitionKey=\'')
            pos2 = uri.find('\',', pos1)
            if pos1 == -1 or pos2 == -1:
                raise WindowsAzureError(azure._ERROR_CANNOT_FIND_PARTITION_KEY)
            return uri[pos1 + len('PartitionKey=\''):pos2]

    def get_request_row_key(self, request):
        '''
        Extracts RowKey from request.body if it is a POST request or from request.uri if 
        it is not a POST request. Only insert operation request is a POST request and the 
        Rowkey is in the request body.

        request: the request to insert, update or delete entity
        '''
        if request.method == 'POST':
            pos1 = request.body.find('<d:RowKey>')
            pos2 = request.body.find('</d:RowKey>')
            if pos1 == -1 or pos2 == -1:
                raise WindowsAzureError(azure._ERROR_CANNOT_FIND_ROW_KEY)
            return request.body[pos1 + len('<d:RowKey>'):pos2]
        else:
            uri = urllib2.unquote(request.uri)
            pos1 = uri.find('RowKey=\'')
            pos2 = uri.find('\')', pos1)
            if pos1 == -1 or pos2 == -1:
                raise WindowsAzureError(azure._ERROR_CANNOT_FIND_ROW_KEY)
            row_key = uri[pos1 + len('RowKey=\''):pos2]
            return row_key

    def validate_request_table(self, request):
        '''
        Validates that all requests have the same table name. Set the table name if it is 
        the first request for the batch operation.

        request: the request to insert, update or delete entity
        '''
        if self.batch_table:
            if self.get_request_table(request) != self.batch_table:
                raise WindowsAzureError(azure._ERROR_INCORRECT_TABLE_IN_BATCH)
        else:
            self.batch_table = self.get_request_table(request)

    def validate_request_partition_key(self, request):
        '''
        Validates that all requests have the same PartitiionKey. Set the PartitionKey if it is 
        the first request for the batch operation.

        request: the request to insert, update or delete entity
        '''
        if self.batch_partition_key:
            if self.get_request_partition_key(request) != self.batch_partition_key:
                raise WindowsAzureError(azure._ERROR_INCORRECT_PARTITION_KEY_IN_BATCH)
        else:
            self.batch_partition_key = self.get_request_partition_key(request)

    def validate_request_row_key(self, request):
        '''
        Validates that all requests have the different RowKey and adds RowKey to existing RowKey list.

        request: the request to insert, update or delete entity
        '''       
        if self.batch_row_keys:
            if self.get_request_row_key(request) in self.batch_row_keys:
                raise WindowsAzureError(azure._ERROR_DUPLICATE_ROW_KEY_IN_BATCH)
        else:
            self.batch_row_keys.append(self.get_request_row_key(request))

    def begin_batch(self):
        '''
        Starts the batch operation. Intializes the batch variables
        
        is_batch: batch operation flag.
        batch_table: the table name of the batch operation
        batch_partition_key: the PartitionKey of the batch requests.
        batch_row_keys: the RowKey list of adding requests.
        batch_requests: the list of the requests.
        '''
        self.is_batch = True
        self.batch_table = ''
        self.batch_partition_key = ''
        self.batch_row_keys = []
        self.batch_requests = []

    def insert_request_to_batch(self, request):
        ''' 
        Adds request to batch operation.
                
        request: the request to insert, update or delete entity
        '''  
        self.validate_request_table(request)
        self.validate_request_partition_key(request)
        self.validate_request_row_key(request)
        self.batch_requests.append(request)

    def commit_batch(self):
        ''' Resets batch flag and commits the batch requests. '''  
        if self.is_batch:
            self.is_batch = False
            resp = self.commit_batch_requests()            
        return resp

    def commit_batch_requests(self):
        ''' Commits the batch requests. '''

        batch_boundary = 'batch_a2e9d677-b28b-435e-a89e-87e6a768a431'
        changeset_boundary = 'changeset_8128b620-b4bb-458c-a177-0959fb14c977'
        
        #Commits batch only the requests list is not empty.
        if self.batch_requests:
            request = HTTPRequest()
            request.method = 'POST'
            request.host = self.batch_requests[0].host
            request.uri = '/$batch'
            request.headers = [('Content-Type', 'multipart/mixed; boundary=' + batch_boundary),
                              ('Accept', 'application/atom+xml,application/xml'),
                              ('Accept-Charset', 'UTF-8')]
            
            request.body = '--' + batch_boundary + '\n'
            request.body += 'Content-Type: multipart/mixed; boundary=' + changeset_boundary + '\n\n'

            content_id = 1

            # Adds each request body to the POST data.
            for batch_request in self.batch_requests:
                request.body += '--' + changeset_boundary + '\n'
                request.body += 'Content-Type: application/http\n'
                request.body += 'Content-Transfer-Encoding: binary\n\n'

                request.body += batch_request.method + ' http://' + batch_request.host + batch_request.uri + ' HTTP/1.1\n'
                request.body += 'Content-ID: ' + str(content_id) + '\n'
                content_id += 1
                
                # Add different headers for different type requests.
                if not batch_request.method == 'DELETE':
                    request.body += 'Content-Type: application/atom+xml;type=entry\n'
                    request.body += 'Content-Length: ' + str(len(batch_request.body)) + '\n\n'
                    request.body += batch_request.body + '\n'
                else:
                    find_if_match = False
                    for name, value in batch_request.headers:
                        #If-Match should be already included in batch_request.headers, but in case it is missing, just add it.
                        if name == 'If-Match':
                            request.body += name + ': ' + value + '\n\n'
                            break
                    else:
                        request.body += 'If-Match: *\n\n'

            request.body += '--' + changeset_boundary + '--' + '\n'
            request.body += '--' + batch_boundary + '--' 

            request.uri, request.query = _update_request_uri_query(request)
            request.headers = _update_storage_table_header(request, self.account_name, self.account_key)

            #Submit the whole request as batch request.
            response = self.perform_request(request)
            resp = response.body

            #Extracts the status code from the response body.  If any operation fails, the status code will appear right after the first HTTP/1.1.
            pos1 = resp.find('HTTP/1.1 ') + len('HTTP/1.1 ')
            pos2 = resp.find(' ', pos1)
            status = resp[pos1:pos2]

            if int(status) >= 300:
                raise HTTPError(status, azure._ERROR_BATCH_COMMIT_FAIL, self.respheader, resp)
            return resp

    def cancel_batch(self):
        ''' Resets the batch flag. '''
        self.is_batch = False
        
    
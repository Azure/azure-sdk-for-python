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
import os
import urllib2

from azure.storage import *
from azure.storage.storageclient import _StorageClient
from azure.storage import (_update_storage_queue_header)
from azure.http import HTTPRequest, HTTP_RESPONSE_NO_CONTENT
from azure import (_validate_not_none, Feed,
                                _convert_response_to_feeds, _str_or_none, _int_or_none,
                                _get_request_body, _update_request_uri_query, 
                                _dont_fail_on_exist, _dont_fail_not_exist, WindowsAzureConflictError, 
                                WindowsAzureError, _parse_response, _convert_class_to_xml, 
                                _parse_response_for_dict, _parse_response_for_dict_prefix, 
                                _parse_response_for_dict_filter,  
                                _parse_enum_results_list, _update_request_uri_query_local_storage, 
                                _get_table_host, _get_queue_host, _get_blob_host, 
                                _parse_simple_list, SERVICE_BUS_HOST_BASE, xml_escape)  

class QueueService(_StorageClient):
    '''
    This is the main class managing queue resources.
    account_name: your storage account name, required for all operations.
    account_key: your storage account key, required for all operations.
    '''

    def get_queue_service_properties(self, timeout=None):
        '''
        Gets the properties of a storage account's Queue Service, including Windows Azure 
        Storage Analytics.
        
        timeout: Optional. The timeout parameter is expressed in seconds. For example, the 
        following value sets a timeout of 30 seconds for the request: timeout=30
        '''
        request = HTTPRequest()
        request.method = 'GET'
        request.host = _get_queue_host(self.account_name, self.use_local_storage)
        request.path = '/?restype=service&comp=properties'
        request.query = [('timeout', _int_or_none(timeout))]
        request.path, request.query = _update_request_uri_query_local_storage(request, self.use_local_storage)
        request.headers = _update_storage_queue_header(request, self.account_name, self.account_key)
        response = self._perform_request(request)

        return _parse_response(response, StorageServiceProperties)

    def list_queues(self, prefix=None, marker=None, maxresults=None, include=None):
        '''
        Lists all of the queues in a given storage account.
        '''
        request = HTTPRequest()
        request.method = 'GET'
        request.host = _get_queue_host(self.account_name, self.use_local_storage)
        request.path = '/?comp=list'
        request.query = [
            ('prefix', _str_or_none(prefix)),
            ('marker', _str_or_none(marker)),
            ('maxresults', _int_or_none(maxresults)),
            ('include', _str_or_none(include))
            ]
        request.path, request.query = _update_request_uri_query_local_storage(request, self.use_local_storage)
        request.headers = _update_storage_queue_header(request, self.account_name, self.account_key)
        response = self._perform_request(request)

        return _parse_enum_results_list(response, QueueEnumResults, "Queues", Queue)

    def create_queue(self, queue_name, x_ms_meta_name_values=None, fail_on_exist=False):
        '''
        Creates a queue under the given account.
        
        queue_name: name of the queue.
        x_ms_meta_name_values: Optional. A dict containing name-value pairs to associate 
        		with the queue as metadata.
        fail_on_exist: specify whether throw exception when queue exists.
        '''
        _validate_not_none('queue_name', queue_name)
        request = HTTPRequest()
        request.method = 'PUT'
        request.host = _get_queue_host(self.account_name, self.use_local_storage)
        request.path = '/' + str(queue_name) + ''
        request.headers = [('x-ms-meta-name-values', x_ms_meta_name_values)]
        request.path, request.query = _update_request_uri_query_local_storage(request, self.use_local_storage)
        request.headers = _update_storage_queue_header(request, self.account_name, self.account_key)
        if not fail_on_exist:
            try:
                response = self._perform_request(request)
                if response.status == HTTP_RESPONSE_NO_CONTENT:
                    return False
                return True
            except WindowsAzureError as e:
                _dont_fail_on_exist(e)
                return False
        else:
            response = self._perform_request(request)
            if response.status == HTTP_RESPONSE_NO_CONTENT:
                raise WindowsAzureConflictError(azure._ERROR_CONFLICT)
            return True

    def delete_queue(self, queue_name, fail_not_exist=False):
        '''
        Permanently deletes the specified queue.
        
        queue_name: name of the queue.
        fail_not_exist: specify whether throw exception when queue doesn't exist.
        '''
        _validate_not_none('queue_name', queue_name)
        request = HTTPRequest()
        request.method = 'DELETE'
        request.host = _get_queue_host(self.account_name, self.use_local_storage)
        request.path = '/' + str(queue_name) + ''
        request.path, request.query = _update_request_uri_query_local_storage(request, self.use_local_storage)
        request.headers = _update_storage_queue_header(request, self.account_name, self.account_key)
        if not fail_not_exist:
            try:
                self._perform_request(request)
                return True
            except WindowsAzureError as e:
                _dont_fail_not_exist(e)
                return False
        else:
            self._perform_request(request)
            return True

    def get_queue_metadata(self, queue_name):
        '''
        Retrieves user-defined metadata and queue properties on the specified queue. 
        Metadata is associated with the queue as name-values pairs.
        
        queue_name: name of the queue.
        '''
        _validate_not_none('queue_name', queue_name)
        request = HTTPRequest()
        request.method = 'GET'
        request.host = _get_queue_host(self.account_name, self.use_local_storage)
        request.path = '/' + str(queue_name) + '?comp=metadata'
        request.path, request.query = _update_request_uri_query_local_storage(request, self.use_local_storage)
        request.headers = _update_storage_queue_header(request, self.account_name, self.account_key)
        response = self._perform_request(request)

        return _parse_response_for_dict_prefix(response, prefix='x-ms-meta')

    def set_queue_metadata(self, queue_name, x_ms_meta_name_values=None):
        '''
        Sets user-defined metadata on the specified queue. Metadata is associated 
        with the queue as name-value pairs.
        
        queue_name: name of the queue.
        x_ms_meta_name_values: Optional. A dict containing name-value pairs to associate 
        		with the queue as metadata.
        '''
        _validate_not_none('queue_name', queue_name)
        request = HTTPRequest()
        request.method = 'PUT'
        request.host = _get_queue_host(self.account_name, self.use_local_storage)
        request.path = '/' + str(queue_name) + '?comp=metadata'
        request.headers = [('x-ms-meta-name-values', x_ms_meta_name_values)]
        request.path, request.query = _update_request_uri_query_local_storage(request, self.use_local_storage)
        request.headers = _update_storage_queue_header(request, self.account_name, self.account_key)
        response = self._perform_request(request)

    def put_message(self, queue_name, message_text, visibilitytimeout=None, messagettl=None):
        '''
        Adds a new message to the back of the message queue. A visibility timeout can 
        also be specified to make the message invisible until the visibility timeout 
        expires. A message must be in a format that can be included in an XML request 
        with UTF-8 encoding. The encoded message can be up to 64KB in size for versions 
        2011-08-18 and newer, or 8KB in size for previous versions.
        
        queue_name: name of the queue.
        visibilitytimeout: Optional. If specified, the request must be made using an 
        		x-ms-version of 2011-08-18 or newer.
        messagettl: Optional. Specifies the time-to-live interval for the message, 
        		in seconds. The maximum time-to-live allowed is 7 days. If this parameter
        		is omitted, the default time-to-live is 7 days.
        '''
        _validate_not_none('queue_name', queue_name)
        _validate_not_none('message_text', message_text)
        request = HTTPRequest()
        request.method = 'POST'
        request.host = _get_queue_host(self.account_name, self.use_local_storage)
        request.path = '/' + str(queue_name) + '/messages'
        request.query = [
            ('visibilitytimeout', _str_or_none(visibilitytimeout)),
            ('messagettl', _str_or_none(messagettl))
            ]
        request.body = _get_request_body('<?xml version="1.0" encoding="utf-8"?> \
<QueueMessage> \
    <MessageText>' + xml_escape(str(message_text)) + '</MessageText> \
</QueueMessage>')
        request.path, request.query = _update_request_uri_query_local_storage(request, self.use_local_storage)
        request.headers = _update_storage_queue_header(request, self.account_name, self.account_key)
        response = self._perform_request(request)

    def get_messages(self, queue_name, numofmessages=None, visibilitytimeout=None):
        '''
        Retrieves one or more messages from the front of the queue.
        
        queue_name: name of the queue.
        numofmessages: Optional. A nonzero integer value that specifies the number of 
        		messages to retrieve from the queue, up to a maximum of 32. If fewer are
        		visible, the visible messages are returned. By default, a single message
        		is retrieved from the queue with this operation.
        visibilitytimeout: Required. Specifies the new visibility timeout value, in 
        		seconds, relative to server time. The new value must be larger than or 
        		equal to 1 second, and cannot be larger than 7 days, or larger than 2 
        		hours on REST protocol versions prior to version 2011-08-18. The visibility
        		timeout of a message can be set to a value later than the expiry time.
        '''
        _validate_not_none('queue_name', queue_name)
        request = HTTPRequest()
        request.method = 'GET'
        request.host = _get_queue_host(self.account_name, self.use_local_storage)
        request.path = '/' + str(queue_name) + '/messages'
        request.query = [
            ('numofmessages', _str_or_none(numofmessages)),
            ('visibilitytimeout', _str_or_none(visibilitytimeout))
            ]
        request.path, request.query = _update_request_uri_query_local_storage(request, self.use_local_storage)
        request.headers = _update_storage_queue_header(request, self.account_name, self.account_key)
        response = self._perform_request(request)

        return _parse_response(response, QueueMessagesList)

    def peek_messages(self, queue_name, numofmessages=None):
        '''
        Retrieves one or more messages from the front of the queue, but does not alter 
        the visibility of the message. 
        
        queue_name: name of the queue.
        numofmessages: Optional. A nonzero integer value that specifies the number of 
        		messages to peek from the queue, up to a maximum of 32. By default, 
        		a single message is peeked from the queue with this operation.
        '''
        _validate_not_none('queue_name', queue_name)
        request = HTTPRequest()
        request.method = 'GET'
        request.host = _get_queue_host(self.account_name, self.use_local_storage)
        request.path = '/' + str(queue_name) + '/messages?peekonly=true'
        request.query = [('numofmessages', _str_or_none(numofmessages))]
        request.path, request.query = _update_request_uri_query_local_storage(request, self.use_local_storage)
        request.headers = _update_storage_queue_header(request, self.account_name, self.account_key)
        response = self._perform_request(request)

        return _parse_response(response, QueueMessagesList)

    def delete_message(self, queue_name, message_id, popreceipt):
        '''
        Deletes the specified message.
        
        queue_name: name of the queue.
        popreceipt: Required. A valid pop receipt value returned from an earlier call 
        		to the Get Messages or Update Message operation.
        '''
        _validate_not_none('queue_name', queue_name)
        _validate_not_none('message_id', message_id)
        _validate_not_none('popreceipt', popreceipt)
        request = HTTPRequest()
        request.method = 'DELETE'
        request.host = _get_queue_host(self.account_name, self.use_local_storage)
        request.path = '/' + str(queue_name) + '/messages/' + str(message_id) + ''
        request.query = [('popreceipt', _str_or_none(popreceipt))]
        request.path, request.query = _update_request_uri_query_local_storage(request, self.use_local_storage)
        request.headers = _update_storage_queue_header(request, self.account_name, self.account_key)
        response = self._perform_request(request)

    def clear_messages(self, queue_name):
        '''
        Deletes all messages from the specified queue.
        
        queue_name: name of the queue.
        '''
        _validate_not_none('queue_name', queue_name)
        request = HTTPRequest()
        request.method = 'DELETE'
        request.host = _get_queue_host(self.account_name, self.use_local_storage)
        request.path = '/' + str(queue_name) + '/messages'
        request.path, request.query = _update_request_uri_query_local_storage(request, self.use_local_storage)
        request.headers = _update_storage_queue_header(request, self.account_name, self.account_key)
        response = self._perform_request(request)

    def update_message(self, queue_name, message_id, message_text, popreceipt, visibilitytimeout):
        '''
        Updates the visibility timeout of a message. You can also use this 
        operation to update the contents of a message. 
        
        queue_name: name of the queue.
        popreceipt: Required. A valid pop receipt value returned from an earlier call 
        		to the Get Messages or Update Message operation. 
        visibilitytimeout: Required. Specifies the new visibility timeout value, in 
        		seconds, relative to server time. The new value must be larger than or 
        		equal to 0, and cannot be larger than 7 days. The visibility timeout 
        		of a message cannot be set to a value later than the expiry time. A 
        		message can be updated until it has been deleted or has expired.
        '''
        _validate_not_none('queue_name', queue_name)
        _validate_not_none('message_id', message_id)
        _validate_not_none('message_text', message_text)
        _validate_not_none('popreceipt', popreceipt)
        _validate_not_none('visibilitytimeout', visibilitytimeout)
        request = HTTPRequest()
        request.method = 'PUT'
        request.host = _get_queue_host(self.account_name, self.use_local_storage)
        request.path = '/' + str(queue_name) + '/messages/' + str(message_id) + ''
        request.query = [
            ('popreceipt', _str_or_none(popreceipt)),
            ('visibilitytimeout', _str_or_none(visibilitytimeout))
            ]
        request.body = _get_request_body('<?xml version="1.0" encoding="utf-8"?> \
<QueueMessage> \
    <MessageText>' + xml_escape(str(message_text)) + '</MessageText> \
</QueueMessage>')
        request.path, request.query = _update_request_uri_query_local_storage(request, self.use_local_storage)
        request.headers = _update_storage_queue_header(request, self.account_name, self.account_key)
        response = self._perform_request(request)

        return _parse_response_for_dict_filter(response, filter=['x-ms-popreceipt', 'x-ms-time-next-visible'])

    def set_queue_service_properties(self, storage_service_properties, timeout=None):
        '''
        Sets the properties of a storage account's Queue service, including Windows Azure 
        Storage Analytics.
        
        storage_service_properties: a StorageServiceProperties object.
        timeout: Optional. The timeout parameter is expressed in seconds.
        '''
        _validate_not_none('storage_service_properties', storage_service_properties)
        request = HTTPRequest()
        request.method = 'PUT'
        request.host = _get_queue_host(self.account_name, self.use_local_storage)
        request.path = '/?restype=service&comp=properties'
        request.query = [('timeout', _int_or_none(timeout))]
        request.body = _get_request_body(_convert_class_to_xml(storage_service_properties))
        request.path, request.query = _update_request_uri_query_local_storage(request, self.use_local_storage)
        request.headers = _update_storage_queue_header(request, self.account_name, self.account_key)
        response = self._perform_request(request)



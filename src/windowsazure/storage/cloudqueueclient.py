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
import base64
import os
import urllib2

from windowsazure.storage import *
from windowsazure.storage.storageclient import _StorageClient
from windowsazure.storage import (_update_storage_queue_header)
from windowsazure import (validate_length, validate_values, validate_not_none, Feed, _Request, 
                                convert_xml_to_feeds, to_right_type, 
                                _get_request_body, _update_request_uri_query, get_host, 
                                _dont_fail_on_exist, _dont_fail_not_exist, HTTPError, 
                                WindowsAzureError, _parse_response, _Request, convert_class_to_xml, 
                                _parse_response_for_dict, _parse_response_for_dict_prefix, 
                                _parse_response_for_dict_filter, _parse_response_for_dict_special, 
                                BLOB_SERVICE, QUEUE_SERVICE, TABLE_SERVICE, SERVICE_BUS_SERVICE)

class CloudQueueClient(_StorageClient):
    '''
    This is the main class managing Blob resources.
    account_name: your storage account name, required for all operations.
    account_key: your storage account key, required for all operations.
    '''

    def get_queue_service_properties(self, timeout=None):
        request = _Request()
        request.method = 'GET'
        request.host = get_host(QUEUE_SERVICE, self.account_name, self.use_local_storage)
        request.uri = '/?restype=service&comp=properties'
        request.query = [('timeout', to_right_type(timeout))]
        request.uri, request.query = _update_request_uri_query(request, self.use_local_storage)
        request.header = _update_storage_queue_header(request, self.account_name, self.account_key)
        respbody = self._perform_request(request)

        return self._parse_response(respbody, StorageServiceProperties)

    def list_queues(self, prefix=None, marker=None, maxresults=None, include=None):
        request = _Request()
        request.method = 'GET'
        request.host = get_host(QUEUE_SERVICE, self.account_name, self.use_local_storage)
        request.uri = '/?comp=list'
        request.query = [
            ('prefix', to_right_type(prefix)),
            ('marker', to_right_type(marker)),
            ('maxresults', to_right_type(maxresults)),
            ('include', to_right_type(include))
            ]
        request.uri, request.query = _update_request_uri_query(request, self.use_local_storage)
        request.header = _update_storage_queue_header(request, self.account_name, self.account_key)
        respbody = self._perform_request(request)

        return self._parse_response(respbody, QueueEnumResults)

    def create_queue(self, queue_name, x_ms_meta_name_values=None, fail_on_exist=False):
        '''
        Creates a queue under the given account.
        
        queue_name: name of the queue.
        x_ms_meta_name_values: Optional. A dict containing name-value pairs to associate 
        		with the queue as metadata.
        fail_on_exist: specify whether throw exception when queue exists.
        '''
        validate_not_none('queue-name', queue_name)
        request = _Request()
        request.method = 'PUT'
        request.host = get_host(QUEUE_SERVICE, self.account_name, self.use_local_storage)
        request.uri = '/' + to_right_type(queue_name) + ''
        request.header = [('x-ms-meta-name-values', to_right_type(x_ms_meta_name_values))]
        request.uri, request.query = _update_request_uri_query(request, self.use_local_storage)
        request.header = _update_storage_queue_header(request, self.account_name, self.account_key)
        if not fail_on_exist:
            try:
                self._perform_request(request)
                return True
            except WindowsAzureError as e:
                _dont_fail_on_exist(e)
                return False
        else:
            self._perform_request(request)
            return True

    def delete_queue(self, queue_name, fail_not_exist=False):
        '''
        Permanently deletes the specified queue.
        
        queue_name: name of the queue.
        fail_not_exist: specify whether throw exception when queue doesn't exist.
        '''
        validate_not_none('queue-name', queue_name)
        request = _Request()
        request.method = 'DELETE'
        request.host = get_host(QUEUE_SERVICE, self.account_name, self.use_local_storage)
        request.uri = '/' + to_right_type(queue_name) + ''
        request.uri, request.query = _update_request_uri_query(request, self.use_local_storage)
        request.header = _update_storage_queue_header(request, self.account_name, self.account_key)
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
        validate_not_none('queue-name', queue_name)
        request = _Request()
        request.method = 'GET'
        request.host = get_host(QUEUE_SERVICE, self.account_name, self.use_local_storage)
        request.uri = '/' + to_right_type(queue_name) + '?comp=metadata'
        request.uri, request.query = _update_request_uri_query(request, self.use_local_storage)
        request.header = _update_storage_queue_header(request, self.account_name, self.account_key)
        respbody = self._perform_request(request)

        return _parse_response_for_dict(self)

    def set_queue_metadata(self, queue_name, x_ms_meta_name_values=None):
        '''
        Sets user-defined metadata on the specified queue. Metadata is associated 
        with the queue as name-value pairs.
        
        queue_name: name of the queue.
        x_ms_meta_name_values: Optional. A dict containing name-value pairs to associate 
        		with the queue as metadata.
        '''
        validate_not_none('queue-name', queue_name)
        request = _Request()
        request.method = 'PUT'
        request.host = get_host(QUEUE_SERVICE, self.account_name, self.use_local_storage)
        request.uri = '/' + to_right_type(queue_name) + '?comp=metadata'
        request.header = [('x-ms-meta-name-values', to_right_type(x_ms_meta_name_values))]
        request.uri, request.query = _update_request_uri_query(request, self.use_local_storage)
        request.header = _update_storage_queue_header(request, self.account_name, self.account_key)
        respbody = self._perform_request(request)

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
        validate_not_none('queue-name', queue_name)
        validate_not_none('MessageText', message_text)
        request = _Request()
        request.method = 'POST'
        request.host = get_host(QUEUE_SERVICE, self.account_name, self.use_local_storage)
        request.uri = '/' + to_right_type(queue_name) + '/messages'
        request.query = [
            ('visibilitytimeout', to_right_type(visibilitytimeout)),
            ('messagettl', to_right_type(messagettl))
            ]
        request.body = _get_request_body(' \
<?xml version="1.0" encoding="utf-8"?> \
<QueueMessage> \
    <MessageText>' + to_right_type(message_text) + '</MessageText> \
</QueueMessage>')
        request.uri, request.query = _update_request_uri_query(request, self.use_local_storage)
        request.header = _update_storage_queue_header(request, self.account_name, self.account_key)
        respbody = self._perform_request(request)

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
        validate_not_none('queue-name', queue_name)
        request = _Request()
        request.method = 'GET'
        request.host = get_host(QUEUE_SERVICE, self.account_name, self.use_local_storage)
        request.uri = '/' + to_right_type(queue_name) + '/messages'
        request.query = [
            ('numofmessages', to_right_type(numofmessages)),
            ('visibilitytimeout', to_right_type(visibilitytimeout))
            ]
        request.uri, request.query = _update_request_uri_query(request, self.use_local_storage)
        request.header = _update_storage_queue_header(request, self.account_name, self.account_key)
        respbody = self._perform_request(request)

        return self._parse_response(respbody, QueueMessageList)

    def peek_messages(self, queue_name, numofmessages=None):
        '''
        Retrieves one or more messages from the front of the queue, but does not alter 
        the visibility of the message. 
        
        queue_name: name of the queue.
        numofmessages: Optional. A nonzero integer value that specifies the number of 
        		messages to peek from the queue, up to a maximum of 32. By default, 
        		a single message is peeked from the queue with this operation.
        '''
        validate_not_none('queue-name', queue_name)
        request = _Request()
        request.method = 'GET'
        request.host = get_host(QUEUE_SERVICE, self.account_name, self.use_local_storage)
        request.uri = '/' + to_right_type(queue_name) + '/messages?peekonly=true'
        request.query = [('numofmessages', to_right_type(numofmessages))]
        request.uri, request.query = _update_request_uri_query(request, self.use_local_storage)
        request.header = _update_storage_queue_header(request, self.account_name, self.account_key)
        respbody = self._perform_request(request)

        return self._parse_response(respbody, QueueMessageList)

    def delete_message(self, queue_name, message_id, popreceipt):
        '''
        Deletes the specified message.
        
        queue_name: name of the queue.
        popreceipt: Required. A valid pop receipt value returned from an earlier call 
        		to the Get Messages or Update Message operation.
        '''
        validate_not_none('queue-name', queue_name)
        validate_not_none('message-id', message_id)
        validate_not_none('popreceipt', popreceipt)
        request = _Request()
        request.method = 'DELETE'
        request.host = get_host(QUEUE_SERVICE, self.account_name, self.use_local_storage)
        request.uri = '/' + to_right_type(queue_name) + '/messages/' + to_right_type(message_id) + ''
        request.query = [('popreceipt', to_right_type(popreceipt))]
        request.uri, request.query = _update_request_uri_query(request, self.use_local_storage)
        request.header = _update_storage_queue_header(request, self.account_name, self.account_key)
        respbody = self._perform_request(request)

    def clear_messages(self, queue_name):
        '''
        Deletes all messages from the specified queue.
        
        queue_name: name of the queue.
        '''
        validate_not_none('queue-name', queue_name)
        request = _Request()
        request.method = 'DELETE'
        request.host = get_host(QUEUE_SERVICE, self.account_name, self.use_local_storage)
        request.uri = '/' + to_right_type(queue_name) + '/messages'
        request.uri, request.query = _update_request_uri_query(request, self.use_local_storage)
        request.header = _update_storage_queue_header(request, self.account_name, self.account_key)
        respbody = self._perform_request(request)

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
        validate_not_none('queue-name', queue_name)
        validate_not_none('message-id', message_id)
        validate_not_none('MessageText', message_text)
        validate_not_none('popreceipt', popreceipt)
        validate_not_none('visibilitytimeout', visibilitytimeout)
        request = _Request()
        request.method = 'PUT'
        request.host = get_host(QUEUE_SERVICE, self.account_name, self.use_local_storage)
        request.uri = '/' + to_right_type(queue_name) + '/messages/' + to_right_type(message_id) + ''
        request.query = [
            ('popreceipt', to_right_type(popreceipt)),
            ('visibilitytimeout', to_right_type(visibilitytimeout))
            ]
        request.body = _get_request_body(' \
<?xml version="1.0" encoding="utf-8"?> \
<QueueMessage> \
    <MessageText>;' + to_right_type(message_text) + '</MessageText> \
</QueueMessage>')
        request.uri, request.query = _update_request_uri_query(request, self.use_local_storage)
        request.header = _update_storage_queue_header(request, self.account_name, self.account_key)
        respbody = self._perform_request(request)

        return _parse_response_for_dict_filter(self, filter=['x-ms-popreceipt', 'x-ms-time-next-visible'])

    def set_queue_service_properties(self, storage_service_properties, timeout=None):
        '''
        Sets the properties of a storage account's Queue service, including Windows Azure 
        Storage Analytics.
        
        storage_service_properties: a StorageServiceProperties object.
        timeout: Optional. The timeout parameter is expressed in seconds.
        '''
        validate_not_none('class:storage_service_properties', storage_service_properties)
        request = _Request()
        request.method = 'PUT'
        request.host = get_host(QUEUE_SERVICE, self.account_name, self.use_local_storage)
        request.uri = '/?restype=service&comp=properties'
        request.query = [('timeout', to_right_type(timeout))]
        request.body = _get_request_body(convert_class_to_xml(storage_service_properties))
        request.uri, request.query = _update_request_uri_query(request, self.use_local_storage)
        request.header = _update_storage_queue_header(request, self.account_name, self.account_key)
        respbody = self._perform_request(request)



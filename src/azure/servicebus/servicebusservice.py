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

from azure.http.httpclient import _HTTPClient
from azure.http import HTTPError, HTTP_RESPONSE_NO_CONTENT
from azure.servicebus import (_update_service_bus_header, _create_message, 
                                convert_topic_to_xml, _convert_response_to_topic, 
                                convert_queue_to_xml, _convert_response_to_queue, 
                                convert_subscription_to_xml, _convert_response_to_subscription, 
                                convert_rule_to_xml, _convert_response_to_rule, 
                                _convert_xml_to_queue, _convert_xml_to_topic, 
                                _convert_xml_to_subscription, _convert_xml_to_rule,
                                _service_bus_error_handler, AZURE_SERVICEBUS_NAMESPACE, 
                                AZURE_SERVICEBUS_ACCESS_KEY, AZURE_SERVICEBUS_ISSUER)
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

class ServiceBusService:

    def create_queue(self, queue_name, queue=None, fail_on_exist=False):
        '''
        Creates a new queue. Once created, this queue's resource manifest is immutable. 
        
        queue: queue object to create. 
        queue_name: the name of the queue.
        fail_on_exist: specify whether to throw an exception when the queue exists.
        '''
        _validate_not_none('queue_name', queue_name)
        request = HTTPRequest()
        request.method = 'PUT'
        request.host = self.service_namespace + SERVICE_BUS_HOST_BASE
        request.path = '/' + str(queue_name) + ''
        request.body = _get_request_body(convert_queue_to_xml(queue))
        request.path, request.query = _update_request_uri_query(request)
        request.headers = _update_service_bus_header(request, self.account_key, self.issuer)
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
        Deletes an existing queue. This operation will also remove all associated state 
        including messages in the queue.
        
        fail_not_exist: specify whether to throw an exception if the queue doesn't exist.
        '''
        _validate_not_none('queue_name', queue_name)
        request = HTTPRequest()
        request.method = 'DELETE'
        request.host = self.service_namespace + SERVICE_BUS_HOST_BASE
        request.path = '/' + str(queue_name) + ''
        request.path, request.query = _update_request_uri_query(request)
        request.headers = _update_service_bus_header(request, self.account_key, self.issuer)
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

    def get_queue(self, queue_name):
        '''
        Retrieves an existing queue.
        
        queue_name: name of the queue.
        '''
        _validate_not_none('queue_name', queue_name)
        request = HTTPRequest()
        request.method = 'GET'
        request.host = self.service_namespace + SERVICE_BUS_HOST_BASE
        request.path = '/' + str(queue_name) + ''
        request.path, request.query = _update_request_uri_query(request)
        request.headers = _update_service_bus_header(request, self.account_key, self.issuer)
        response = self._perform_request(request)

        return _convert_response_to_queue(response)

    def list_queues(self):
        '''
        Enumerates the queues in the service namespace.
        '''
        request = HTTPRequest()
        request.method = 'GET'
        request.host = self.service_namespace + SERVICE_BUS_HOST_BASE
        request.path = '/$Resources/Queues'
        request.path, request.query = _update_request_uri_query(request)
        request.headers = _update_service_bus_header(request, self.account_key, self.issuer)
        response = self._perform_request(request)

        return _convert_response_to_feeds(response, _convert_xml_to_queue)

    def create_topic(self, topic_name, topic=None, fail_on_exist=False):
        '''
        Creates a new topic. Once created, this topic resource manifest is immutable. 
        
        topic_name: name of the topic.
        topic: the Topic object to create.
        fail_on_exist: specify whether to throw an exception when the topic exists.
        '''
        _validate_not_none('topic_name', topic_name)
        request = HTTPRequest()
        request.method = 'PUT'
        request.host = self.service_namespace + SERVICE_BUS_HOST_BASE
        request.path = '/' + str(topic_name) + ''
        request.body = _get_request_body(convert_topic_to_xml(topic))
        request.path, request.query = _update_request_uri_query(request)
        request.headers = _update_service_bus_header(request, self.account_key, self.issuer)
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

    def delete_topic(self, topic_name, fail_not_exist=False):
        '''
        Deletes an existing topic. This operation will also remove all associated state 
        including associated subscriptions.
        
        topic_name: name of the topic.
        fail_not_exist: specify whether throw exception when topic doesn't exist.
        '''
        _validate_not_none('topic_name', topic_name)
        request = HTTPRequest()
        request.method = 'DELETE'
        request.host = self.service_namespace + SERVICE_BUS_HOST_BASE
        request.path = '/' + str(topic_name) + ''
        request.path, request.query = _update_request_uri_query(request)
        request.headers = _update_service_bus_header(request, self.account_key, self.issuer)
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

    def get_topic(self, topic_name):
        '''
        Retrieves the description for the specified topic.
        
        topic_name: name of the topic.
        '''
        _validate_not_none('topic_name', topic_name)
        request = HTTPRequest()
        request.method = 'GET'
        request.host = self.service_namespace + SERVICE_BUS_HOST_BASE
        request.path = '/' + str(topic_name) + ''
        request.path, request.query = _update_request_uri_query(request)
        request.headers = _update_service_bus_header(request, self.account_key, self.issuer)
        response = self._perform_request(request)

        return _convert_response_to_topic(response)

    def list_topics(self):
        '''
        Retrieves the topics in the service namespace.
        '''
        request = HTTPRequest()
        request.method = 'GET'
        request.host = self.service_namespace + SERVICE_BUS_HOST_BASE
        request.path = '/$Resources/Topics'
        request.path, request.query = _update_request_uri_query(request)
        request.headers = _update_service_bus_header(request, self.account_key, self.issuer)
        response = self._perform_request(request)

        return _convert_response_to_feeds(response, _convert_xml_to_topic)

    def create_rule(self, topic_name, subscription_name, rule_name, rule=None, fail_on_exist=False):
        '''
        Creates a new rule. Once created, this rule's resource manifest is immutable.
        
        topic_name: the name of the topic
        subscription_name: the name of the subscription
        rule_name: name of the rule.
        fail_on_exist: specify whether to throw an exception when the rule exists.
        '''
        _validate_not_none('topic_name', topic_name)
        _validate_not_none('subscription_name', subscription_name)
        _validate_not_none('rule_name', rule_name)
        request = HTTPRequest()
        request.method = 'PUT'
        request.host = self.service_namespace + SERVICE_BUS_HOST_BASE
        request.path = '/' + str(topic_name) + '/subscriptions/' + str(subscription_name) + '/rules/' + str(rule_name) + ''
        request.body = _get_request_body(convert_rule_to_xml(rule))
        request.path, request.query = _update_request_uri_query(request)
        request.headers = _update_service_bus_header(request, self.account_key, self.issuer)
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

    def delete_rule(self, topic_name, subscription_name, rule_name, fail_not_exist=False):
        '''
        Deletes an existing rule.
        
        topic_name: the name of the topic
        subscription_name: the name of the subscription
        rule_name: the name of the rule.  DEFAULT_RULE_NAME=$Default. Use DEFAULT_RULE_NAME
        		to delete default rule for the subscription.
        fail_not_exist: specify whether throw exception when rule doesn't exist.
        '''
        _validate_not_none('topic_name', topic_name)
        _validate_not_none('subscription_name', subscription_name)
        _validate_not_none('rule_name', rule_name)
        request = HTTPRequest()
        request.method = 'DELETE'
        request.host = self.service_namespace + SERVICE_BUS_HOST_BASE
        request.path = '/' + str(topic_name) + '/subscriptions/' + str(subscription_name) + '/rules/' + str(rule_name) + ''
        request.path, request.query = _update_request_uri_query(request)
        request.headers = _update_service_bus_header(request, self.account_key, self.issuer)
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

    def get_rule(self, topic_name, subscription_name, rule_name):
        '''
        Retrieves the description for the specified rule. 
        
        topic_name: the name of the topic
        subscription_name: the name of the subscription
        rule_name: name of the rule
        '''
        _validate_not_none('topic_name', topic_name)
        _validate_not_none('subscription_name', subscription_name)
        _validate_not_none('rule_name', rule_name)
        request = HTTPRequest()
        request.method = 'GET'
        request.host = self.service_namespace + SERVICE_BUS_HOST_BASE
        request.path = '/' + str(topic_name) + '/subscriptions/' + str(subscription_name) + '/rules/' + str(rule_name) + ''
        request.path, request.query = _update_request_uri_query(request)
        request.headers = _update_service_bus_header(request, self.account_key, self.issuer)
        response = self._perform_request(request)

        return _convert_response_to_rule(response)

    def list_rules(self, topic_name, subscription_name):
        '''
        Retrieves the rules that exist under the specified subscription. 
        
        topic_name: the name of the topic
        subscription_name: the name of the subscription
        '''
        _validate_not_none('topic_name', topic_name)
        _validate_not_none('subscription_name', subscription_name)
        request = HTTPRequest()
        request.method = 'GET'
        request.host = self.service_namespace + SERVICE_BUS_HOST_BASE
        request.path = '/' + str(topic_name) + '/subscriptions/' + str(subscription_name) + '/rules/'
        request.path, request.query = _update_request_uri_query(request)
        request.headers = _update_service_bus_header(request, self.account_key, self.issuer)
        response = self._perform_request(request)

        return _convert_response_to_feeds(response, _convert_xml_to_rule)

    def create_subscription(self, topic_name, subscription_name, subscription=None, fail_on_exist=False):
        '''
        Creates a new subscription. Once created, this subscription resource manifest is 
        immutable. 
        
        topic_name: the name of the topic
        subscription_name: the name of the subscription
        fail_on_exist: specify whether throw exception when subscription exists.
        '''
        _validate_not_none('topic_name', topic_name)
        _validate_not_none('subscription_name', subscription_name)
        request = HTTPRequest()
        request.method = 'PUT'
        request.host = self.service_namespace + SERVICE_BUS_HOST_BASE
        request.path = '/' + str(topic_name) + '/subscriptions/' + str(subscription_name) + ''
        request.body = _get_request_body(convert_subscription_to_xml(subscription))
        request.path, request.query = _update_request_uri_query(request)
        request.headers = _update_service_bus_header(request, self.account_key, self.issuer)
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

    def delete_subscription(self, topic_name, subscription_name, fail_not_exist=False):
        '''
        Deletes an existing subscription.
        
        topic_name: the name of the topic
        subscription_name: the name of the subscription
        fail_not_exist: specify whether to throw an exception when the subscription doesn't exist.
        '''
        _validate_not_none('topic_name', topic_name)
        _validate_not_none('subscription_name', subscription_name)
        request = HTTPRequest()
        request.method = 'DELETE'
        request.host = self.service_namespace + SERVICE_BUS_HOST_BASE
        request.path = '/' + str(topic_name) + '/subscriptions/' + str(subscription_name) + ''
        request.path, request.query = _update_request_uri_query(request)
        request.headers = _update_service_bus_header(request, self.account_key, self.issuer)
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

    def get_subscription(self, topic_name, subscription_name):
        '''
        Gets an existing subscription.
        
        topic_name: the name of the topic
        subscription_name: the name of the subscription
        '''
        _validate_not_none('topic_name', topic_name)
        _validate_not_none('subscription_name', subscription_name)
        request = HTTPRequest()
        request.method = 'GET'
        request.host = self.service_namespace + SERVICE_BUS_HOST_BASE
        request.path = '/' + str(topic_name) + '/subscriptions/' + str(subscription_name) + ''
        request.path, request.query = _update_request_uri_query(request)
        request.headers = _update_service_bus_header(request, self.account_key, self.issuer)
        response = self._perform_request(request)

        return _convert_response_to_subscription(response)

    def list_subscriptions(self, topic_name):
        '''
        Retrieves the subscriptions in the specified topic. 
        
        topic_name: the name of the topic
        '''
        _validate_not_none('topic_name', topic_name)
        request = HTTPRequest()
        request.method = 'GET'
        request.host = self.service_namespace + SERVICE_BUS_HOST_BASE
        request.path = '/' + str(topic_name) + '/subscriptions/'
        request.path, request.query = _update_request_uri_query(request)
        request.headers = _update_service_bus_header(request, self.account_key, self.issuer)
        response = self._perform_request(request)

        return _convert_response_to_feeds(response, _convert_xml_to_subscription)

    def send_topic_message(self, topic_name, message=None):
        '''
        Enqueues a message into the specified topic. The limit to the number of messages 
        which may be present in the topic is governed by the message size in MaxTopicSizeInBytes. 
        If this message causes the topic to exceed its quota, a quota exceeded error is 
        returned and the message will be rejected.
        
        topic_name: name of the topic.
        message: the Message object containing message body and properties.
        '''
        _validate_not_none('topic_name', topic_name)
        request = HTTPRequest()
        request.method = 'POST'
        request.host = self.service_namespace + SERVICE_BUS_HOST_BASE
        request.path = '/' + str(topic_name) + '/messages'
        request.headers = message.add_headers(request)
        request.body = _get_request_body(message.body)
        request.path, request.query = _update_request_uri_query(request)
        request.headers = _update_service_bus_header(request, self.account_key, self.issuer)
        response = self._perform_request(request)

    def peek_lock_subscription_message(self, topic_name, subscription_name, timeout='60'):
        '''
        This operation is used to atomically retrieve and lock a message for processing. 
        The message is guaranteed not to be delivered to other receivers during the lock 
        duration period specified in buffer description. Once the lock expires, the 
        message will be available to other receivers (on the same subscription only) 
        during the lock duration period specified in the topic description. Once the lock
        expires, the message will be available to other receivers. In order to complete 
        processing of the message, the receiver should issue a delete command with the 
        lock ID received from this operation. To abandon processing of the message and 
        unlock it for other receivers, an Unlock Message command should be issued, or 
        the lock duration period can expire. 
        
        topic_name: the name of the topic
        subscription_name: the name of the subscription
        '''
        _validate_not_none('topic_name', topic_name)
        _validate_not_none('subscription_name', subscription_name)
        request = HTTPRequest()
        request.method = 'POST'
        request.host = self.service_namespace + SERVICE_BUS_HOST_BASE
        request.path = '/' + str(topic_name) + '/subscriptions/' + str(subscription_name) + '/messages/head'
        request.query = [('timeout', _int_or_none(timeout))]
        request.path, request.query = _update_request_uri_query(request)
        request.headers = _update_service_bus_header(request, self.account_key, self.issuer)
        response = self._perform_request(request)

        return _create_message(response, self)

    def unlock_subscription_message(self, topic_name, subscription_name, sequence_number, lock_token):
        '''
        Unlock a message for processing by other receivers on a given subscription. 
        This operation deletes the lock object, causing the message to be unlocked. 
        A message must have first been locked by a receiver before this operation 
        is called.
        
        topic_name: the name of the topic
        subscription_name: the name of the subscription
        sequence_name: The sequence number of the message to be unlocked as returned 
        		in BrokerProperties['SequenceNumber'] by the Peek Message operation.
        lock_token: The ID of the lock as returned by the Peek Message operation in 
        		BrokerProperties['LockToken']
        '''
        _validate_not_none('topic_name', topic_name)
        _validate_not_none('subscription_name', subscription_name)
        _validate_not_none('sequence_number', sequence_number)
        _validate_not_none('lock_token', lock_token)
        request = HTTPRequest()
        request.method = 'PUT'
        request.host = self.service_namespace + SERVICE_BUS_HOST_BASE
        request.path = '/' + str(topic_name) + '/subscriptions/' + str(subscription_name) + '/messages/' + str(sequence_number) + '/' + str(lock_token) + ''
        request.path, request.query = _update_request_uri_query(request)
        request.headers = _update_service_bus_header(request, self.account_key, self.issuer)
        response = self._perform_request(request)

    def read_delete_subscription_message(self, topic_name, subscription_name, timeout='60'):
        '''
        Read and delete a message from a subscription as an atomic operation. This 
        operation should be used when a best-effort guarantee is sufficient for an 
        application; that is, using this operation it is possible for messages to 
        be lost if processing fails.
        
        topic_name: the name of the topic
        subscription_name: the name of the subscription
        '''
        _validate_not_none('topic_name', topic_name)
        _validate_not_none('subscription_name', subscription_name)
        request = HTTPRequest()
        request.method = 'DELETE'
        request.host = self.service_namespace + SERVICE_BUS_HOST_BASE
        request.path = '/' + str(topic_name) + '/subscriptions/' + str(subscription_name) + '/messages/head'
        request.query = [('timeout', _int_or_none(timeout))]
        request.path, request.query = _update_request_uri_query(request)
        request.headers = _update_service_bus_header(request, self.account_key, self.issuer)
        response = self._perform_request(request)

        return _create_message(response, self)

    def delete_subscription_message(self, topic_name, subscription_name, sequence_number, lock_token):
        '''
        Completes processing on a locked message and delete it from the subscription. 
        This operation should only be called after processing a previously locked 
        message is successful to maintain At-Least-Once delivery assurances.
        
        topic_name: the name of the topic
        subscription_name: the name of the subscription
        sequence_name: The sequence number of the message to be deleted as returned 
        		in BrokerProperties['SequenceNumber'] by the Peek Message operation.
        lock_token: The ID of the lock as returned by the Peek Message operation in 
        		BrokerProperties['LockToken']
        '''
        _validate_not_none('topic_name', topic_name)
        _validate_not_none('subscription_name', subscription_name)
        _validate_not_none('sequence_number', sequence_number)
        _validate_not_none('lock_token', lock_token)
        request = HTTPRequest()
        request.method = 'DELETE'
        request.host = self.service_namespace + SERVICE_BUS_HOST_BASE
        request.path = '/' + str(topic_name) + '/subscriptions/' + str(subscription_name) + '/messages/' + str(sequence_number) + '/' + str(lock_token) + ''
        request.path, request.query = _update_request_uri_query(request)
        request.headers = _update_service_bus_header(request, self.account_key, self.issuer)
        response = self._perform_request(request)

    def send_queue_message(self, queue_name, message=None):
        '''
        Sends a message into the specified queue. The limit to the number of messages 
        which may be present in the topic is governed by the message size the 
        MaxTopicSizeInMegaBytes. If this message will cause the queue to exceed its 
        quota, a quota exceeded error is returned and the message will be rejected.
        
        queue_name: name of the queue
        message: the Message object containing message body and properties.
        '''
        _validate_not_none('queue_name', queue_name)
        request = HTTPRequest()
        request.method = 'POST'
        request.host = self.service_namespace + SERVICE_BUS_HOST_BASE
        request.path = '/' + str(queue_name) + '/messages'
        request.headers = message.add_headers(request)
        request.body = _get_request_body(message.body)
        request.path, request.query = _update_request_uri_query(request)
        request.headers = _update_service_bus_header(request, self.account_key, self.issuer)
        response = self._perform_request(request)

    def peek_lock_queue_message(self, queue_name, timeout='60'):
        '''
        Automically retrieves and locks a message from a queue for processing. The 
        message is guaranteed not to be delivered to other receivers (on the same 
        subscription only) during the lock duration period specified in the queue 
        description. Once the lock expires, the message will be available to other 
        receivers. In order to complete processing of the message, the receiver 
        should issue a delete command with the lock ID received from this operation. 
        To abandon processing of the message and unlock it for other receivers, 
        an Unlock Message command should be issued, or the lock duration period 
        can expire.
        
        queue_name: name of the queue
        '''
        _validate_not_none('queue_name', queue_name)
        request = HTTPRequest()
        request.method = 'POST'
        request.host = self.service_namespace + SERVICE_BUS_HOST_BASE
        request.path = '/' + str(queue_name) + '/messages/head'
        request.query = [('timeout', _int_or_none(timeout))]
        request.path, request.query = _update_request_uri_query(request)
        request.headers = _update_service_bus_header(request, self.account_key, self.issuer)
        response = self._perform_request(request)

        return _create_message(response, self)

    def unlock_queue_message(self, queue_name, sequence_number, lock_token):
        '''
        Unlocks a message for processing by other receivers on a given subscription. 
        This operation deletes the lock object, causing the message to be unlocked. 
        A message must have first been locked by a receiver before this operation is 
        called.
        
        queue_name: name of the queue
        sequence_name: The sequence number of the message to be unlocked as returned 
        		in BrokerProperties['SequenceNumber'] by the Peek Message operation.
        lock_token: The ID of the lock as returned by the Peek Message operation in 
        		BrokerProperties['LockToken']
        '''
        _validate_not_none('queue_name', queue_name)
        _validate_not_none('sequence_number', sequence_number)
        _validate_not_none('lock_token', lock_token)
        request = HTTPRequest()
        request.method = 'PUT'
        request.host = self.service_namespace + SERVICE_BUS_HOST_BASE
        request.path = '/' + str(queue_name) + '/messages/' + str(sequence_number) + '/' + str(lock_token) + ''
        request.path, request.query = _update_request_uri_query(request)
        request.headers = _update_service_bus_header(request, self.account_key, self.issuer)
        response = self._perform_request(request)

    def read_delete_queue_message(self, queue_name, timeout='60'):
        '''
        Reads and deletes a message from a queue as an atomic operation. This operation 
        should be used when a best-effort guarantee is sufficient for an application; 
        that is, using this operation it is possible for messages to be lost if 
        processing fails.
        
        queue_name: name of the queue
        '''
        _validate_not_none('queue_name', queue_name)
        request = HTTPRequest()
        request.method = 'DELETE'
        request.host = self.service_namespace + SERVICE_BUS_HOST_BASE
        request.path = '/' + str(queue_name) + '/messages/head'
        request.query = [('timeout', _int_or_none(timeout))]
        request.path, request.query = _update_request_uri_query(request)
        request.headers = _update_service_bus_header(request, self.account_key, self.issuer)
        response = self._perform_request(request)

        return _create_message(response, self)

    def delete_queue_message(self, queue_name, sequence_number, lock_token):
        '''
        Completes processing on a locked message and delete it from the queue. This 
        operation should only be called after processing a previously locked message 
        is successful to maintain At-Least-Once delivery assurances.
        
        queue_name: name of the queue
        sequence_name: The sequence number of the message to be deleted as returned 
        		in BrokerProperties['SequenceNumber'] by the Peek Message operation.
        lock_token: The ID of the lock as returned by the Peek Message operation in 
        		BrokerProperties['LockToken']
        '''
        _validate_not_none('queue_name', queue_name)
        _validate_not_none('sequence_number', sequence_number)
        _validate_not_none('lock_token', lock_token)
        request = HTTPRequest()
        request.method = 'DELETE'
        request.host = self.service_namespace + SERVICE_BUS_HOST_BASE
        request.path = '/' + str(queue_name) + '/messages/' + str(sequence_number) + '/' + str(lock_token) + ''
        request.path, request.query = _update_request_uri_query(request)
        request.headers = _update_service_bus_header(request, self.account_key, self.issuer)
        response = self._perform_request(request)


    def receive_queue_message(self, queue_name, peek_lock=True, timeout=60):
        if peek_lock:
            return self.peek_lock_queue_message(queue_name, timeout)
        else:
            return self.read_delete_queue_message(queue_name, timeout)
    
    def receive_subscription_message(self, topic_name, subscription_name, peek_lock=True, timeout=60):
        if peek_lock:
            return self.peek_lock_subscription_message(topic_name, subscription_name, timeout)
        else:
            return self.read_delete_subscription_message(topic_name, subscription_name, timeout)
    
    def __init__(self, service_namespace=None, account_key=None, issuer=None, x_ms_version='2011-06-01'):
        self.requestid = None
        self.service_namespace = service_namespace
        self.account_key = account_key
        self.issuer = issuer    
    
        #get service namespace, account key and issuer. If they are set when constructing, then use them.
        #else find them from environment variables.
        if not service_namespace:
            if os.environ.has_key(AZURE_SERVICEBUS_NAMESPACE):
                self.service_namespace = os.environ[AZURE_SERVICEBUS_NAMESPACE]
        if not account_key:
            if os.environ.has_key(AZURE_SERVICEBUS_ACCESS_KEY):
                self.account_key = os.environ[AZURE_SERVICEBUS_ACCESS_KEY]
        if not issuer:
            if os.environ.has_key(AZURE_SERVICEBUS_ISSUER):
                self.issuer = os.environ[AZURE_SERVICEBUS_ISSUER]
        
        if not self.service_namespace or not self.account_key or not self.issuer:
            raise WindowsAzureError('You need to provide servicebus namespace, access key and Issuer')
        
        self.x_ms_version = x_ms_version
        self._httpclient = _HTTPClient(service_instance=self, service_namespace=service_namespace, account_key=account_key, issuer=issuer, x_ms_version=self.x_ms_version)
        self._filter = self._httpclient.perform_request
    
    def with_filter(self, filter):
        '''Returns a new service which will process requests with the
        specified filter.  Filtering operations can include logging, automatic
        retrying, etc...  The filter is a lambda which receives the HTTPRequest
        and another lambda.  The filter can perform any pre-processing on the
        request, pass it off to the next lambda, and then perform any post-processing
        on the response.'''
        res = ServiceBusService(self.service_namespace, self.account_key, 
                                self.issuer, self.x_ms_version)
        old_filter = self._filter
        def new_filter(request):
            return filter(request, old_filter)
                    
        res._filter = new_filter
        return res
            
    def _perform_request(self, request):
        try:
            resp = self._filter(request)
        except HTTPError as e:
            return _service_bus_error_handler(e)
    
        return resp
    

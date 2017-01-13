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
import datetime
import os
import time
import json

import requests

from azure.common import (
    AzureHttpError,
)
from .constants import (
    AZURE_SERVICEBUS_NAMESPACE,
    AZURE_SERVICEBUS_ACCESS_KEY,
    AZURE_SERVICEBUS_ISSUER,
    DEFAULT_HTTP_TIMEOUT,
    SERVICE_BUS_HOST_BASE,
    _USER_AGENT_STRING,
)
from ._common_error import (
    _dont_fail_not_exist,
    _dont_fail_on_exist,
    _validate_not_none,
)
from ._common_models import (
    _unicode_type,
)
from ._common_conversion import (
    _encode_base64,
    _int_or_none,
    _sign_string,
    _str,
)
from ._common_serialization import (
    _ETreeXmlToObject,
    _get_request_body,
    url_quote,
    url_unquote,
)
from ._http import (
    HTTPError,
    HTTPRequest,
)
from ._http.httpclient import _HTTPClient
from ._serialization import (
    _convert_event_hub_to_xml,
    _convert_topic_to_xml,
    _convert_response_to_topic,
    _convert_queue_to_xml,
    _convert_response_to_queue,
    _convert_subscription_to_xml,
    _convert_response_to_subscription,
    _convert_rule_to_xml,
    _convert_response_to_rule,
    _convert_response_to_event_hub,
    _convert_etree_element_to_queue,
    _convert_etree_element_to_topic,
    _convert_etree_element_to_subscription,
    _convert_etree_element_to_rule,
    _create_message,
    _service_bus_error_handler,
)


class ServiceBusService(object):

    def __init__(self, service_namespace=None, account_key=None, issuer=None,
                 x_ms_version='2011-06-01', host_base=SERVICE_BUS_HOST_BASE,
                 shared_access_key_name=None, shared_access_key_value=None,
                 authentication=None, timeout=DEFAULT_HTTP_TIMEOUT,
                 request_session=None):
        '''
        Initializes the service bus service for a namespace with the specified
        authentication settings (SAS or ACS).

        service_namespace:
            Service bus namespace, required for all operations. If None,
            the value is set to the AZURE_SERVICEBUS_NAMESPACE env variable.
        account_key:
            ACS authentication account key. If None, the value is set to the
            AZURE_SERVICEBUS_ACCESS_KEY env variable.
            Note that if both SAS and ACS settings are specified, SAS is used.
        issuer:
            ACS authentication issuer. If None, the value is set to the
            AZURE_SERVICEBUS_ISSUER env variable.
            Note that if both SAS and ACS settings are specified, SAS is used.
        x_ms_version:
            Unused. Kept for backwards compatibility.
        host_base:
            Optional. Live host base url. Defaults to Azure url. Override this
            for on-premise.
        shared_access_key_name:
            SAS authentication key name.
            Note that if both SAS and ACS settings are specified, SAS is used.
        shared_access_key_value:
            SAS authentication key value.
            Note that if both SAS and ACS settings are specified, SAS is used.
        authentication:
            Instance of authentication class. If this is specified, then
            ACS and SAS parameters are ignored.
        timeout:
            Optional. Timeout for the http request, in seconds.
        request_session:
            Optional. Session object to use for http requests.
        '''
        self.requestid = None
        self.service_namespace = service_namespace
        self.host_base = host_base

        if not self.service_namespace:
            self.service_namespace = os.environ.get(AZURE_SERVICEBUS_NAMESPACE)

        if not self.service_namespace:
            raise ValueError('You need to provide servicebus namespace')

        if authentication:
            self.authentication = authentication
        else:
            if not account_key:
                account_key = os.environ.get(AZURE_SERVICEBUS_ACCESS_KEY)
            if not issuer:
                issuer = os.environ.get(AZURE_SERVICEBUS_ISSUER)

            if shared_access_key_name and shared_access_key_value:
                self.authentication = ServiceBusSASAuthentication(
                    shared_access_key_name,
                    shared_access_key_value)
            elif account_key and issuer:
                self.authentication = ServiceBusWrapTokenAuthentication(
                    account_key,
                    issuer)
            else:
                raise ValueError(
                    'You need to provide servicebus access key and Issuer OR shared access key and value')

        self._httpclient = _HTTPClient(
            service_instance=self,
            timeout=timeout,
            request_session=request_session or requests.Session(),
            user_agent=_USER_AGENT_STRING,
        )
        self._filter = self._httpclient.perform_request

    @staticmethod
    def format_dead_letter_queue_name(queue_name):
        """Get the dead letter name of this queue"""
        return queue_name + '/$DeadLetterQueue'

    @staticmethod
    def format_dead_letter_subscription_name(subscription_name):
        """Get the dead letter name of this subscription"""
        return subscription_name + '/$DeadLetterQueue'

    # Backwards compatibility:
    # account_key and issuer used to be stored on the service class, they are
    # now stored on the authentication class.
    @property
    def account_key(self):
        return self.authentication.account_key

    @account_key.setter
    def account_key(self, value):
        self.authentication.account_key = value

    @property
    def issuer(self):
        return self.authentication.issuer

    @issuer.setter
    def issuer(self, value):
        self.authentication.issuer = value

    def with_filter(self, filter):
        '''
        Returns a new service which will process requests with the specified
        filter.  Filtering operations can include logging, automatic retrying,
        etc...  The filter is a lambda which receives the HTTPRequest and
        another lambda.  The filter can perform any pre-processing on the
        request, pass it off to the next lambda, and then perform any
        post-processing on the response.
        '''
        res = ServiceBusService(
            service_namespace=self.service_namespace,
            authentication=self.authentication)

        old_filter = self._filter

        def new_filter(request):
            return filter(request, old_filter)

        res._filter = new_filter
        return res

    def set_proxy(self, host, port, user=None, password=None):
        '''
        Sets the proxy server host and port for the HTTP CONNECT Tunnelling.

        host:
            Address of the proxy. Ex: '192.168.0.100'
        port:
            Port of the proxy. Ex: 6000
        user:
            User for proxy authorization.
        password:
            Password for proxy authorization.
        '''
        self._httpclient.set_proxy(host, port, user, password)

    @property
    def timeout(self):
        return self._httpclient.timeout

    @timeout.setter
    def timeout(self, value):
        self._httpclient.timeout = value

    def create_queue(self, queue_name, queue=None, fail_on_exist=False):
        '''
        Creates a new queue. Once created, this queue's resource manifest is
        immutable.

        queue_name:
            Name of the queue to create.
        queue:
            Queue object to create.
        fail_on_exist:
            Specify whether to throw an exception when the queue exists.
        '''
        _validate_not_none('queue_name', queue_name)
        request = HTTPRequest()
        request.method = 'PUT'
        request.host = self._get_host()
        request.path = '/' + _str(queue_name) + ''
        request.body = _get_request_body(_convert_queue_to_xml(queue))
        request.path, request.query = self._httpclient._update_request_uri_query(request)
        request.headers = self._update_service_bus_header(request)
        if not fail_on_exist:
            try:
                self._perform_request(request)
                return True
            except AzureHttpError as ex:
                _dont_fail_on_exist(ex)
                return False
        else:
            self._perform_request(request)
            return True

    def delete_queue(self, queue_name, fail_not_exist=False):
        '''
        Deletes an existing queue. This operation will also remove all
        associated state including messages in the queue.

        queue_name:
            Name of the queue to delete.
        fail_not_exist:
            Specify whether to throw an exception if the queue doesn't exist.
        '''
        _validate_not_none('queue_name', queue_name)
        request = HTTPRequest()
        request.method = 'DELETE'
        request.host = self._get_host()
        request.path = '/' + _str(queue_name) + ''
        request.path, request.query = self._httpclient._update_request_uri_query(request)
        request.headers = self._update_service_bus_header(request)
        if not fail_not_exist:
            try:
                self._perform_request(request)
                return True
            except AzureHttpError as ex:
                _dont_fail_not_exist(ex)
                return False
        else:
            self._perform_request(request)
            return True

    def get_queue(self, queue_name):
        '''
        Retrieves an existing queue.

        queue_name:
            Name of the queue.
        '''
        _validate_not_none('queue_name', queue_name)
        request = HTTPRequest()
        request.method = 'GET'
        request.host = self._get_host()
        request.path = '/' + _str(queue_name) + ''
        request.path, request.query = self._httpclient._update_request_uri_query(request)
        request.headers = self._update_service_bus_header(request)
        response = self._perform_request(request)

        return _convert_response_to_queue(response)

    def list_queues(self):
        '''
        Enumerates the queues in the service namespace.
        '''
        request = HTTPRequest()
        request.method = 'GET'
        request.host = self._get_host()
        request.path = '/$Resources/Queues'
        request.path, request.query = self._httpclient._update_request_uri_query(request)
        request.headers = self._update_service_bus_header(request)
        response = self._perform_request(request)

        return _ETreeXmlToObject.convert_response_to_feeds(
            response, _convert_etree_element_to_queue)

    def create_topic(self, topic_name, topic=None, fail_on_exist=False):
        '''
        Creates a new topic. Once created, this topic resource manifest is
        immutable.

        topic_name:
            Name of the topic to create.
        topic:
            Topic object to create.
        fail_on_exist:
            Specify whether to throw an exception when the topic exists.
        '''
        _validate_not_none('topic_name', topic_name)
        request = HTTPRequest()
        request.method = 'PUT'
        request.host = self._get_host()
        request.path = '/' + _str(topic_name) + ''
        request.body = _get_request_body(_convert_topic_to_xml(topic))
        request.path, request.query = self._httpclient._update_request_uri_query(request)
        request.headers = self._update_service_bus_header(request)
        if not fail_on_exist:
            try:
                self._perform_request(request)
                return True
            except AzureHttpError as ex:
                _dont_fail_on_exist(ex)
                return False
        else:
            self._perform_request(request)
            return True

    def delete_topic(self, topic_name, fail_not_exist=False):
        '''
        Deletes an existing topic. This operation will also remove all
        associated state including associated subscriptions.

        topic_name:
            Name of the topic to delete.
        fail_not_exist:
            Specify whether throw exception when topic doesn't exist.
        '''
        _validate_not_none('topic_name', topic_name)
        request = HTTPRequest()
        request.method = 'DELETE'
        request.host = self._get_host()
        request.path = '/' + _str(topic_name) + ''
        request.path, request.query = self._httpclient._update_request_uri_query(request)
        request.headers = self._update_service_bus_header(request)
        if not fail_not_exist:
            try:
                self._perform_request(request)
                return True
            except AzureHttpError as ex:
                _dont_fail_not_exist(ex)
                return False
        else:
            self._perform_request(request)
            return True

    def get_topic(self, topic_name):
        '''
        Retrieves the description for the specified topic.

        topic_name:
            Name of the topic.
        '''
        _validate_not_none('topic_name', topic_name)
        request = HTTPRequest()
        request.method = 'GET'
        request.host = self._get_host()
        request.path = '/' + _str(topic_name) + ''
        request.path, request.query = self._httpclient._update_request_uri_query(request)
        request.headers = self._update_service_bus_header(request)
        response = self._perform_request(request)

        return _convert_response_to_topic(response)

    def list_topics(self):
        '''
        Retrieves the topics in the service namespace.
        '''
        request = HTTPRequest()
        request.method = 'GET'
        request.host = self._get_host()
        request.path = '/$Resources/Topics'
        request.path, request.query = self._httpclient._update_request_uri_query(request)
        request.headers = self._update_service_bus_header(request)
        response = self._perform_request(request)

        return _ETreeXmlToObject.convert_response_to_feeds(
            response, _convert_etree_element_to_topic)

    def create_rule(self, topic_name, subscription_name, rule_name, rule=None,
                    fail_on_exist=False):
        '''
        Creates a new rule. Once created, this rule's resource manifest is
        immutable.

        topic_name:
            Name of the topic.
        subscription_name:
            Name of the subscription.
        rule_name:
            Name of the rule.
        fail_on_exist:
            Specify whether to throw an exception when the rule exists.
        '''
        _validate_not_none('topic_name', topic_name)
        _validate_not_none('subscription_name', subscription_name)
        _validate_not_none('rule_name', rule_name)
        request = HTTPRequest()
        request.method = 'PUT'
        request.host = self._get_host()
        request.path = '/' + _str(topic_name) + '/subscriptions/' + \
            _str(subscription_name) + \
            '/rules/' + _str(rule_name) + ''
        request.body = _get_request_body(_convert_rule_to_xml(rule))
        request.path, request.query = self._httpclient._update_request_uri_query(request)
        request.headers = self._update_service_bus_header(request)
        if not fail_on_exist:
            try:
                self._perform_request(request)
                return True
            except AzureHttpError as ex:
                _dont_fail_on_exist(ex)
                return False
        else:
            self._perform_request(request)
            return True

    def delete_rule(self, topic_name, subscription_name, rule_name,
                    fail_not_exist=False):
        '''
        Deletes an existing rule.

        topic_name:
            Name of the topic.
        subscription_name:
            Name of the subscription.
        rule_name:
            Name of the rule to delete.  DEFAULT_RULE_NAME=$Default.
            Use DEFAULT_RULE_NAME to delete default rule for the subscription.
        fail_not_exist:
            Specify whether throw exception when rule doesn't exist.
        '''
        _validate_not_none('topic_name', topic_name)
        _validate_not_none('subscription_name', subscription_name)
        _validate_not_none('rule_name', rule_name)
        request = HTTPRequest()
        request.method = 'DELETE'
        request.host = self._get_host()
        request.path = '/' + _str(topic_name) + '/subscriptions/' + \
            _str(subscription_name) + \
            '/rules/' + _str(rule_name) + ''
        request.path, request.query = self._httpclient._update_request_uri_query(request)
        request.headers = self._update_service_bus_header(request)
        if not fail_not_exist:
            try:
                self._perform_request(request)
                return True
            except AzureHttpError as ex:
                _dont_fail_not_exist(ex)
                return False
        else:
            self._perform_request(request)
            return True

    def get_rule(self, topic_name, subscription_name, rule_name):
        '''
        Retrieves the description for the specified rule.

        topic_name:
            Name of the topic.
        subscription_name:
            Name of the subscription.
        rule_name:
            Name of the rule.
        '''
        _validate_not_none('topic_name', topic_name)
        _validate_not_none('subscription_name', subscription_name)
        _validate_not_none('rule_name', rule_name)
        request = HTTPRequest()
        request.method = 'GET'
        request.host = self._get_host()
        request.path = '/' + _str(topic_name) + '/subscriptions/' + \
            _str(subscription_name) + \
            '/rules/' + _str(rule_name) + ''
        request.path, request.query = self._httpclient._update_request_uri_query(request)
        request.headers = self._update_service_bus_header(request)
        response = self._perform_request(request)

        return _convert_response_to_rule(response)

    def list_rules(self, topic_name, subscription_name):
        '''
        Retrieves the rules that exist under the specified subscription.

        topic_name:
            Name of the topic.
        subscription_name:
            Name of the subscription.
        '''
        _validate_not_none('topic_name', topic_name)
        _validate_not_none('subscription_name', subscription_name)
        request = HTTPRequest()
        request.method = 'GET'
        request.host = self._get_host()
        request.path = '/' + \
            _str(topic_name) + '/subscriptions/' + \
            _str(subscription_name) + '/rules/'
        request.path, request.query = self._httpclient._update_request_uri_query(request)
        request.headers = self._update_service_bus_header(request)
        response = self._perform_request(request)

        return _ETreeXmlToObject.convert_response_to_feeds(
            response, _convert_etree_element_to_rule)

    def create_subscription(self, topic_name, subscription_name,
                            subscription=None, fail_on_exist=False):
        '''
        Creates a new subscription. Once created, this subscription resource
        manifest is immutable.

        topic_name:
            Name of the topic.
        subscription_name:
            Name of the subscription.
        fail_on_exist:
            Specify whether throw exception when subscription exists.
        '''
        _validate_not_none('topic_name', topic_name)
        _validate_not_none('subscription_name', subscription_name)
        request = HTTPRequest()
        request.method = 'PUT'
        request.host = self._get_host()
        request.path = '/' + \
            _str(topic_name) + '/subscriptions/' + _str(subscription_name) + ''
        request.body = _get_request_body(
            _convert_subscription_to_xml(subscription))
        request.path, request.query = self._httpclient._update_request_uri_query(request)
        request.headers = self._update_service_bus_header(request)
        if not fail_on_exist:
            try:
                self._perform_request(request)
                return True
            except AzureHttpError as ex:
                _dont_fail_on_exist(ex)
                return False
        else:
            self._perform_request(request)
            return True

    def delete_subscription(self, topic_name, subscription_name,
                            fail_not_exist=False):
        '''
        Deletes an existing subscription.

        topic_name:
            Name of the topic.
        subscription_name:
            Name of the subscription to delete.
        fail_not_exist:
            Specify whether to throw an exception when the subscription
            doesn't exist.
        '''
        _validate_not_none('topic_name', topic_name)
        _validate_not_none('subscription_name', subscription_name)
        request = HTTPRequest()
        request.method = 'DELETE'
        request.host = self._get_host()
        request.path = '/' + \
            _str(topic_name) + '/subscriptions/' + _str(subscription_name) + ''
        request.path, request.query = self._httpclient._update_request_uri_query(request)
        request.headers = self._update_service_bus_header(request)
        if not fail_not_exist:
            try:
                self._perform_request(request)
                return True
            except AzureHttpError as ex:
                _dont_fail_not_exist(ex)
                return False
        else:
            self._perform_request(request)
            return True

    def get_subscription(self, topic_name, subscription_name):
        '''
        Gets an existing subscription.

        topic_name:
            Name of the topic.
        subscription_name:
            Name of the subscription.
        '''
        _validate_not_none('topic_name', topic_name)
        _validate_not_none('subscription_name', subscription_name)
        request = HTTPRequest()
        request.method = 'GET'
        request.host = self._get_host()
        request.path = '/' + \
            _str(topic_name) + '/subscriptions/' + _str(subscription_name) + ''
        request.path, request.query = self._httpclient._update_request_uri_query(request)
        request.headers = self._update_service_bus_header(request)
        response = self._perform_request(request)

        return _convert_response_to_subscription(response)

    def list_subscriptions(self, topic_name):
        '''
        Retrieves the subscriptions in the specified topic.

        topic_name:
            Name of the topic.
        '''
        _validate_not_none('topic_name', topic_name)
        request = HTTPRequest()
        request.method = 'GET'
        request.host = self._get_host()
        request.path = '/' + _str(topic_name) + '/subscriptions/'
        request.path, request.query = self._httpclient._update_request_uri_query(request)
        request.headers = self._update_service_bus_header(request)
        response = self._perform_request(request)

        return _ETreeXmlToObject.convert_response_to_feeds(
            response, _convert_etree_element_to_subscription)

    def send_topic_message(self, topic_name, message=None):
        '''
        Enqueues a message into the specified topic. The limit to the number
        of messages which may be present in the topic is governed by the
        message size in MaxTopicSizeInBytes. If this message causes the topic
        to exceed its quota, a quota exceeded error is returned and the
        message will be rejected.

        topic_name:
            Name of the topic.
        message:
            Message object containing message body and properties.
        '''
        _validate_not_none('topic_name', topic_name)
        _validate_not_none('message', message)
        request = HTTPRequest()
        request.method = 'POST'
        request.host = self._get_host()
        request.path = '/' + _str(topic_name) + '/messages'
        request.headers = message.add_headers(request)
        request.body = _get_request_body(message.body)
        request.path, request.query = self._httpclient._update_request_uri_query(request)
        request.headers = self._update_service_bus_header(request)
        self._perform_request(request)

    def send_topic_message_batch(self, topic_name, messages=None):
        '''
        Sends a batch of messages into the specified topic. The limit to the number of
        messages which may be present in the topic is governed by the message
        size the MaxTopicSizeInMegaBytes. If this message will cause the topic
        to exceed its quota, a quota exceeded error is returned and the
        message will be rejected.

        topic_name:
            Name of the topic.
        messages:
            List of message objects containing message body and properties.
        '''
        _validate_not_none('topic_name', topic_name)
        _validate_not_none('messages', messages)
        request = HTTPRequest()
        request.method = 'POST'
        request.host = self._get_host()
        request.path = '/' + _str(topic_name) + '/messages'
        request.headers.append(('Content-Type', 'application/vnd.microsoft.servicebus.json'))
        request.body = _get_request_body(json.dumps([m.as_batch_body() for m in messages]))
        request.path, request.query = self._httpclient._update_request_uri_query(request)
        request.headers = self._update_service_bus_header(request)
        self._perform_request(request)

    def peek_lock_subscription_message(self, topic_name, subscription_name,
                                       timeout='60'):
        '''
        This operation is used to atomically retrieve and lock a message for
        processing. The message is guaranteed not to be delivered to other
        receivers during the lock duration period specified in buffer
        description. Once the lock expires, the message will be available to
        other receivers (on the same subscription only) during the lock
        duration period specified in the topic description. Once the lock
        expires, the message will be available to other receivers. In order to
        complete processing of the message, the receiver should issue a delete
        command with the lock ID received from this operation. To abandon
        processing of the message and unlock it for other receivers, an Unlock
        Message command should be issued, or the lock duration period can
        expire.

        topic_name:
            Name of the topic.
        subscription_name:
            Name of the subscription.
        timeout:
            Optional. The timeout parameter is expressed in seconds.
        '''
        _validate_not_none('topic_name', topic_name)
        _validate_not_none('subscription_name', subscription_name)
        request = HTTPRequest()
        request.method = 'POST'
        request.host = self._get_host()
        request.path = '/' + \
            _str(topic_name) + '/subscriptions/' + \
            _str(subscription_name) + '/messages/head'
        request.query = [('timeout', _int_or_none(timeout))]
        request.path, request.query = self._httpclient._update_request_uri_query(request)
        request.headers = self._update_service_bus_header(request)
        response = self._perform_request(request)

        return _create_message(response, self)

    def unlock_subscription_message(self, topic_name, subscription_name,
                                    sequence_number, lock_token):
        '''
        Unlock a message for processing by other receivers on a given
        subscription. This operation deletes the lock object, causing the
        message to be unlocked. A message must have first been locked by a
        receiver before this operation is called.

        topic_name:
            Name of the topic.
        subscription_name:
            Name of the subscription.
        sequence_number:
            The sequence number of the message to be unlocked as returned in
            BrokerProperties['SequenceNumber'] by the Peek Message operation.
        lock_token:
            The ID of the lock as returned by the Peek Message operation in
            BrokerProperties['LockToken']
        '''
        _validate_not_none('topic_name', topic_name)
        _validate_not_none('subscription_name', subscription_name)
        _validate_not_none('sequence_number', sequence_number)
        _validate_not_none('lock_token', lock_token)
        request = HTTPRequest()
        request.method = 'PUT'
        request.host = self._get_host()
        request.path = '/' + _str(topic_name) + \
                       '/subscriptions/' + str(subscription_name) + \
                       '/messages/' + _str(sequence_number) + \
                       '/' + _str(lock_token) + ''
        request.path, request.query = self._httpclient._update_request_uri_query(request)
        request.headers = self._update_service_bus_header(request)
        self._perform_request(request)

    def renew_lock_subscription_message(self, topic_name, subscription_name,
                                        sequence_number, lock_token):
        '''
        Renew the lock on an already locked message on a given
        subscription. A message must have first been locked by a
        receiver before this operation is called.

        topic_name:
            Name of the topic.
        subscription_name:
            Name of the subscription.
        sequence_number:
            The sequence number of the message to be unlocked as returned in
            BrokerProperties['SequenceNumber'] by the Peek Message operation.
        lock_token:
            The ID of the lock as returned by the Peek Message operation in
            BrokerProperties['LockToken']
        '''
        _validate_not_none('topic_name', topic_name)
        _validate_not_none('subscription_name', subscription_name)
        _validate_not_none('sequence_number', sequence_number)
        _validate_not_none('lock_token', lock_token)
        request = HTTPRequest()
        request.method = 'POST'
        request.host = self._get_host()
        request.path = '/' + _str(topic_name) + \
                       '/subscriptions/' + str(subscription_name) + \
                       '/messages/' + _str(sequence_number) + \
                       '/' + _str(lock_token) + ''
        request.path, request.query = self._httpclient._update_request_uri_query(request)
        request.headers = self._update_service_bus_header(request)
        self._perform_request(request)

    def read_delete_subscription_message(self, topic_name, subscription_name,
                                         timeout='60'):
        '''
        Read and delete a message from a subscription as an atomic operation.
        This operation should be used when a best-effort guarantee is
        sufficient for an application; that is, using this operation it is
        possible for messages to be lost if processing fails.

        topic_name:
            Name of the topic.
        subscription_name:
            Name of the subscription.
        timeout:
            Optional. The timeout parameter is expressed in seconds.
        '''
        _validate_not_none('topic_name', topic_name)
        _validate_not_none('subscription_name', subscription_name)
        request = HTTPRequest()
        request.method = 'DELETE'
        request.host = self._get_host()
        request.path = '/' + _str(topic_name) + \
                       '/subscriptions/' + _str(subscription_name) + \
                       '/messages/head'
        request.query = [('timeout', _int_or_none(timeout))]
        request.path, request.query = self._httpclient._update_request_uri_query(request)
        request.headers = self._update_service_bus_header(request)
        response = self._perform_request(request)

        return _create_message(response, self)

    def delete_subscription_message(self, topic_name, subscription_name,
                                    sequence_number, lock_token):
        '''
        Completes processing on a locked message and delete it from the
        subscription. This operation should only be called after processing a
        previously locked message is successful to maintain At-Least-Once
        delivery assurances.

        topic_name:
            Name of the topic.
        subscription_name:
            Name of the subscription.
        sequence_number:
            The sequence number of the message to be deleted as returned in
            BrokerProperties['SequenceNumber'] by the Peek Message operation.
        lock_token:
            The ID of the lock as returned by the Peek Message operation in
            BrokerProperties['LockToken']
        '''
        _validate_not_none('topic_name', topic_name)
        _validate_not_none('subscription_name', subscription_name)
        _validate_not_none('sequence_number', sequence_number)
        _validate_not_none('lock_token', lock_token)
        request = HTTPRequest()
        request.method = 'DELETE'
        request.host = self._get_host()
        request.path = '/' + _str(topic_name) + \
                       '/subscriptions/' + _str(subscription_name) + \
                       '/messages/' + _str(sequence_number) + \
                       '/' + _str(lock_token) + ''
        request.path, request.query = self._httpclient._update_request_uri_query(request)
        request.headers = self._update_service_bus_header(request)
        self._perform_request(request)

    def send_queue_message(self, queue_name, message=None):
        '''
        Sends a message into the specified queue. The limit to the number of
        messages which may be present in the queue is governed by the message
        size the MaxTopicSizeInMegaBytes. If this message will cause the queue
        to exceed its quota, a quota exceeded error is returned and the
        message will be rejected.

        queue_name:
            Name of the queue.
        message:
            Message object containing message body and properties.
        '''
        _validate_not_none('queue_name', queue_name)
        _validate_not_none('message', message)
        request = HTTPRequest()
        request.method = 'POST'
        request.host = self._get_host()
        request.path = '/' + _str(queue_name) + '/messages'
        request.headers = message.add_headers(request)
        request.body = _get_request_body(message.body)
        request.path, request.query = self._httpclient._update_request_uri_query(request)
        request.headers = self._update_service_bus_header(request)
        self._perform_request(request)

    def send_queue_message_batch(self, queue_name, messages=None):
        '''
        Sends a batch of messages into the specified queue. The limit to the number of
        messages which may be present in the topic is governed by the message
        size the MaxTopicSizeInMegaBytes. If this message will cause the queue
        to exceed its quota, a quota exceeded error is returned and the
        message will be rejected.

        queue_name:
            Name of the queue.
        messages:
            List of message objects containing message body and properties.
        '''
        _validate_not_none('queue_name', queue_name)
        _validate_not_none('messages', messages)
        request = HTTPRequest()
        request.method = 'POST'
        request.host = self._get_host()
        request.path = '/' + _str(queue_name) + '/messages'
        request.headers.append(('Content-Type', 'application/vnd.microsoft.servicebus.json'))
        request.body = _get_request_body(json.dumps([m.as_batch_body() for m in messages]))
        request.path, request.query = self._httpclient._update_request_uri_query(request)
        request.headers = self._update_service_bus_header(request)
        self._perform_request(request)

    def peek_lock_queue_message(self, queue_name, timeout='60'):
        '''
        Automically retrieves and locks a message from a queue for processing.
        The message is guaranteed not to be delivered to other receivers (on
        the same subscription only) during the lock duration period specified
        in the queue description. Once the lock expires, the message will be
        available to other receivers. In order to complete processing of the
        message, the receiver should issue a delete command with the lock ID
        received from this operation. To abandon processing of the message and
        unlock it for other receivers, an Unlock Message command should be
        issued, or the lock duration period can expire.

        queue_name:
            Name of the queue.
        timeout:
            Optional. The timeout parameter is expressed in seconds.
        '''
        _validate_not_none('queue_name', queue_name)
        request = HTTPRequest()
        request.method = 'POST'
        request.host = self._get_host()
        request.path = '/' + _str(queue_name) + '/messages/head'
        request.query = [('timeout', _int_or_none(timeout))]
        request.path, request.query = self._httpclient._update_request_uri_query(request)
        request.headers = self._update_service_bus_header(request)
        response = self._perform_request(request)

        return _create_message(response, self)

    def unlock_queue_message(self, queue_name, sequence_number, lock_token):
        '''
        Unlocks a message for processing by other receivers on a given
        queue. This operation deletes the lock object, causing the
        message to be unlocked. A message must have first been locked by a
        receiver before this operation is called.

        queue_name:
            Name of the queue.
        sequence_number:
            The sequence number of the message to be unlocked as returned in
            BrokerProperties['SequenceNumber'] by the Peek Message operation.
        lock_token:
            The ID of the lock as returned by the Peek Message operation in
            BrokerProperties['LockToken']
        '''
        _validate_not_none('queue_name', queue_name)
        _validate_not_none('sequence_number', sequence_number)
        _validate_not_none('lock_token', lock_token)
        request = HTTPRequest()
        request.method = 'PUT'
        request.host = self._get_host()
        request.path = '/' + _str(queue_name) + \
                       '/messages/' + _str(sequence_number) + \
                       '/' + _str(lock_token) + ''
        request.path, request.query = self._httpclient._update_request_uri_query(request)
        request.headers = self._update_service_bus_header(request)
        self._perform_request(request)

    def renew_lock_queue_message(self, queue_name, sequence_number, lock_token):
        '''
        Renew lock on an already locked message on a given
        queue. A message must have first been locked by a
        receiver before this operation is called.

        queue_name:
            Name of the queue.
        sequence_number:
            The sequence number of the message to be unlocked as returned in
            BrokerProperties['SequenceNumber'] by the Peek Message operation.
        lock_token:
            The ID of the lock as returned by the Peek Message operation in
            BrokerProperties['LockToken']
        '''
        _validate_not_none('queue_name', queue_name)
        _validate_not_none('sequence_number', sequence_number)
        _validate_not_none('lock_token', lock_token)
        request = HTTPRequest()
        request.method = 'POST'
        request.host = self._get_host()
        request.path = '/' + _str(queue_name) + \
                       '/messages/' + _str(sequence_number) + \
                       '/' + _str(lock_token) + ''
        request.path, request.query = self._httpclient._update_request_uri_query(request)
        request.headers = self._update_service_bus_header(request)
        self._perform_request(request)

    def read_delete_queue_message(self, queue_name, timeout='60'):
        '''
        Reads and deletes a message from a queue as an atomic operation. This
        operation should be used when a best-effort guarantee is sufficient
        for an application; that is, using this operation it is possible for
        messages to be lost if processing fails.

        queue_name:
            Name of the queue.
        timeout:
            Optional. The timeout parameter is expressed in seconds.
        '''
        _validate_not_none('queue_name', queue_name)
        request = HTTPRequest()
        request.method = 'DELETE'
        request.host = self._get_host()
        request.path = '/' + _str(queue_name) + '/messages/head'
        request.query = [('timeout', _int_or_none(timeout))]
        request.path, request.query = self._httpclient._update_request_uri_query(request)
        request.headers = self._update_service_bus_header(request)
        response = self._perform_request(request)

        return _create_message(response, self)

    def delete_queue_message(self, queue_name, sequence_number, lock_token):
        '''
        Completes processing on a locked message and delete it from the queue.
        This operation should only be called after processing a previously
        locked message is successful to maintain At-Least-Once delivery
        assurances.

        queue_name:
            Name of the queue.
        sequence_number:
            The sequence number of the message to be deleted as returned in
            BrokerProperties['SequenceNumber'] by the Peek Message operation.
        lock_token:
            The ID of the lock as returned by the Peek Message operation in
            BrokerProperties['LockToken']
        '''
        _validate_not_none('queue_name', queue_name)
        _validate_not_none('sequence_number', sequence_number)
        _validate_not_none('lock_token', lock_token)
        request = HTTPRequest()
        request.method = 'DELETE'
        request.host = self._get_host()
        request.path = '/' + _str(queue_name) + \
                       '/messages/' + _str(sequence_number) + \
                       '/' + _str(lock_token) + ''
        request.path, request.query = self._httpclient._update_request_uri_query(request)
        request.headers = self._update_service_bus_header(request)
        self._perform_request(request)

    def receive_queue_message(self, queue_name, peek_lock=True, timeout=60):
        '''
        Receive a message from a queue for processing.

        queue_name:
            Name of the queue.
        peek_lock:
            Optional. True to retrieve and lock the message. False to read and
            delete the message. Default is True (lock).
        timeout:
            Optional. The timeout parameter is expressed in seconds.
        '''
        if peek_lock:
            return self.peek_lock_queue_message(queue_name, timeout)
        else:
            return self.read_delete_queue_message(queue_name, timeout)

    def receive_subscription_message(self, topic_name, subscription_name,
                                     peek_lock=True, timeout=60):
        '''
        Receive a message from a subscription for processing.

        topic_name:
            Name of the topic.
        subscription_name:
            Name of the subscription.
        peek_lock:
            Optional. True to retrieve and lock the message. False to read and
            delete the message. Default is True (lock).
        timeout:
            Optional. The timeout parameter is expressed in seconds.
        '''
        if peek_lock:
            return self.peek_lock_subscription_message(topic_name,
                                                       subscription_name,
                                                       timeout)
        else:
            return self.read_delete_subscription_message(topic_name,
                                                         subscription_name,
                                                         timeout)

    def create_event_hub(self, hub_name, hub=None, fail_on_exist=False):
        '''
        Creates a new Event Hub.

        hub_name:
            Name of event hub.
        hub:
            Optional. Event hub properties. Instance of EventHub class.
        hub.message_retention_in_days:
            Number of days to retain the events for this Event Hub.
        hub.status: Status of the Event Hub (enabled or disabled).
        hub.user_metadata: User metadata.
        hub.partition_count: Number of shards on the Event Hub.
        fail_on_exist:
            Specify whether to throw an exception when the event hub exists.
        '''
        _validate_not_none('hub_name', hub_name)
        request = HTTPRequest()
        request.method = 'PUT'
        request.host = self._get_host()
        request.path = '/' + _str(hub_name) + '?api-version=2014-01'
        request.body = _get_request_body(_convert_event_hub_to_xml(hub))
        request.path, request.query = self._httpclient._update_request_uri_query(request)
        request.headers = self._update_service_bus_header(request)
        if not fail_on_exist:
            try:
                self._perform_request(request)
                return True
            except AzureHttpError as ex:
                _dont_fail_on_exist(ex)
                return False
        else:
            self._perform_request(request)
            return True

    def update_event_hub(self, hub_name, hub=None):
        '''
        Updates an Event Hub.

        hub_name:
            Name of event hub.
        hub:
            Optional. Event hub properties. Instance of EventHub class.
        hub.message_retention_in_days:
            Number of days to retain the events for this Event Hub.
        '''
        _validate_not_none('hub_name', hub_name)
        request = HTTPRequest()
        request.method = 'PUT'
        request.host = self._get_host()
        request.path = '/' + _str(hub_name) + '?api-version=2014-01'
        request.body = _get_request_body(_convert_event_hub_to_xml(hub))
        request.path, request.query = self._httpclient._update_request_uri_query(request)
        request.headers.append(('If-Match', '*'))
        request.headers = self._update_service_bus_header(request)
        response = self._perform_request(request)

        return _convert_response_to_event_hub(response)

    def delete_event_hub(self, hub_name, fail_not_exist=False):
        '''
        Deletes an Event Hub. This operation will also remove all associated
        state.

        hub_name:
            Name of the event hub to delete.
        fail_not_exist:
            Specify whether to throw an exception if the event hub doesn't exist.
        '''
        _validate_not_none('hub_name', hub_name)
        request = HTTPRequest()
        request.method = 'DELETE'
        request.host = self._get_host()
        request.path = '/' + _str(hub_name) + '?api-version=2014-01'
        request.path, request.query = self._httpclient._update_request_uri_query(request)
        request.headers = self._update_service_bus_header(request)
        if not fail_not_exist:
            try:
                self._perform_request(request)
                return True
            except AzureHttpError as ex:
                _dont_fail_not_exist(ex)
                return False
        else:
            self._perform_request(request)
            return True

    def get_event_hub(self, hub_name):
        '''
        Retrieves an existing event hub.

        hub_name:
            Name of the event hub.
        '''
        _validate_not_none('hub_name', hub_name)
        request = HTTPRequest()
        request.method = 'GET'
        request.host = self._get_host()
        request.path = '/' + _str(hub_name) + ''
        request.path, request.query = self._httpclient._update_request_uri_query(request)
        request.headers = self._update_service_bus_header(request)
        response = self._perform_request(request)

        return _convert_response_to_event_hub(response)

    def send_event(self, hub_name, message, device_id=None,
                   broker_properties=None):
        '''
        Sends a new message event to an Event Hub.
        '''
        _validate_not_none('hub_name', hub_name)
        request = HTTPRequest()
        request.method = 'POST'
        request.host = self._get_host()
        if device_id:
            request.path = '/{0}/publishers/{1}/messages?api-version=2014-01'.format(hub_name, device_id)
        else:
            request.path = '/{0}/messages?api-version=2014-01'.format(hub_name)
        if broker_properties:
            request.headers.append(
                ('BrokerProperties', str(broker_properties)))
        request.body = _get_request_body(message)
        request.path, request.query = self._httpclient._update_request_uri_query(request)
        request.headers = self._update_service_bus_header(request)
        self._perform_request(request)

    def _get_host(self):
        return self.service_namespace + self.host_base

    def _perform_request(self, request):
        try:
            resp = self._filter(request)
        except HTTPError as ex:
            return _service_bus_error_handler(ex)

        return resp

    def _update_service_bus_header(self, request):
        ''' Add additional headers for service bus. '''

        if request.method in ['PUT', 'POST', 'MERGE', 'DELETE']:
            request.headers.append(('Content-Length', str(len(request.body))))

        # if it is not GET or HEAD request, must set content-type.
        if not request.method in ['GET', 'HEAD']:
            for name, _ in request.headers:
                if 'content-type' == name.lower():
                    break
            else:
                request.headers.append(
                    ('Content-Type',
                     'application/atom+xml;type=entry;charset=utf-8'))

        # Adds authorization header for authentication.
        self.authentication.sign_request(request, self._httpclient)

        return request.headers


# Token cache for Authentication
# Shared by the different instances of ServiceBusWrapTokenAuthentication
_tokens = {}


class ServiceBusWrapTokenAuthentication:
    def __init__(self, account_key, issuer):
        self.account_key = account_key
        self.issuer = issuer

    def sign_request(self, request, httpclient):
        request.headers.append(
            ('Authorization', self._get_authorization(request, httpclient)))

    def _get_authorization(self, request, httpclient):
        ''' return the signed string with token. '''
        return 'WRAP access_token="' + \
                self._get_token(request.host, request.path, httpclient) + '"'

    def _token_is_expired(self, token):
        ''' Check if token expires or not. '''
        time_pos_begin = token.find('ExpiresOn=') + len('ExpiresOn=')
        time_pos_end = token.find('&', time_pos_begin)
        token_expire_time = int(token[time_pos_begin:time_pos_end])
        time_now = time.mktime(time.localtime())

        # Adding 30 seconds so the token wouldn't be expired when we send the
        # token to server.
        return (token_expire_time - time_now) < 30

    def _get_token(self, host, path, httpclient):
        '''
        Returns token for the request.

        host:
            the service bus service request.
        path:
            the service bus service request.
        '''
        wrap_scope = 'http://' + host + path + self.issuer + self.account_key

        # Check whether has unexpired cache, return cached token if it is still
        # usable.
        if wrap_scope in _tokens:
            token = _tokens[wrap_scope]
            if not self._token_is_expired(token):
                return token

        # get token from accessconstrol server
        request = HTTPRequest()
        request.protocol_override = 'https'
        request.host = host.replace('.servicebus.', '-sb.accesscontrol.')
        request.method = 'POST'
        request.path = '/WRAPv0.9'
        request.body = ('wrap_name=' + url_quote(self.issuer) +
                        '&wrap_password=' + url_quote(self.account_key) +
                        '&wrap_scope=' +
                        url_quote('http://' + host + path)).encode('utf-8')
        request.headers.append(('Content-Length', str(len(request.body))))
        resp = httpclient.perform_request(request)

        token = resp.body.decode('utf-8-sig')
        token = url_unquote(token[token.find('=') + 1:token.rfind('&')])
        _tokens[wrap_scope] = token

        return token


class ServiceBusSASAuthentication:
    def __init__(self, key_name, key_value):
        self.key_name = key_name
        self.key_value = key_value

    def sign_request(self, request, httpclient):
        request.headers.append(
            ('Authorization', self._get_authorization(request, httpclient)))

    def _get_authorization(self, request, httpclient):
        uri = httpclient.get_uri(request)
        uri = url_quote(uri, '').lower()
        expiry = str(self._get_expiry())

        to_sign = uri + '\n' + expiry
        signature = url_quote(_sign_string(self.key_value, to_sign, False), '')

        auth_format = 'SharedAccessSignature sig={0}&se={1}&skn={2}&sr={3}'
        auth = auth_format.format(signature, expiry, self.key_name, uri)

        return auth

    def _get_expiry(self):
        '''Returns the UTC datetime, in seconds since Epoch, when this signed 
        request expires (5 minutes from now).'''
        return int(round(time.time() + 300))

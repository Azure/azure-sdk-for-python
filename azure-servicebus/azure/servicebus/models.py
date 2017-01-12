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
import sys
import json

from datetime import datetime
from azure.common import (
    AzureException,
)
from ._common_models import (
    WindowsAzureData,
)
from ._common_error import (
    _ERROR_MESSAGE_NOT_PEEK_LOCKED_ON_DELETE,
    _ERROR_MESSAGE_NOT_PEEK_LOCKED_ON_UNLOCK,
    _ERROR_MESSAGE_NOT_PEEK_LOCKED_ON_RENEW_LOCK,
)

from ._common_serialization import _get_request_body

class AzureServiceBusPeekLockError(AzureException):
    '''Indicates that peek-lock is required for this operation.'''


class AzureServiceBusResourceNotFound(AzureException):
    '''Indicates that the resource doesn't exist.'''


class Queue(WindowsAzureData):

    ''' Queue class corresponding to Queue Description:
    http://msdn.microsoft.com/en-us/library/windowsazure/hh780773'''

    def __init__(self, lock_duration=None, max_size_in_megabytes=None,
                 requires_duplicate_detection=None, requires_session=None,
                 default_message_time_to_live=None,
                 dead_lettering_on_message_expiration=None,
                 duplicate_detection_history_time_window=None,
                 max_delivery_count=None, enable_batched_operations=None,
                 size_in_bytes=None, message_count=None):

        self.lock_duration = lock_duration
        self.max_size_in_megabytes = max_size_in_megabytes
        self.requires_duplicate_detection = requires_duplicate_detection
        self.requires_session = requires_session
        self.default_message_time_to_live = default_message_time_to_live
        self.dead_lettering_on_message_expiration = \
            dead_lettering_on_message_expiration
        self.duplicate_detection_history_time_window = \
            duplicate_detection_history_time_window
        self.max_delivery_count = max_delivery_count
        self.enable_batched_operations = enable_batched_operations
        self.size_in_bytes = size_in_bytes
        self.message_count = message_count


class Topic(WindowsAzureData):

    ''' Topic class corresponding to Topic Description:
    http://msdn.microsoft.com/en-us/library/windowsazure/hh780749. '''

    def __init__(self, default_message_time_to_live=None,
                 max_size_in_megabytes=None, requires_duplicate_detection=None,
                 duplicate_detection_history_time_window=None,
                 enable_batched_operations=None, size_in_bytes=None):

        self.default_message_time_to_live = default_message_time_to_live
        self.max_size_in_megabytes = max_size_in_megabytes
        self.requires_duplicate_detection = requires_duplicate_detection
        self.duplicate_detection_history_time_window = \
            duplicate_detection_history_time_window
        self.enable_batched_operations = enable_batched_operations
        self.size_in_bytes = size_in_bytes

    @property
    def max_size_in_mega_bytes(self):
        import warnings
        warnings.warn(
            'This attribute has been changed to max_size_in_megabytes.')
        return self.max_size_in_megabytes

    @max_size_in_mega_bytes.setter
    def max_size_in_mega_bytes(self, value):
        self.max_size_in_megabytes = value


class Subscription(WindowsAzureData):

    ''' Subscription class corresponding to Subscription Description:
    http://msdn.microsoft.com/en-us/library/windowsazure/hh780763. '''

    def __init__(self, lock_duration=None, requires_session=None,
                 default_message_time_to_live=None,
                 dead_lettering_on_message_expiration=None,
                 dead_lettering_on_filter_evaluation_exceptions=None,
                 enable_batched_operations=None, max_delivery_count=None,
                 message_count=None):

        self.lock_duration = lock_duration
        self.requires_session = requires_session
        self.default_message_time_to_live = default_message_time_to_live
        self.dead_lettering_on_message_expiration = \
            dead_lettering_on_message_expiration
        self.dead_lettering_on_filter_evaluation_exceptions = \
            dead_lettering_on_filter_evaluation_exceptions
        self.enable_batched_operations = enable_batched_operations
        self.max_delivery_count = max_delivery_count
        self.message_count = message_count


class Rule(WindowsAzureData):

    ''' Rule class corresponding to Rule Description:
    http://msdn.microsoft.com/en-us/library/windowsazure/hh780753. '''

    def __init__(self, filter_type=None, filter_expression=None,
                 action_type=None, action_expression=None):
        self.filter_type = filter_type
        self.filter_expression = filter_expression
        self.action_type = action_type
        self.action_expression = action_type


class EventHub(WindowsAzureData):

    def __init__(self, message_retention_in_days=None, status=None,
                 user_metadata=None, partition_count=None):
        self.message_retention_in_days = message_retention_in_days
        self.status = status
        self.user_metadata = user_metadata
        self.partition_count = partition_count
        self.authorization_rules = []
        self.partition_ids = []


class AuthorizationRule(WindowsAzureData):

    def __init__(self, claim_type=None, claim_value=None, rights=None,
                 key_name=None, primary_key=None, secondary_key=None):
        self.claim_type = claim_type
        self.claim_value = claim_value
        self.rights = rights or []
        self.created_time = None
        self.modified_time = None
        self.key_name = key_name
        self.primary_key = primary_key
        self.secondary_key = secondary_key


class Message(WindowsAzureData):

    ''' Message class that used in send message/get mesage apis. '''

    def __init__(self, body=None, service_bus_service=None, location=None,
                 custom_properties=None,
                 type='application/atom+xml;type=entry;charset=utf-8',
                 broker_properties=None):
        self.body = body
        self.location = location
        self.broker_properties = broker_properties
        self.custom_properties = custom_properties
        self.type = type
        self.service_bus_service = service_bus_service
        self._topic_name = None
        self._subscription_name = None
        self._queue_name = None

        if not service_bus_service:
            return

        # if location is set, then extracts the queue name for queue message and
        # extracts the topic and subscriptions name if it is topic message.
        if location:
            if '/subscriptions/' in location:
                pos = location.find(service_bus_service.host_base.lower())+1
                pos1 = location.find('/subscriptions/')
                self._topic_name = location[pos+len(service_bus_service.host_base):pos1]
                pos = pos1 + len('/subscriptions/')
                pos1 = location.find('/', pos)
                self._subscription_name = location[pos:pos1]
            elif '/messages/' in location:
                pos = location.find(service_bus_service.host_base.lower())+1
                pos1 = location.find('/messages/')
                self._queue_name = location[pos+len(service_bus_service.host_base):pos1]

    def delete(self):
        ''' Deletes itself if find queue name or topic name and subscription
        name. '''
        if self._queue_name:
            self.service_bus_service.delete_queue_message(
                self._queue_name,
                self.broker_properties['SequenceNumber'],
                self.broker_properties['LockToken'])
        elif self._topic_name and self._subscription_name:
            self.service_bus_service.delete_subscription_message(
                self._topic_name,
                self._subscription_name,
                self.broker_properties['SequenceNumber'],
                self.broker_properties['LockToken'])
        else:
            raise AzureServiceBusPeekLockError(_ERROR_MESSAGE_NOT_PEEK_LOCKED_ON_DELETE)

    def unlock(self):
        ''' Unlocks itself if find queue name or topic name and subscription
        name. '''
        if self._queue_name:
            self.service_bus_service.unlock_queue_message(
                self._queue_name,
                self.broker_properties['SequenceNumber'],
                self.broker_properties['LockToken'])
        elif self._topic_name and self._subscription_name:
            self.service_bus_service.unlock_subscription_message(
                self._topic_name,
                self._subscription_name,
                self.broker_properties['SequenceNumber'],
                self.broker_properties['LockToken'])
        else:
            raise AzureServiceBusPeekLockError(_ERROR_MESSAGE_NOT_PEEK_LOCKED_ON_UNLOCK)

    def renew_lock(self):
        ''' Renew lock on itself if find queue name or topic name and subscription
        name. '''
        if self._queue_name:
            self.service_bus_service.renew_lock_queue_message(
                self._queue_name,
                self.broker_properties['SequenceNumber'],
                self.broker_properties['LockToken'])
        elif self._topic_name and self._subscription_name:
            self.service_bus_service.renew_lock_subscription_message(
                self._topic_name,
                self._subscription_name,
                self.broker_properties['SequenceNumber'],
                self.broker_properties['LockToken'])
        else:
            raise AzureServiceBusPeekLockError(_ERROR_MESSAGE_NOT_PEEK_LOCKED_ON_RENEW_LOCK)

    def _serialize_escaped_properties_value(self, value):
        if sys.version_info < (3,) and isinstance(value, unicode):
            escaped_value = value.replace('"', '\\"')
            return '"' + escaped_value.encode('utf-8') + '"'
        elif isinstance(value, str):
            escaped_value = value.replace('"', '\\"')
            return '"' + escaped_value + '"'
        elif isinstance(value, datetime):
            return '"' + value.strftime('%a, %d %b %Y %H:%M:%S GMT') + '"'
        else:
            return str(value).lower()

    def _serialize_basic_properties_value(self, value):
        if sys.version_info < (3,) and isinstance(value, unicode):
            return value.encode('utf-8')
        elif isinstance(value, str):
            return value
        elif isinstance(value, datetime):
            return value.strftime('%a, %d %b %Y %H:%M:%S GMT')
        else:
            return str(value).lower()

    def add_headers(self, request):
        ''' add addtional headers to request for message request.'''

        # Adds custom properties
        if self.custom_properties:
            for name, value in self.custom_properties.items():
                request.headers.append((name, self._serialize_escaped_properties_value(value)))

        # Adds content-type
        request.headers.append(('Content-Type', self.type))

        # Adds BrokerProperties
        if self.broker_properties:
            if hasattr(self.broker_properties, 'items'):
                broker_properties = {name: self._serialize_basic_properties_value(value) 
                                     for name, value 
                                     in self.broker_properties.items()}
                broker_properties = json.dumps(broker_properties)
            else:
                broker_properties = self.broker_properties
            request.headers.append(
                ('BrokerProperties', str(broker_properties)))

        return request.headers

    def as_batch_body(self):
        ''' return the current message as expected by batch body format'''
        if sys.version_info >= (3,) and isinstance(self.body, bytes):
            # It HAS to be string to be serialized in JSON
            body = self.body.decode('utf-8')
        else:
            # Python 2.7 people handle this themself
            body = self.body
        result = {'Body': body}

        # Adds custom properties
        if self.custom_properties:
            result['UserProperties'] = {name: self._serialize_basic_properties_value(value) 
                                        for name, value 
                                        in self.custom_properties.items()}

        # Adds BrokerProperties
        if self.broker_properties:
            result['BrokerProperties'] = {name: self._serialize_basic_properties_value(value) 
                                          for name, value 
                                          in self.broker_properties.items()}

        return result

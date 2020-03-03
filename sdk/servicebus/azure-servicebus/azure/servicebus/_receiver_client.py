# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import time
import datetime
import logging
import functools
import uuid

from uamqp import ReceiveClient, Source, types

from ._client_base import ClientBase
from .common.utils import create_properties
from .common.message import Message
from .common.constants import (
    REQUEST_RESPONSE_RECEIVE_BY_SEQUENCE_NUMBER,
    REQUEST_RESPONSE_UPDATE_DISPOSTION_OPERATION,
    ReceiveSettleMode,
    NEXT_AVAILABLE,
    SESSION_LOCKED_UNTIL,
    DATETIMEOFFSET_EPOCH,
    SESSION_FILTER,
)
from .common.errors import _ServiceBusErrorPolicy
from .common import mgmt_handlers

_LOGGER = logging.getLogger(__name__)


class ReceiverMixin(object):
    def _create_attribute(self, **kwargs):
        if kwargs.get("subscription_name"):
            self.subscription_name = kwargs.get("subscription_name")
            self._is_subscription = True
            self._entity_path = self._entity_name + "/Subscriptions/" + self.subscription_name
        else:
            self._entity_path = self._entity_name

        self._session_id = kwargs.get("session_id")
        self._auth_uri = "sb://{}/{}".format(self.fully_qualified_namespace, self._entity_path)
        self._entity_uri = "amqps://{}/{}".format(self.fully_qualified_namespace, self._entity_path)
        self._mode = kwargs.get("mode", ReceiveSettleMode.PeekLock)
        self._error_policy = _ServiceBusErrorPolicy(
            max_retries=self._config.retry_total,
            is_session=(True if self._session_id else False)
        )
        self._name = "SBReceiver-{}".format(uuid.uuid4())

    def _build_message(self, received, message_type=Message):
        message = message_type(None, message=received)
        message._receiver = self  # pylint: disable=protected-access
        self._last_received_sequenced_number = message.sequence_number
        return message

    def _get_source_for_session_entity(self):
        source = Source(self._entity_uri)
        session_filter = None if self._session_id == NEXT_AVAILABLE else self._session_id
        source.set_filter(session_filter, name=SESSION_FILTER, descriptor=None)
        return source

    def _on_attach_for_session_entity(self, source, target, properties, error):  # pylint: disable=unused-argument
        if str(source) == self._entity_uri:
            self._session_start = datetime.datetime.now()
            expiry_in_seconds = properties.get(SESSION_LOCKED_UNTIL)
            if expiry_in_seconds:
                expiry_in_seconds = (expiry_in_seconds - DATETIMEOFFSET_EPOCH)/10000000
                self._locked_until = datetime.datetime.fromtimestamp(expiry_in_seconds)
            session_filter = source.get_filter(name=SESSION_FILTER)
            self._session_id = session_filter.decode(self._config.encoding)


class ServiceBusReceiverClient(ClientBase, ReceiverMixin):
    def __init__(
        self,
        fully_qualified_namespace,
        credential,
        **kwargs
    ):
        # type: (str, TokenCredential, Any) -> None
        if kwargs.get("from_connection_str", False):
            super(ServiceBusReceiverClient, self).__init__(
                fully_qualified_namespace=fully_qualified_namespace,
                credential=credential,
                **kwargs
            )
        else:
            queue_name = kwargs.get("queue_name")
            topic_name = kwargs.get("topic_name")
            subscription_name = kwargs.get("subscription_name")
            if queue_name and topic_name:
                raise ValueError("Queue/Topic name can not be specified simultaneously.")
            if not (queue_name or topic_name):
                raise ValueError("Queue/Topic name is missing. Please specify queue_name/topic_name.")
            if topic_name and not subscription_name:
                raise ValueError("Subscription name is missing for the topic. Please specify subscription_name.")

            entity_name = queue_name or topic_name

            super(ServiceBusReceiverClient, self).__init__(
                fully_qualified_namespace=fully_qualified_namespace,
                credential=credential,
                entity_name=entity_name,
                **kwargs
            )
        self._create_attribute(**kwargs)

    def __iter__(self):
        return self

    def __next__(self):
        while True:
            try:
                self._open()
                uamqp_message = next(self._message_iter)
                message = self._build_message(uamqp_message)
                return message
            except StopIteration:
                raise
            except Exception as e:  # pylint: disable=broad-except
                self._handle_exception(e)

    next = __next__  # for python2.7

    def _create_handler(self, auth):
        properties = create_properties()
        if not self._session_id:
            self._handler = ReceiveClient(
                self._entity_uri,
                auth=auth,
                debug=self._config.logging_enable,
                properties=properties,
                error_policy=self._error_policy,
                client_name=self._name,
                auto_complete=False,
                encoding=self._config.encoding,
                receive_settle_mode=self._mode.value
            )
        else:
            self._handler = ReceiveClient(
                self._get_source_for_session_entity(),
                auth=auth,
                debug=self._config.logging_enable,
                properties=properties,
                error_policy=self._error_policy,
                client_name=self._name,
                on_attach=self._on_attach_for_session_entity,
                auto_complete=False,
                encoding=self._config.encoding,
                receive_settle_mode=self._mode.value
            )

    def _open(self):
        if self._running:
            return
        if self._handler:
            self._handler.close()
        try:
            auth = self._create_auth()
            self._create_handler(auth)
            self._handler.open()
            self._message_iter = self._handler.receive_messages_iter()
            while not self._handler.client_ready():
                time.sleep(0.05)
        except Exception as e:  # pylint: disable=broad-except
            try:
                self._handle_exception(e)
            except Exception:
                self.running = False
                raise
        self._running = True

    def _receive(self, max_batch_size=None, timeout=None):
        self._open()
        wrapped_batch = []
        max_batch_size = max_batch_size or self._handler._prefetch  # pylint: disable=protected-access

        timeout_ms = 1000 * timeout if timeout else 0
        batch = self._handler.receive_message_batch(
            max_batch_size=max_batch_size,
            timeout=timeout_ms
        )
        for received in batch:
            message = self._build_message(received)
            wrapped_batch.append(message)

        return wrapped_batch

    def _settle_deferred(self, settlement, lock_tokens, dead_letter_details=None):
        message = {
            'disposition-status': settlement,
            'lock-tokens': types.AMQPArray(lock_tokens)}
        if dead_letter_details:
            message.update(dead_letter_details)
        return self._mgmt_request_response(
            REQUEST_RESPONSE_UPDATE_DISPOSTION_OPERATION,
            message,
            mgmt_handlers.default)

    def close(self, exception=None):
        if not self._running:
            return
        self._running = False
        super(ServiceBusReceiverClient, self).close(exception=exception)

    @classmethod
    def from_connection_string(
        cls,
        conn_str,
        **kwargs,
    ):
        # type: (str, Any) -> ServiceBusReceiverClient
        constructor_args = cls._from_connection_string(
            conn_str,
            **kwargs
        )
        if kwargs.get("queue_name") and kwargs.get("subscription_name"):
            raise ValueError("Queue entity does not have subscription.")

        if kwargs.get("topic_name") and not kwargs.get("subscription_name"):
            raise ValueError("Subscription name is missing for the topic. Please specify subscription_name.")
        return cls(**constructor_args)

    def receive(self, max_batch_size=None, timeout=None):
        # type: (int, float) -> List[ReceivedMessage]
        return self._do_retryable_operation(
            self._receive,
            max_batch_size=max_batch_size,
            timeout=timeout,
            require_timeout=True
        )

    def receive_deferred_messages(self, sequence_numbers):
        # type: (List[int]) -> List[DeferredMessage]
        if not sequence_numbers:
            raise ValueError("At least one sequence number must be specified.")
        self._open()
        try:
            receive_mode = self._mode.value.value
        except AttributeError:
            receive_mode = int(self._mode)
        message = {
            'sequence-numbers': types.AMQPArray([types.AMQPLong(s) for s in sequence_numbers]),
            'receiver-settle-mode': types.AMQPuInt(receive_mode),
            'session-id': self._session_id
        }
        handler = functools.partial(mgmt_handlers.deferred_message_op, mode=receive_mode)
        messages = self._mgmt_request_response(
            REQUEST_RESPONSE_RECEIVE_BY_SEQUENCE_NUMBER,
            message,
            handler)
        for m in messages:
            m._receiver = self  # pylint: disable=protected-access
        return messages

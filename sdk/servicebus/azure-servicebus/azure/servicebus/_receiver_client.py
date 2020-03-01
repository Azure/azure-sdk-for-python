# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import time
import logging

from uamqp import ReceiveClient, Message

from ._client_base import ClientBase, SenderReceiverMixin
from .common.utils import create_properties


_LOGGER = logging.getLogger(__name__)


class ServiceBusReceiverClient(ClientBase, SenderReceiverMixin):
    def __init__(
        self,
        fully_qualified_namespace,
        entity_name,
        credential,
        **kwargs
    ):
        # type: (str, str, TokenCredential, Any) -> None
        super(ServiceBusReceiverClient, self).__init__(
            fully_qualified_namespace=fully_qualified_namespace,
            credential=credential,
            entity_name=entity_name,
            **kwargs
        )
        self._create_attribute_for_receiver(entity_name, **kwargs)

    def __iter__(self):
        return self

    def __next__(self):
        while True:
            try:
                self._open()
                uamqp_message = next(self._message_iter)
                message = self._receiver_build_message(uamqp_message)
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
                self._receiver_get_source_for_session_entity(),
                auth=auth,
                debug=self._config.logging_enable,
                properties=properties,
                error_policy=self._error_policy,
                client_name=self._name,
                on_attach=self._receiver_on_attach_for_session_entity,
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
            message = self._receiver_build_message(received)
            wrapped_batch.append(message)

        return wrapped_batch

    def close(self, exception=None):
        if not self._running:
            return
        self._running = False
        super(ServiceBusReceiverClient, self).close(exception=exception)

    @classmethod
    def from_queue(
        cls,
        fully_qualified_namespace,
        queue_name,
        credential,
        **kwargs
    ):
        # type: (str, str, TokenCredential, Any) -> ServiceBusReceiverClient
        return cls(
            fully_qualified_namespace=fully_qualified_namespace,
            entity_name=queue_name,
            credential=credential,
            **kwargs
        )

    @classmethod
    def from_topic_subscription(
        cls,
        fully_qualified_namespace,
        topic_name,
        subscription_name,
        credential,
        **kwargs
    ):
        # type: (str, str, str, TokenCredential, Any) -> ServiceBusReceiverClient
        return cls(
            fully_qualified_namespace=fully_qualified_namespace,
            entity_name=topic_name,
            subscription_name=subscription_name,
            credential=credential,
            **kwargs
        )

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
        return cls(**constructor_args)

    def receive(self, max_batch_size=None, timeout=None):
        # type: (int, float) -> List[ReceivedMessage]
        return self._do_retryable_operation(
            self._receive,
            max_batch_size=max_batch_size,
            timeout=timeout,
            require_need_timeout=True
        )

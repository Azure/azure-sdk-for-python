# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import uuid
import logging
import time

from uamqp import SendClient

from ._client_base import ClientBase
from .common.errors import (
    _ServiceBusErrorPolicy,
    OperationTimeoutError,
    MessageSendFailed
)
from .common.utils import create_properties

_LOGGER = logging.getLogger(__name__)


class ServiceBusSenderClient(ClientBase):
    def __init__(
        self,
        fully_qualified_namespace,
        entity_name,
        credential,
        ** kwargs
    ):
        # type: (str, str, TokenCredential, Any) -> None
        super(ServiceBusSenderClient, self).__init__(
            fully_qualified_namespace=fully_qualified_namespace,
            credential=credential,
            entity_name=entity_name,
            **kwargs
        )

        self._entity_path = entity_name
        self._auth_uri = "sb://{}/{}".format(self.fully_qualified_namespace, self._entity_path)
        self._entity_uri = "amqps://{}/{}".format(self.fully_qualified_namespace, self._entity_path)
        self._logging_enable = self._config.logging_enable
        self._error_policy = _ServiceBusErrorPolicy(max_retries=self._config.retry_total)
        self._error = None
        self._name = "SBReceiver-{}".format(uuid.uuid4())

    def _create_handler(self):
        auth = self._create_auth()
        properties = create_properties()
        self._handler = SendClient(
            self._entity_uri,
            auth=auth,
            debug=self._logging_enable,
            properties=properties,
            error_policy=self._error_policy,
            client_name=self._name,
            encoding=self._config.encoding
        )

    def _open(self):
        if self._running:
            return
        if self._handler:
            self._handler.close()
        try:
            self._create_handler()
            self._handler.open()
            while not self._handler.client_ready():
                time.sleep(0.05)
        except Exception as e:  # pylint: disable=broad-except
            try:
                self._handle_exception(e)
            except Exception:
                self._running = False
                raise
        self._running = True

    def _reconnect(self):
        """Reconnect the handler.

        If the handler was disconnected from the service with
        a retryable error - attempt to reconnect.
        This method will be called automatically for most retryable errors.
        Also attempts to re-queue any messages that were pending before the reconnect.
        """
        unsent_events = self._handler.pending_messages
        super(ServiceBusSenderClient, self)._reconnect()
        try:
            self._handler.queue_message(*unsent_events)
            self._handler.wait()
        except Exception as e:  # pylint: disable=broad-except
            self._handle_exception(e)

    def _set_msg_timeout(self, timeout=None, last_exception=None):
        # type: (Optional[float], Optional[Exception]) -> None
        if not timeout:
            return
        timeout_time = time.time() + timeout
        remaining_time = timeout_time - time.time()
        if remaining_time <= 0.0:
            if last_exception:
                error = last_exception
            else:
                error = OperationTimeoutError("Send operation timed out")
            _LOGGER.info("%r send operation timed out. (%r)", self._name, error)
            raise error
        self._handler._msg_timeout = remaining_time * 1000  # type: ignore  # pylint: disable=protected-access

    def _send(self, message, session_id=None, timeout=None, last_exception=None):
        self._open()
        self._set_msg_timeout(timeout, last_exception)
        if session_id and not message.properties.group_id:
            message.properties.group_id = session_id
        try:
            self._handler.send_message(message.message)
        except Exception as e:
            raise MessageSendFailed(e)

    @classmethod
    def from_queue(
        cls,
        fully_qualified_namespace,
        queue_name,
        credential,
        **kwargs
    ):
        # type: (str, str, TokenCredential, Any) -> ServiceBusSenderClient
        return cls(
            fully_qualified_namespace=fully_qualified_namespace,
            entity_name=queue_name,
            credential=credential,
            **kwargs
        )

    @classmethod
    def from_topic(
        cls,
        fully_qualified_namespace,
        topic_name,
        credential,
        **kwargs
    ):
        # type: (str, str, TokenCredential, Any) -> ServiceBusSenderClient
        return cls(
            fully_qualified_namespace=fully_qualified_namespace,
            entity_name=topic_name,
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

    def send(self, message, session_id=None, message_timeout=None):
        # type: (Message, str, float) -> None
        self._do_retryable_operation(
            self._send,
            message=message,
            session_id=session_id,
            timeout=message_timeout,
            require_need_timeout=True,
            require_last_exception=True
        )

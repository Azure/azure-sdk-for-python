# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import uuid
import logging
import time

from uamqp import SendClient

from ._client_base import ClientBase, SenderReceiverMixin
from .common.errors import (
    _ServiceBusErrorPolicy,
    MessageSendFailed
)
from .common.utils import create_properties

_LOGGER = logging.getLogger(__name__)


class ServiceBusSenderClient(ClientBase, SenderReceiverMixin):
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
        self._create_attribute_for_sender(entity_name)

    def _create_handler(self, auth):
        properties = create_properties()
        self._handler = SendClient(
            self._entity_uri,
            auth=auth,
            debug=self._config.logging_enable,
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
            auth = self._create_auth()
            self._create_handler(auth)
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
        unsent_events = self._handler.pending_messages
        super(ServiceBusSenderClient, self)._reconnect()
        try:
            self._handler.queue_message(*unsent_events)
            self._handler.wait()
        except Exception as e:  # pylint: disable=broad-except
            self._handle_exception(e)

    def _send(self, message, session_id=None, timeout=None, last_exception=None):
        self._open()
        self._set_sender_msg_timeout(timeout, last_exception)
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

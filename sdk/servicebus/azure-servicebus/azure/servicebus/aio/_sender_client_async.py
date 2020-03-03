# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import logging
import asyncio
from typing import Any

from uamqp import SendClientAsync

from .._client_base import SenderReceiverMixin
from ._client_base_async import ClientBaseAsync
from ..common.errors import (
    MessageSendFailed
)
from ..common.utils import create_properties

_LOGGER = logging.getLogger(__name__)


class ServiceBusSenderClient(ClientBaseAsync, SenderReceiverMixin):
    def __init__(
        self,
        fully_qualified_namespace: str,
        credential: "TokenCredential",
        **kwargs: Any
    ):
        if kwargs.get("from_connection_str", False):
            super(ServiceBusSenderClient, self).__init__(
                fully_qualified_namespace=fully_qualified_namespace,
                credential=credential,
                **kwargs
            )
        else:
            queue_name = kwargs.get("queue_name")
            topic_name = kwargs.get("topic_name")
            if queue_name and topic_name:
                raise ValueError("Queue/Topic name can not be specified simultaneously.")
            if not (queue_name or topic_name):
                raise ValueError("Queue/Topic name is missing. Please specify queue_name/topic_name.")
            entity_name = queue_name or topic_name
            super(ServiceBusSenderClient, self).__init__(
                fully_qualified_namespace=fully_qualified_namespace,
                credential=credential,
                entity_name=entity_name,
                **kwargs
            )

        self._create_attribute_for_sender()

    def _create_handler(self, auth):
        properties = create_properties()
        self._handler = SendClientAsync(
            self._entity_uri,
            auth=auth,
            debug=self._config.logging_enable,
            properties=properties,
            error_policy=self._error_policy,
            client_name=self._name,
            encoding=self._config.encoding
        )

    async def _open_async(self):
        if self._running:
            return
        if self._handler:
            await self._handler.close_async()
        try:
            auth = await self._create_auth_async()
            self._create_handler(auth)
            await self._handler.open_async()
            while not await self._handler.client_ready_async():
                await asyncio.sleep(0.05)
        except Exception as e:  # pylint: disable=broad-except
            try:
                await self._handle_exception_async(e)
            except Exception:
                self._running = False
                raise
        self._running = True

    async def _reconnect_async(self):
        unsent_events = self._handler.pending_messages
        await super(ServiceBusSenderClient, self)._reconnect_async()
        try:
            self._handler.queue_message(*unsent_events)
            await self._handler.wait_async()
        except Exception as e:  # pylint: disable=broad-except
            await self._handle_exception_async(e)

    async def _send_async(self, message, session_id=None, timeout=None, last_exception=None):
        await self._open_async()
        self._sender_set_msg_timeout(timeout, last_exception)
        if session_id and not message.properties.group_id:
            message.properties.group_id = session_id
        try:
            await self._handler.send_message_async(message.message)
        except Exception as e:
            raise MessageSendFailed(e)

    @classmethod
    def from_connection_string(
        cls,
        conn_str: str,
        **kwargs: Any,
    ) -> "ServiceBusSenderClient":
        constructor_args = cls._from_connection_string(
            conn_str,
            **kwargs
        )
        return cls(**constructor_args)

    async def send(self, message, session_id=None, message_timeout=None):
        # type: (Message, str, float) -> None
        await self._do_retryable_operation_async(
            self._send_async,
            message=message,
            session_id=session_id,
            timeout=message_timeout,
            require_timeout=True,
            require_last_exception=True
        )

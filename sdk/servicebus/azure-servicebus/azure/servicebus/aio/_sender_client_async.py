# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import uuid
import logging
import time
import asyncio

from uamqp import SendClientAsync

from .._client_base import SenderReceiverMixin
from ._client_base_async import ClientBaseAsync
from ..common.errors import (
    _ServiceBusErrorPolicy,
    OperationTimeoutError,
    MessageSendFailed
)
from ..common.utils import create_properties

_LOGGER = logging.getLogger(__name__)


class ServiceBusSenderClient(ClientBaseAsync, SenderReceiverMixin):
    def __init__(
        self,
        fully_qualified_namespace: str,
        entity_name: str,
        credential: "TokenCredential",
        **kwargs
    ):
        super(ClientBaseAsync, self).__init__(
            fully_qualified_namespace=fully_qualified_namespace,
            credential=credential,
            entity_name=entity_name,
            **kwargs
        )
        self._create_attribute_for_sender(entity_name)

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

    async def _open(self):
        if self._running:
            return
        if self._handler:
            await self._handler.close()
        try:
            auth = await self._create_auth_async()
            self._create_handler(auth)
            await self._handler.open()
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

    async def _send(self, message, session_id=None, timeout=None, last_exception=None):
        await self._open()
        self._set_sender_msg_timeout(timeout, last_exception)
        if session_id and not message.properties.group_id:
            message.properties.group_id = session_id
        try:
            await self._handler.send_message_async(message.message)
        except Exception as e:
            raise MessageSendFailed(e)

    async def send(self, message, session_id=None, message_timeout=None):
        # type: (Message, str, float) -> None
        await self._do_retryable_operation_async(
            self._send,
            message=message,
            session_id=session_id,
            timeout=message_timeout,
            require_need_timeout=True,
            require_last_exception=True
        )

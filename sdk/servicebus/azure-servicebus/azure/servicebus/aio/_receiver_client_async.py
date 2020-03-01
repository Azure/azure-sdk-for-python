# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import asyncio
import collections
import logging

from uamqp import ReceiveClientAsync

from .._client_base import SenderReceiverMixin
from ._client_base_async import ClientBaseAsync
from ..common.utils import create_properties


_LOGGER = logging.getLogger(__name__)


class ServiceBusReceiverClient(collections.abc.AsyncIterator, ClientBaseAsync, SenderReceiverMixin):
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

    async def __anext__(self):
        while True:
            try:
                await self._open_async()
                uamqp_message = await self._message_iter.__anext__()
                message = self._receiver_build_message(uamqp_message)
                return message
            except StopAsyncIteration:
                await self.close()
                raise
            except Exception as e:  # pylint: disable=broad-except
                await self._handle_exception_async(e)

    def _create_handler(self, auth):
        properties = create_properties()
        if not self._session_id:
            self._handler = ReceiveClientAsync(
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
            self._handler = ReceiveClientAsync(
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

    async def _open_async(self):
        if self._running:
            return
        if self._handler:
            await self._handler.close_async()
        try:
            auth = await self._create_auth_async()
            self._create_handler(auth)
            await self._handler.open_async()
            self._message_iter = self._handle.receive_messages_iter_async()
            while not self._handler.client_ready_async():
                await asyncio.sleep(0.05)
        except Exception as e:  # pylint: disable=broad-except
            try:
                await self._handle_exception_async(e)
            except Exception:
                self.running = False
                raise
        self._running = True

    async def _receive_async(self, max_batch_size=None, timeout=None):
        await self._open_async()
        wrapped_batch = []
        max_batch_size = max_batch_size or self._handler._prefetch  # pylint: disable=protected-access

        timeout_ms = 1000 * timeout if timeout else 0
        batch = await self._handler.receive_message_batch_async(
            max_batch_size=max_batch_size,
            timeout=timeout_ms)
        for received in batch:
            message = self._receiver_build_message(received)
            wrapped_batch.append(message)

        return wrapped_batch

    async def close(self, exception=None):
        if not self._running:
            return
        self._running = False
        await super(ServiceBusReceiverClient, self).close(exception=exception)

    async def receive(self, max_batch_size=None, timeout=None):
        # type: (int, float) -> List[ReceivedMessage]
        return await self._do_retryable_operation(
            self._receive_async,
            max_batch_size=max_batch_size,
            timeout=timeout,
            require_need_timeout=True
        )

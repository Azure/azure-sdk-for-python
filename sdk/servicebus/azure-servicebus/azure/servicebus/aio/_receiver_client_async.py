# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import asyncio
import collections
import logging
from typing import Any, TYPE_CHECKING

from uamqp import ReceiveClientAsync

from .._receiver_client import ReceiverMixin
from ._client_base_async import ClientBaseAsync
from ..common.utils import create_properties
from .async_message import Message as MessageAsync

if TYPE_CHECKING:
    from azure.core.credentials import TokenCredential

_LOGGER = logging.getLogger(__name__)


class ServiceBusReceiverClient(collections.abc.AsyncIterator, ClientBaseAsync, ReceiverMixin):
    def __init__(
        self,
        fully_qualified_namespace: str,
        credential: "TokenCredential",
        **kwargs: Any
    ):
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

    async def __anext__(self):
        while True:
            try:
                await self._open_async()
                uamqp_message = await self._message_iter.__anext__()
                message = self._build_message(uamqp_message, MessageAsync)
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

    async def _open_async(self):
        if self._running:
            return
        if self._handler:
            await self._handler.close_async()
        try:
            auth = await self._create_auth_async()
            self._create_handler(auth)
            await self._handler.open_async()
            self._message_iter = self._handler.receive_messages_iter_async()
            while not await self._handler.client_ready_async():
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
            message = self._build_message(received, MessageAsync)
            wrapped_batch.append(message)

        return wrapped_batch

    @classmethod
    def from_connection_string(
        cls,
        conn_str: str,
        **kwargs: Any,
    ) -> "ServiceBusReceiverClient":
        constructor_args = cls._from_connection_string(
            conn_str,
            **kwargs
        )
        if kwargs.get("queue_name") and kwargs.get("subscription_name"):
            raise ValueError("Queue entity does not have subscription.")

        if kwargs.get("topic_name") and not kwargs.get("subscription_name"):
            raise ValueError("Subscription name is missing for the topic. Please specify subscription_name.")
        return cls(**constructor_args)

    async def close(self, exception=None):
        if not self._running:
            return
        self._running = False
        await super(ServiceBusReceiverClient, self).close(exception=exception)

    async def receive(self, max_batch_size=None, timeout=None):
        # type: (int, float) -> List[ReceivedMessage]
        return await self._do_retryable_operation_async(
            self._receive_async,
            max_batch_size=max_batch_size,
            timeout=timeout,
            require_timeout=True
        )

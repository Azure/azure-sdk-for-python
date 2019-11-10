# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import asyncio
import logging
import time

from uamqp import errors, constants, compat  # type: ignore
from ..error import EventHubError
from ..aio.error_async import _handle_exception

log = logging.getLogger(__name__)


class ConsumerProducerMixin(object):

    def __init__(self):
        self._client = None
        self._handler = None
        self._name = None
        self._running = False
        self._closed = False

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    def _check_closed(self):
        if self._closed:
            raise EventHubError("{} has been closed. Please create a new one to handle event data.".format(self._name))

    def _create_handler(self):
        pass

    async def _open(self):
        """
        Open the EventHubConsumer using the supplied connection.

        """
        # pylint: disable=protected-access
        if not self._running:
            if self._handler:
                await self._handler.close_async()
            self._create_handler()
            await self._handler.open_async(connection=await self._client._conn_manager.get_connection(
                self._client._address.hostname,
                self._client._create_auth()
            ))
            while not await self._handler.client_ready_async():
                await asyncio.sleep(0.05)
            self._max_message_size_on_link = self._handler.message_handler._link.peer_max_message_size \
                                             or constants.MAX_MESSAGE_LENGTH_BYTES  # pylint: disable=protected-access
            self._running = True

    async def _close_handler(self):
        if self._handler:
            await self._handler.close_async()  # close the link (sharing connection) or connection (not sharing)
        self._running = False

    async def _close_connection(self):
        await self._close_handler()
        await self._client._conn_manager.reset_connection_if_broken()  # pylint:disable=protected-access

    async def _handle_exception(self, exception):
        if not self._running and isinstance(exception, compat.TimeoutException):
            exception = errors.AuthenticationException("Authorization timeout.")
            return await _handle_exception(exception, self)

        return await _handle_exception(exception, self)

    async def _do_retryable_operation(self, operation, timeout=100000, **kwargs):
        # pylint:disable=protected-access
        timeout_time = time.time() + (
            timeout if timeout else 100000)  # timeout equals to 0 means no timeout, set the value to be a large number.
        retried_times = 0
        last_exception = kwargs.pop('last_exception', None)
        operation_need_param = kwargs.pop('operation_need_param', True)

        while retried_times <= self._client._config.max_retries:
            try:
                if operation_need_param:
                    return await operation(timeout_time=timeout_time, last_exception=last_exception, **kwargs)
                return await operation()
            except Exception as exception:  # pylint:disable=broad-except
                last_exception = await self._handle_exception(exception)
                await self._client._try_delay(retried_times=retried_times, last_exception=last_exception,
                                              timeout_time=timeout_time, entity_name=self._name)
                retried_times += 1

        log.info("%r operation has exhausted retry. Last exception: %r.", self._name, last_exception)
        raise last_exception

    async def close(self):
        # type: () -> None
        """
        Close down the handler. If the handler has already closed,
        this will be a no op.
        """
        self._running = False
        if self._handler:
            await self._handler.close_async()
        self._closed = True

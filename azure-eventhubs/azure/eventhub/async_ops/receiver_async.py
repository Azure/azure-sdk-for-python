# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import asyncio
import uuid
import logging

from uamqp import errors, types
from uamqp import ReceiveClientAsync, Source

from azure.eventhub import EventHubError, EventData
from azure.eventhub.receiver import Receiver
from azure.eventhub.common import _error_handler

log = logging.getLogger(__name__)


class AsyncReceiver(Receiver):
    """
    Implements the async API of a Receiver.

    Example:
        .. literalinclude:: ../examples/async_examples/test_examples_eventhub_async.py
            :start-after: [START create_eventhub_client_async_receiver_instance]
            :end-before: [END create_eventhub_client_async_receiver_instance]
            :language: python
            :dedent: 4
            :caption: Create a new instance of the Async Receiver.

    """

    def __init__(  # pylint: disable=super-init-not-called
            self, client, source, offset=None, prefetch=300, epoch=None,
            keep_alive=None, auto_reconnect=True, loop=None):
        """
        Instantiate an async receiver.

        :param client: The parent EventHubClientAsync.
        :type client: ~azure.eventhub.async_ops.EventHubClientAsync
        :param source: The source EventHub from which to receive events.
        :type source: ~uamqp.address.Source
        :param prefetch: The number of events to prefetch from the service
         for processing. Default is 300.
        :type prefetch: int
        :param epoch: An optional epoch value.
        :type epoch: int
        :param loop: An event loop.
        """
        self.loop = loop or asyncio.get_event_loop()
        self.running = False
        self.client = client
        self.source = source
        self.offset = offset
        self.prefetch = prefetch
        self.epoch = epoch
        self.keep_alive = keep_alive
        self.auto_reconnect = auto_reconnect
        self.retry_policy = errors.ErrorPolicy(max_retries=3, on_error=_error_handler)
        self.reconnect_backoff = 1
        self.redirected = None
        self.error = None
        self.properties = None
        partition = self.source.split('/')[-1]
        self.name = "EHReceiver-{}-partition{}".format(uuid.uuid4(), partition)
        source = Source(self.source)
        if self.offset is not None:
            source.set_filter(self.offset.selector())
        if epoch:
            self.properties = {types.AMQPSymbol(self._epoch): types.AMQPLong(int(epoch))}
        self._handler = ReceiveClientAsync(
            source,
            auth=self.client.get_auth(),
            debug=self.client.debug,
            prefetch=self.prefetch,
            link_properties=self.properties,
            timeout=self.timeout,
            error_policy=self.retry_policy,
            keep_alive_interval=self.keep_alive,
            client_name=self.name,
            properties=self.client.create_properties(),
            loop=self.loop)

    async def open_async(self):
        """
        Open the Receiver using the supplied conneciton.
        If the handler has previously been redirected, the redirect
        context will be used to create a new handler before opening it.

        :param connection: The underlying client shared connection.
        :type: connection: ~uamqp.async_ops.connection_async.ConnectionAsync

        Example:
            .. literalinclude:: ../examples/async_examples/test_examples_eventhub_async.py
                :start-after: [START eventhub_client_async_receiver_open]
                :end-before: [END eventhub_client_async_receiver_open]
                :language: python
                :dedent: 4
                :caption: Open the Receiver using the supplied conneciton.

        """
        # pylint: disable=protected-access
        self.running = True
        if self.redirected:
            self.source = self.redirected.address
            source = Source(self.source)
            if self.offset is not None:
                source.set_filter(self.offset.selector())
            alt_creds = {
                "username": self.client._auth_config.get("iot_username"),
                "password":self.client._auth_config.get("iot_password")}
            self._handler = ReceiveClientAsync(
                source,
                auth=self.client.get_auth(**alt_creds),
                debug=self.client.debug,
                prefetch=self.prefetch,
                link_properties=self.properties,
                timeout=self.timeout,
                error_policy=self.retry_policy,
                keep_alive_interval=self.keep_alive,
                client_name=self.name,
                properties=self.client.create_properties(),
                loop=self.loop)
        await self._handler.open_async()
        while not await self._handler.client_ready_async():
            await asyncio.sleep(0.05)

    async def _reconnect_async(self):  # pylint: disable=too-many-statements
        # pylint: disable=protected-access
        alt_creds = {
            "username": self.client._auth_config.get("iot_username"),
            "password":self.client._auth_config.get("iot_password")}
        await self._handler.close_async()
        source = Source(self.source)
        if self.offset is not None:
            source.set_filter(self.offset.selector())
        self._handler = ReceiveClientAsync(
            source,
            auth=self.client.get_auth(**alt_creds),
            debug=self.client.debug,
            prefetch=self.prefetch,
            link_properties=self.properties,
            timeout=self.timeout,
            error_policy=self.retry_policy,
            keep_alive_interval=self.keep_alive,
            client_name=self.name,
            properties=self.client.create_properties(),
            loop=self.loop)
        try:
            await self._handler.open_async()
            while not await self._handler.client_ready_async():
                await asyncio.sleep(0.05)
            return True
        except errors.TokenExpired as shutdown:
            log.info("AsyncReceiver disconnected due to token expiry. Shutting down.")
            error = EventHubError(str(shutdown), shutdown)
            await self.close_async(exception=error)
            raise error
        except (errors.LinkDetach, errors.ConnectionClose) as shutdown:
            if shutdown.action.retry and self.auto_reconnect:
                log.info("AsyncReceiver detached. Attempting reconnect.")
                return False
            log.info("AsyncReceiver detached. Shutting down.")
            error = EventHubError(str(shutdown), shutdown)
            await self.close_async(exception=error)
            raise error
        except errors.MessageHandlerError as shutdown:
            if self.auto_reconnect:
                log.info("AsyncReceiver detached. Attempting reconnect.")
                return False
            log.info("AsyncReceiver detached. Shutting down.")
            error = EventHubError(str(shutdown), shutdown)
            await self.close_async(exception=error)
            raise error
        except errors.AMQPConnectionError as shutdown:
            if str(shutdown).startswith("Unable to open authentication session") and self.auto_reconnect:
                log.info("AsyncReceiver couldn't authenticate. Attempting reconnect.")
                return False
            log.info("AsyncReceiver connection error (%r). Shutting down.", shutdown)
            error = EventHubError(str(shutdown))
            await self.close_async(exception=error)
            raise error
        except Exception as e:
            log.info("Unexpected error occurred (%r). Shutting down.", e)
            error = EventHubError("Receiver reconnect failed: {}".format(e))
            await self.close_async(exception=error)
            raise error

    async def reconnect_async(self):
        """If the Receiver was disconnected from the service with
        a retryable error - attempt to reconnect."""
        while not await self._reconnect_async():
            await asyncio.sleep(self.reconnect_backoff)

    async def has_started(self):
        """
        Whether the handler has completed all start up processes such as
        establishing the connection, session, link and authentication, and
        is not ready to process messages.
        **This function is now deprecated and will be removed in v2.0+.**

        :rtype: bool
        """
        # pylint: disable=protected-access
        timeout = False
        auth_in_progress = False
        if self._handler._connection.cbs:
            timeout, auth_in_progress = await self._handler._auth.handle_token_async()
        if timeout:
            raise EventHubError("Authorization timeout.")
        if auth_in_progress:
            return False
        if not await self._handler._client_ready_async():
            return False
        return True

    async def close_async(self, exception=None):
        """
        Close down the handler. If the handler has already closed,
        this will be a no op. An optional exception can be passed in to
        indicate that the handler was shutdown due to error.

        :param exception: An optional exception if the handler is closing
         due to an error.
        :type exception: Exception

        Example:
            .. literalinclude:: ../examples/async_examples/test_examples_eventhub_async.py
                :start-after: [START eventhub_client_async_receiver_close]
                :end-before: [END eventhub_client_async_receiver_close]
                :language: python
                :dedent: 4
                :caption: Close down the handler.

        """
        self.running = False
        if self.error:
            return
        if isinstance(exception, errors.LinkRedirect):
            self.redirected = exception
        elif isinstance(exception, EventHubError):
            self.error = exception
        elif isinstance(exception, (errors.LinkDetach, errors.ConnectionClose)):
            self.error = EventHubError(str(exception), exception)
        elif exception:
            self.error = EventHubError(str(exception))
        else:
            self.error = EventHubError("This receive handler is now closed.")
        await self._handler.close_async()

    async def receive(self, max_batch_size=None, timeout=None):
        """
        Receive events asynchronously from the EventHub.

        :param max_batch_size: Receive a batch of events. Batch size will
         be up to the maximum specified, but will return as soon as service
         returns no new events. If combined with a timeout and no events are
         retrieve before the time, the result will be empty. If no batch
         size is supplied, the prefetch size will be the maximum.
        :type max_batch_size: int
        :rtype: list[~azure.eventhub.common.EventData]

        Example:
            .. literalinclude:: ../examples/async_examples/test_examples_eventhub_async.py
                :start-after: [START eventhub_client_async_receive]
                :end-before: [END eventhub_client_async_receive]
                :language: python
                :dedent: 4
                :caption: Sends an event data and asynchronously waits
                 until acknowledgement is received or operation times out.

        """
        if self.error:
            raise self.error
        if not self.running:
            raise ValueError("Unable to receive until client has been started.")
        data_batch = []
        try:
            timeout_ms = 1000 * timeout if timeout else 0
            message_batch = await self._handler.receive_message_batch_async(
                max_batch_size=max_batch_size,
                timeout=timeout_ms)
            for message in message_batch:
                event_data = EventData(message=message)
                self.offset = event_data.offset
                data_batch.append(event_data)
            return data_batch
        except (errors.TokenExpired, errors.AuthenticationException):
            log.info("AsyncReceiver disconnected due to token error. Attempting reconnect.")
            await self.reconnect_async()
            return data_batch
        except (errors.LinkDetach, errors.ConnectionClose) as shutdown:
            if shutdown.action.retry and self.auto_reconnect:
                log.info("AsyncReceiver detached. Attempting reconnect.")
                await self.reconnect_async()
                return data_batch
            log.info("AsyncReceiver detached. Shutting down.")
            error = EventHubError(str(shutdown), shutdown)
            await self.close_async(exception=error)
            raise error
        except errors.MessageHandlerError as shutdown:
            if self.auto_reconnect:
                log.info("AsyncReceiver detached. Attempting reconnect.")
                await self.reconnect_async()
                return data_batch
            log.info("AsyncReceiver detached. Shutting down.")
            error = EventHubError(str(shutdown), shutdown)
            await self.close_async(exception=error)
            raise error
        except Exception as e:
            log.info("Unexpected error occurred (%r). Shutting down.", e)
            error = EventHubError("Receive failed: {}".format(e))
            await self.close_async(exception=error)
            raise error

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import asyncio
import uuid
import logging

from uamqp import errors, types, compat
from uamqp import ReceiveClientAsync, Source

from azure.eventhub import EventHubError, EventData
from azure.eventhub.error import EventHubError, AuthenticationError, ConnectError, ConnectionLostError, _error_handler

log = logging.getLogger(__name__)


class EventHubConsumer(object):
    """
    Implements the async API of a EventHubConsumer.

    """
    timeout = 0
    _epoch = b'com.microsoft:epoch'

    def __init__(  # pylint: disable=super-init-not-called
            self, client, source, event_position=None, prefetch=300, owner_level=None,
            keep_alive=None, auto_reconnect=True, loop=None):
        """
        Instantiate an async consumer.

        :param client: The parent EventHubClientAsync.
        :type client: ~azure.eventhub.aio.EventHubClientAsync
        :param source: The source EventHub from which to receive events.
        :type source: ~uamqp.address.Source
        :param event_position: The position from which to start receiving.
        :type event_position: ~azure.eventhub.common.EventPosition
        :param prefetch: The number of events to prefetch from the service
         for processing. Default is 300.
        :type prefetch: int
        :param owner_level: The priority of the exclusive consumer. It will an exclusive
         consumer if owner_level is set.
        :type owner_level: int
        :param loop: An event loop.
        """
        self.loop = loop or asyncio.get_event_loop()
        self.running = False
        self.client = client
        self.source = source
        self.offset = event_position
        self.messages_iter = None
        self.prefetch = prefetch
        self.owner_level = owner_level
        self.keep_alive = keep_alive
        self.auto_reconnect = auto_reconnect
        self.retry_policy = errors.ErrorPolicy(max_retries=self.client.config.max_retries, on_error=_error_handler)
        self.reconnect_backoff = 1
        self.redirected = None
        self.error = None
        self.properties = None
        partition = self.source.split('/')[-1]
        self.name = "EHReceiver-{}-partition{}".format(uuid.uuid4(), partition)
        source = Source(self.source)
        if self.offset is not None:
            source.set_filter(self.offset._selector())  # pylint: disable=protected-access
        if owner_level:
            self.properties = {types.AMQPSymbol(self._epoch): types.AMQPLong(int(owner_level))}
        self._handler = ReceiveClientAsync(
            source,
            auth=self.client.get_auth(),
            debug=self.client.config.network_tracing,
            prefetch=self.prefetch,
            link_properties=self.properties,
            timeout=self.timeout,
            error_policy=self.retry_policy,
            keep_alive_interval=self.keep_alive,
            client_name=self.name,
            properties=self.client._create_properties(self.client.config.user_agent),  # pylint: disable=protected-access
            loop=self.loop)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close(exc_val)

    def __aiter__(self):
        return self

    async def __anext__(self):
        await self._open()
        max_retries = self.client.config.max_retries
        connecting_count = 0
        while True:
            connecting_count += 1
            try:
                if not self.messages_iter:
                    self.messages_iter = self._handler.receive_messages_iter_async()
                message = await self.messages_iter.__anext__()
                event_data = EventData(message=message)
                self.offset = event_data.offset
                return event_data
            except errors.AuthenticationException as auth_error:
                if connecting_count < max_retries:
                    log.info("EventHubConsumer disconnected due to token error. Attempting reconnect.")
                    await self._reconnect()
                else:
                    log.info("EventHubConsumer authentication failed. Shutting down.")
                    error = AuthenticationError(str(auth_error), auth_error)
                    await self.close(auth_error)
                    raise error
            except (errors.LinkDetach, errors.ConnectionClose) as shutdown:
                if shutdown.action.retry and self.auto_reconnect:
                    log.info("EventHubConsumer detached. Attempting reconnect.")
                    await self._reconnect()
                else:
                    log.info("EventHubConsumer detached. Shutting down.")
                    error = ConnectionLostError(str(shutdown), shutdown)
                    await self.close(exception=error)
                    raise error
            except errors.MessageHandlerError as shutdown:
                if connecting_count < max_retries:
                    log.info("EventHubConsumer detached. Attempting reconnect.")
                    await self._reconnect()
                else:
                    log.info("EventHubConsumer detached. Shutting down.")
                    error = ConnectionLostError(str(shutdown), shutdown)
                    await self.close(error)
                    raise error
            except errors.AMQPConnectionError as shutdown:
                if connecting_count < max_retries:
                    log.info("EventHubConsumer connection lost. Attempting reconnect.")
                    await self._reconnect()
                else:
                    log.info("EventHubConsumer connection lost. Shutting down.")
                    error = ConnectionLostError(str(shutdown), shutdown)
                    await self.close(error)
                    raise error
            except compat.TimeoutException as shutdown:
                if connecting_count < max_retries:
                    log.info("EventHubConsumer timed out receiving event data. Attempting reconnect.")
                    await self._reconnect()
                else:
                    log.info("EventHubConsumer timed out. Shutting down.")
                    await self.close(shutdown)
                    raise TimeoutError(str(shutdown), shutdown)
            except StopAsyncIteration:
                raise
            except Exception as e:
                log.info("Unexpected error occurred (%r). Shutting down.", e)
                error = EventHubError("Receive failed: {}".format(e))
                await self.close(exception=error)
                raise error

    def _check_closed(self):
        if self.error:
            raise EventHubError("This consumer has been closed. Please create a new consumer to receive event data.",
                                self.error)
    async def _open(self):
        """
        Open the EventHubConsumer using the supplied connection.
        If the handler has previously been redirected, the redirect
        context will be used to create a new handler before opening it.

        """
        # pylint: disable=protected-access
        self._check_closed()
        if self.redirected:
            self.source = self.redirected.address
            source = Source(self.source)
            if self.offset is not None:
                source.set_filter(self.offset._selector())  # pylint: disable=protected-access
            alt_creds = {
                "username": self.client._auth_config.get("iot_username"),
                "password":self.client._auth_config.get("iot_password")}
            self._handler = ReceiveClientAsync(
                source,
                auth=self.client.get_auth(**alt_creds),
                debug=self.client.config.network_tracing,
                prefetch=self.prefetch,
                link_properties=self.properties,
                timeout=self.timeout,
                error_policy=self.retry_policy,
                keep_alive_interval=self.keep_alive,
                client_name=self.name,
                properties=self.client._create_properties(self.client.config.user_agent),  # pylint: disable=protected-access
                loop=self.loop)
        if not self.running:
            await self._connect()
            self.running = True

    async def _connect(self):
        connected = await self._build_connection()
        if not connected:
            await asyncio.sleep(self.reconnect_backoff)
            while not await self._build_connection(is_reconnect=True):
                await asyncio.sleep(self.reconnect_backoff)

    async def _build_connection(self, is_reconnect=False):  # pylint: disable=too-many-statements
        # pylint: disable=protected-access
        if is_reconnect:
            alt_creds = {
                "username": self.client._auth_config.get("iot_username"),
                "password":self.client._auth_config.get("iot_password")}
            await self._handler.close_async()
            source = Source(self.source)
            if self.offset is not None:
                source.set_filter(self.offset._selector())  # pylint: disable=protected-access
            self._handler = ReceiveClientAsync(
                source,
                auth=self.client.get_auth(**alt_creds),
                debug=self.client.config.network_tracing,
                prefetch=self.prefetch,
                link_properties=self.properties,
                timeout=self.timeout,
                error_policy=self.retry_policy,
                keep_alive_interval=self.keep_alive,
                client_name=self.name,
                properties=self.client._create_properties(self.client.config.user_agent),  # pylint: disable=protected-access
                loop=self.loop)
            self.messages_iter = None
        try:
            await self._handler.open_async()
            while not await self._handler.client_ready_async():
                await asyncio.sleep(0.05)
            return True
        except errors.AuthenticationException as shutdown:
            if is_reconnect:
                log.info("EventHubConsumer couldn't authenticate. Shutting down. (%r)", shutdown)
                error = AuthenticationError(str(shutdown), shutdown)
                await self.close(exception=error)
                raise error
            else:
                log.info("EventHubConsumer couldn't authenticate. Attempting reconnect.")
                return False
        except (errors.LinkDetach, errors.ConnectionClose) as shutdown:
            if shutdown.action.retry:
                log.info("EventHubConsumer detached. Attempting reconnect.")
                return False
            else:
                log.info("EventHubConsumer detached. Shutting down.")
                error = ConnectError(str(shutdown), shutdown)
                await self.close(exception=error)
                raise error
        except errors.MessageHandlerError as shutdown:
            if is_reconnect:
                log.info("EventHubConsumer detached. Shutting down.")
                error = ConnectError(str(shutdown), shutdown)
                await self.close(exception=error)
                raise error
            else:
                log.info("EventHubConsumer detached. Attempting reconnect.")
                return False
        except errors.AMQPConnectionError as shutdown:
            if is_reconnect:
                log.info("EventHubConsumer connection error (%r). Shutting down.", shutdown)
                error = AuthenticationError(str(shutdown), shutdown)
                await self.close(exception=error)
                raise error
            else:
                log.info("EventHubConsumer couldn't authenticate. Attempting reconnect.")
                return False
        except compat.TimeoutException as shutdown:
            if is_reconnect:
                log.info("EventHubConsumer authentication timed out. Shutting down.")
                error = AuthenticationError(str(shutdown), shutdown)
                await self.close(exception=error)
                raise error
            else:
                log.info("EventHubConsumer authentication timed out. Attempting reconnect.")
                return False
        except Exception as e:
            log.info("Unexpected error occurred (%r). Shutting down.", e)
            error = EventHubError("EventHubConsumer reconnect failed: {}".format(e))
            await self.close(exception=error)
            raise error

    async def _reconnect(self):
        """If the EventHubConsumer was disconnected from the service with
        a retryable error - attempt to reconnect."""
        return await self._build_connection(is_reconnect=True)

    async def close(self, exception=None):
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
            self.error = ConnectError(str(exception), exception)
        elif exception:
            self.error = EventHubError(str(exception))
        else:
            self.error = EventHubError("This receive handler is now closed.")
        await self._handler.close_async()

    @property
    def queue_size(self):
        """
        The current size of the unprocessed Event queue.

        :rtype: int
        """
        # pylint: disable=protected-access
        if self._handler._received_messages:
            return self._handler._received_messages.qsize()
        return 0

    async def receive(self, max_batch_size=None, timeout=None):
        """
        Receive events asynchronously from the EventHub.

        :param max_batch_size: Receive a batch of events. Batch size will
         be up to the maximum specified, but will return as soon as service
         returns no new events. If combined with a timeout and no events are
         retrieve before the time, the result will be empty. If no batch
         size is supplied, the prefetch size will be the maximum.
        :type max_batch_size: int
        :param timeout: The timeout time in seconds to receive a batch of events
         from an Event Hub. Results will be returned after timeout. If combined
         with max_batch_size, it will return after either the count of received events
         reaches the max_batch_size or the operation has timed out.
        :type timeout: int
        :rtype: list[~azure.eventhub.common.EventData]

        Example:
            .. literalinclude:: ../examples/async_examples/test_examples_eventhub_async.py
                :start-after: [START eventhub_client_async_receive]
                :end-before: [END eventhub_client_async_receive]
                :language: python
                :dedent: 4
                :caption: Receives events asynchronously

        """
        await self._open()

        max_batch_size = min(self.client.config.max_batch_size, self.prefetch) if max_batch_size is None else max_batch_size
        timeout = self.client.config.receive_timeout if timeout is None else timeout

        data_batch = []
        max_retries = self.client.config.max_retries
        connecting_count = 0
        while True:
            connecting_count += 1
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
            except errors.AuthenticationException as auth_error:
                if connecting_count < max_retries:
                    log.info("EventHubConsumer disconnected due to token error. Attempting reconnect.")
                    await self._reconnect()
                else:
                    log.info("EventHubConsumer authentication failed. Shutting down.")
                    error = AuthenticationError(str(auth_error), auth_error)
                    await self.close(auth_error)
                    raise error
            except (errors.LinkDetach, errors.ConnectionClose) as shutdown:
                if shutdown.action.retry and self.auto_reconnect:
                    log.info("EventHubConsumer detached. Attempting reconnect.")
                    await self._reconnect()
                else:
                    log.info("EventHubConsumer detached. Shutting down.")
                    error = ConnectionLostError(str(shutdown), shutdown)
                    await self.close(exception=error)
                    raise error
            except errors.MessageHandlerError as shutdown:
                if connecting_count < max_retries:
                    log.info("EventHubConsumer detached. Attempting reconnect.")
                    await self._reconnect()
                else:
                    log.info("EventHubConsumer detached. Shutting down.")
                    error = ConnectionLostError(str(shutdown), shutdown)
                    await self.close(error)
                    raise error
            except errors.AMQPConnectionError as shutdown:
                if connecting_count < max_retries:
                    log.info("EventHubConsumer connection lost. Attempting reconnect.")
                    await self._reconnect()
                else:
                    log.info("EventHubConsumer connection lost. Shutting down.")
                    error = ConnectionLostError(str(shutdown), shutdown)
                    await self.close(error)
                    raise error
            except compat.TimeoutException as shutdown:
                if connecting_count < max_retries:
                    log.info("EventHubConsumer timed out receiving event data. Attempting reconnect.")
                    await self._reconnect()
                else:
                    log.info("EventHubConsumer timed out. Shutting down.")
                    await self.close(shutdown)
                    raise TimeoutError(str(shutdown), shutdown)
            except Exception as e:
                log.info("Unexpected error occurred (%r). Shutting down.", e)
                error = EventHubError("Receive failed: {}".format(e))
                await self.close(exception=error)
                raise error
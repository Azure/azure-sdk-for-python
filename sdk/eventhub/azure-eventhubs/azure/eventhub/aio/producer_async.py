# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import uuid
import asyncio
import logging
from typing import Iterator, Generator, List, Union

from uamqp import constants, errors, compat
from uamqp import SendClientAsync

from azure.eventhub.common import EventData, _BatchSendEventData
from azure.eventhub.error import EventHubError, ConnectError, \
    AuthenticationError, EventDataError, EventDataSendError, ConnectionLostError, _error_handler

log = logging.getLogger(__name__)


class EventHubProducer(object):
    """
    A producer responsible for transmitting EventData to a specific Event Hub,
     grouped together in batches. Depending on the options specified at creation, the producer may
     be created to allow event data to be automatically routed to an available partition or specific
     to a partition.

    """

    def __init__(  # pylint: disable=super-init-not-called
            self, client, target, partition=None, send_timeout=60,
            keep_alive=None, auto_reconnect=True, loop=None):
        """
        Instantiate an async EventHubProducer. EventHubProducer should be instantiated by calling the `create_producer`
         method in EventHubClient.

        :param client: The parent EventHubClientAsync.
        :type client: ~azure.eventhub.aio.EventHubClientAsync
        :param target: The URI of the EventHub to send to.
        :type target: str
        :param partition: The specific partition ID to send to. Default is `None`, in which case the service
         will assign to all partitions using round-robin.
        :type partition: str
        :param send_timeout: The timeout in seconds for an individual event to be sent from the time that it is
         queued. Default value is 60 seconds. If set to 0, there will be no timeout.
        :type send_timeout: float
        :param keep_alive: The time interval in seconds between pinging the connection to keep it alive during
         periods of inactivity. The default value is `None`, i.e. no keep alive pings.
        :type keep_alive: float
        :param auto_reconnect: Whether to automatically reconnect the producer if a retryable error occurs.
         Default value is `True`.
        :type auto_reconnect: bool
        :param loop: An event loop. If not specified the default event loop will be used.
        """
        self.loop = loop or asyncio.get_event_loop()
        self.running = False
        self.client = client
        self.target = target
        self.partition = partition
        self.keep_alive = keep_alive
        self.auto_reconnect = auto_reconnect
        self.timeout = send_timeout
        self.retry_policy = errors.ErrorPolicy(max_retries=self.client.config.max_retries, on_error=_error_handler)
        self.reconnect_backoff = 1
        self.name = "EHProducer-{}".format(uuid.uuid4())
        self.unsent_events = None
        self.redirected = None
        self.error = None
        if partition:
            self.target += "/Partitions/" + partition
            self.name += "-partition{}".format(partition)
        self._handler = SendClientAsync(
            self.target,
            auth=self.client.get_auth(),
            debug=self.client.config.network_tracing,
            msg_timeout=self.timeout,
            error_policy=self.retry_policy,
            keep_alive_interval=self.keep_alive,
            client_name=self.name,
            properties=self.client._create_properties(self.client.config.user_agent),  # pylint: disable=protected-access
            loop=self.loop)
        self._outcome = None
        self._condition = None

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close(exc_val)

    async def _open(self):
        """
        Open the EventHubProducer using the supplied connection.
        If the handler has previously been redirected, the redirect
        context will be used to create a new handler before opening it.

        """
        if self.redirected:
            self.target = self.redirected.address
            self._handler = SendClientAsync(
                self.target,
                auth=self.client.get_auth(),
                debug=self.client.config.network_tracing,
                msg_timeout=self.timeout,
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

    async def _build_connection(self, is_reconnect=False):
        """

        :param is_reconnect: True - trying to reconnect after fail to connect or a connection is lost.
                             False - the 1st time to connect
        :return: True - connected.  False - not connected
        """
        # pylint: disable=protected-access
        if is_reconnect:
            await self._handler.close_async()
            self._handler = SendClientAsync(
                self.target,
                auth=self.client.get_auth(),
                debug=self.client.config.network_tracing,
                msg_timeout=self.timeout,
                error_policy=self.retry_policy,
                keep_alive_interval=self.keep_alive,
                client_name=self.name,
                properties=self.client._create_properties(self.client.config.user_agent),
                loop=self.loop)
        try:
            await self._handler.open_async()
            while not await self._handler.client_ready_async():
                await asyncio.sleep(0.05)
            return True
        except errors.AuthenticationException as shutdown:
            if is_reconnect:
                log.info("EventHubProducer couldn't authenticate. Shutting down. (%r)", shutdown)
                error = AuthenticationError(str(shutdown), shutdown)
                await self.close(exception=error)
                raise error
            else:
                log.info("EventHubProducer couldn't authenticate. Attempting reconnect.")
                return False
        except (errors.LinkDetach, errors.ConnectionClose) as shutdown:
            if shutdown.action.retry:
                log.info("EventHubProducer detached. Attempting reconnect.")
                return False
            else:
                log.info("EventHubProducer detached. Shutting down.")
                error = ConnectError(str(shutdown), shutdown)
                await self.close(exception=error)
                raise error
        except errors.MessageHandlerError as shutdown:
            if is_reconnect:
                log.info("EventHubProducer detached. Shutting down.")
                error = ConnectError(str(shutdown), shutdown)
                await self.close(exception=error)
                raise error
            else:
                log.info("EventHubProducer detached. Attempting reconnect.")
                return False
        except errors.AMQPConnectionError as shutdown:
            if is_reconnect:
                log.info("EventHubProducer connection error (%r). Shutting down.", shutdown)
                error = AuthenticationError(str(shutdown), shutdown)
                await self.close(exception=error)
                raise error
            else:
                log.info("EventHubProducer couldn't authenticate. Attempting reconnect.")
                return False
        except compat.TimeoutException as shutdown:
            if is_reconnect:
                log.info("EventHubProducer authentication timed out. Shutting down.")
                error = AuthenticationError(str(shutdown), shutdown)
                await self.close(exception=error)
                raise error
            else:
                log.info("EventHubProducer authentication timed out. Attempting reconnect.")
                return False
        except Exception as e:
            log.info("Unexpected error occurred when building connection (%r). Shutting down.", e)
            error = EventHubError("Unexpected error occurred when building connection", e)
            await self.close(exception=error)
            raise error

    async def _reconnect(self):
        return await self._build_connection(is_reconnect=True)

    async def _send_event_data(self):
        await self._open()
        max_retries = self.client.config.max_retries
        connecting_count = 0
        while True:
            connecting_count += 1
            try:
                if self.unsent_events:
                    self._handler.queue_message(*self.unsent_events)
                    await self._handler.wait_async()
                    self.unsent_events = self._handler.pending_messages
                if self._outcome != constants.MessageSendResult.Ok:
                    EventHubProducer._error(self._outcome, self._condition)
                return
            except (errors.MessageAccepted,
                    errors.MessageAlreadySettled,
                    errors.MessageModified,
                    errors.MessageRejected,
                    errors.MessageReleased,
                    errors.MessageContentTooLarge) as msg_error:
                raise EventDataError(str(msg_error), msg_error)
            except errors.MessageException as failed:
                log.error("Send event data error (%r)", failed)
                error = EventDataSendError(str(failed), failed)
                await self.close(exception=error)
                raise error
            except errors.AuthenticationException as auth_error:
                if connecting_count < max_retries:
                    log.info("EventHubProducer disconnected due to token error. Attempting reconnect.")
                    await self._reconnect()
                else:
                    log.info("EventHubProducer authentication failed. Shutting down.")
                    error = AuthenticationError(str(auth_error), auth_error)
                    await self.close(auth_error)
                    raise error
            except (errors.LinkDetach, errors.ConnectionClose) as shutdown:
                if shutdown.action.retry:
                    log.info("EventHubProducer detached. Attempting reconnect.")
                    await self._reconnect()
                else:
                    log.info("EventHubProducer detached. Shutting down.")
                    error = ConnectionLostError(str(shutdown), shutdown)
                    await self.close(exception=error)
                    raise error
            except errors.MessageHandlerError as shutdown:
                if connecting_count < max_retries:
                    log.info("EventHubProducer detached. Attempting reconnect.")
                    await self._reconnect()
                else:
                    log.info("EventHubProducer detached. Shutting down.")
                    error = ConnectionLostError(str(shutdown), shutdown)
                    await self.close(error)
                    raise error
            except errors.AMQPConnectionError as shutdown:
                if connecting_count < max_retries:
                    log.info("EventHubProducer connection lost. Attempting reconnect.")
                    await self._reconnect()
                else:
                    log.info("EventHubProducer connection lost. Shutting down.")
                    error = ConnectionLostError(str(shutdown), shutdown)
                    await self.close(error)
                    raise error
            except compat.TimeoutException as shutdown:
                if connecting_count < max_retries:
                    log.info("EventHubProducer timed out sending event data. Attempting reconnect.")
                    await self._reconnect()
                else:
                    log.info("EventHubProducer timed out. Shutting down.")
                    await self.close(shutdown)
                    raise ConnectionLostError(str(shutdown), shutdown)
            except Exception as e:
                log.info("Unexpected error occurred (%r). Shutting down.", e)
                error = EventHubError("Send failed: {}".format(e), e)
                await self.close(exception=error)
                raise error

    def _check_closed(self):
        if self.error:
            raise EventHubError("This producer has been closed. Please create a new producer to send event data.",
                                self.error)

    def _on_outcome(self, outcome, condition):
        """
        Called when the outcome is received for a delivery.

        :param outcome: The outcome of the message delivery - success or failure.
        :type outcome: ~uamqp.constants.MessageSendResult
        :param condition: Detail information of the outcome.

        """
        self._outcome = outcome
        self._condition = condition

    @staticmethod
    def _error(outcome, condition):
        if outcome != constants.MessageSendResult.Ok:
            raise condition

    @staticmethod
    def _set_partition_key(event_datas, partition_key):
        ed_iter = iter(event_datas)
        for ed in ed_iter:
            ed._set_partition_key(partition_key)
            yield ed

    async def send(self, event_data, partition_key=None):
        # type:(Union[EventData, Union[List[EventData], Iterator[EventData], Generator[EventData]]], Union[str, bytes]) -> None
        """
        Sends an event data and blocks until acknowledgement is
        received or operation times out.

        :param event_data: The event to be sent. It can be an EventData object, or iterable of EventData objects
        :type event_data: ~azure.eventhub.common.EventData, Iterator, Generator, list
        :param partition_key: With the given partition_key, event data will land to
         a particular partition of the Event Hub decided by the service.
        :type partition_key: str
        :raises: ~azure.eventhub.AuthenticationError, ~azure.eventhub.ConnectError, ~azure.eventhub.ConnectionLostError,
                ~azure.eventhub.EventDataError, ~azure.eventhub.EventDataSendError, ~azure.eventhub.EventHubError
        :return: None
        :rtype: None

        Example:
            .. literalinclude:: ../examples/test_examples_eventhub.py
                :start-after: [START eventhub_client_async_send]
                :end-before: [END eventhub_client_async_send]
                :language: python
                :dedent: 4
                :caption: Sends an event data and blocks until acknowledgement is received or operation times out.

        """
        self._check_closed()
        if isinstance(event_data, EventData):
            if partition_key:
                event_data._set_partition_key(partition_key)
            wrapper_event_data = event_data
        else:
            event_data_with_pk = self._set_partition_key(event_data, partition_key)
            wrapper_event_data = _BatchSendEventData(
                event_data_with_pk,
                partition_key=partition_key) if partition_key else _BatchSendEventData(event_data)
        wrapper_event_data.message.on_send_complete = self._on_outcome
        self.unsent_events = [wrapper_event_data.message]
        await self._send_event_data()

    async def close(self, exception=None):
        # type: (Exception) -> None
        """
        Close down the handler. If the handler has already closed,
        this will be a no op. An optional exception can be passed in to
        indicate that the handler was shutdown due to error.

        :param exception: An optional exception if the handler is closing
         due to an error.
        :type exception: Exception

        Example:
            .. literalinclude:: ../examples/async_examples/test_examples_eventhub_async.py
                :start-after: [START eventhub_client_async_sender_close]
                :end-before: [END eventhub_client_async_sender_close]
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
            self.error = EventHubError("This send handler is now closed.")
        await self._handler.close_async()
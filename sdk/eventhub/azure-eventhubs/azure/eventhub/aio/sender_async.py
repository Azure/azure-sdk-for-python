# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import uuid
import asyncio
import logging

from uamqp import constants, errors
from uamqp import SendClientAsync

from azure.eventhub import MessageSendResult
from azure.eventhub import EventHubError
from azure.eventhub.common import _error_handler, EventData, _BatchSendEventData

log = logging.getLogger(__name__)


class Sender(object):
    """
    Implements the async API of a Sender.

    Example:
        .. literalinclude:: ../examples/async_examples/test_examples_eventhub_async.py
            :start-after: [START create_eventhub_client_async_sender_instance]
            :end-before: [END create_eventhub_client_async_sender_instance]
            :language: python
            :dedent: 4
            :caption: Create a new instance of the Async Sender.

    """

    def __init__(  # pylint: disable=super-init-not-called
            self, client, target, partition=None, send_timeout=60,
            keep_alive=None, auto_reconnect=True, loop=None):
        """
        Instantiate an EventHub event SenderAsync handler.

        :param client: The parent EventHubClientAsync.
        :type client: ~azure.eventhub.aio.EventHubClientAsync
        :param target: The URI of the EventHub to send to.
        :type target: str
        :param partition: The specific partition ID to send to. Default is `None`, in which case the service
         will assign to all partitions using round-robin.
        :type partition: str
        :param send_timeout: The timeout in seconds for an individual event to be sent from the time that it is
         queued. Default value is 60 seconds. If set to 0, there will be no timeout.
        :type send_timeout: int
        :param keep_alive: The time interval in seconds between pinging the connection to keep it alive during
         periods of inactivity. The default value is `None`, i.e. no keep alive pings.
        :type keep_alive: int
        :param auto_reconnect: Whether to automatically reconnect the sender if a retryable error occurs.
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
        self.name = "EHSender-{}".format(uuid.uuid4())
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
            properties=self.client.create_properties(self.client.config.user_agent),
            loop=self.loop)
        self._outcome = None
        self._condition = None

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close(exc_val)

    async def _open(self):
        """
        Open the Sender using the supplied conneciton.
        If the handler has previously been redirected, the redirect
        context will be used to create a new handler before opening it.

        :param connection: The underlying client shared connection.
        :type: connection: ~uamqp.async_ops.connection_async.ConnectionAsync

        Example:
            .. literalinclude:: ../examples/async_examples/test_examples_eventhub_async.py
                :start-after: [START eventhub_client_async_sender_open]
                :end-before: [END eventhub_client_async_sender_open]
                :language: python
                :dedent: 4
                :caption: Open the Sender using the supplied conneciton.

        """
        self.running = True
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
                properties=self.client.create_properties(self.client.config.user_agent),
                loop=self.loop)
        await self._handler.open_async()
        while not await self._handler.client_ready_async():
            await asyncio.sleep(0.05)

    async def _reconnect(self):
        await self._handler.close_async()
        unsent_events = self._handler.pending_messages
        self._handler = SendClientAsync(
            self.target,
            auth=self.client.get_auth(),
            debug=self.client.config.network_tracing,
            msg_timeout=self.timeout,
            error_policy=self.retry_policy,
            keep_alive_interval=self.keep_alive,
            client_name=self.name,
            properties=self.client.create_properties(self.client.config.user_agent),
            loop=self.loop)
        try:
            await self._handler.open_async()
            self._handler.queue_message(*unsent_events)
            await self._handler.wait_async()
            return True
        except errors.TokenExpired as shutdown:
            log.info("AsyncSender disconnected due to token expiry. Shutting down.")
            error = EventHubError(str(shutdown), shutdown)
            await self.close(exception=error)
            raise error
        except (errors.LinkDetach, errors.ConnectionClose) as shutdown:
            if shutdown.action.retry and self.auto_reconnect:
                log.info("AsyncSender detached. Attempting reconnect.")
                return False
            log.info("AsyncSender reconnect failed. Shutting down.")
            error = EventHubError(str(shutdown), shutdown)
            await self.close(exception=error)
            raise error
        except errors.MessageHandlerError as shutdown:
            if self.auto_reconnect:
                log.info("AsyncSender detached. Attempting reconnect.")
                return False
            log.info("AsyncSender reconnect failed. Shutting down.")
            error = EventHubError(str(shutdown), shutdown)
            await self.close(exception=error)
            raise error
        except errors.AMQPConnectionError as shutdown:
            if str(shutdown).startswith("Unable to open authentication session") and self.auto_reconnect:
                log.info("AsyncSender couldn't authenticate. Attempting reconnect.")
                return False
            log.info("AsyncSender connection error (%r). Shutting down.", shutdown)
            error = EventHubError(str(shutdown))
            await self.close(exception=error)
            raise error
        except Exception as e:
            log.info("Unexpected error occurred (%r). Shutting down.", e)
            error = EventHubError("Sender reconnect failed: {}".format(e))
            await self.close(exception=error)
            raise error

    async def reconnect(self):
        """If the Receiver was disconnected from the service with
        a retryable error - attempt to reconnect."""
        while not await self._reconnect():
            await asyncio.sleep(self.reconnect_backoff)

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
            self.error = EventHubError(str(exception), exception)
        elif exception:
            self.error = EventHubError(str(exception))
        else:
            self.error = EventHubError("This send handler is now closed.")
        await self._handler.close_async()

    async def _send_event_data(self, event_data):
        if not self.running:
            await self._open()
        try:
            self._handler.send_message(event_data.message)
            if self._outcome != MessageSendResult.Ok:
                raise Sender._error(self._outcome, self._condition)
        except errors.MessageException as failed:
            error = EventHubError(str(failed), failed)
            await self.close(exception=error)
            raise error
        except (errors.TokenExpired, errors.AuthenticationException):
            log.info("Sender disconnected due to token error. Attempting reconnect.")
            await self.reconnect()
        except (errors.LinkDetach, errors.ConnectionClose) as shutdown:
            if shutdown.action.retry and self.auto_reconnect:
                log.info("Sender detached. Attempting reconnect.")
                await self.reconnect()
            else:
                log.info("Sender detached. Shutting down.")
                error = EventHubError(str(shutdown), shutdown)
                await self.close(exception=error)
                raise error
        except errors.MessageHandlerError as shutdown:
            if self.auto_reconnect:
                log.info("Sender detached. Attempting reconnect.")
                await self.reconnect()
            else:
                log.info("Sender detached. Shutting down.")
                error = EventHubError(str(shutdown), shutdown)
                await self.close(exception=error)
                raise error
        except Exception as e:
            log.info("Unexpected error occurred (%r). Shutting down.", e)
            error = EventHubError("Send failed: {}".format(e))
            await self.close(exception=error)
            raise error
        else:
            return self._outcome

    @staticmethod
    def _verify_partition(event_datas):
        ed_iter = iter(event_datas)
        try:
            ed = next(ed_iter)
            partition_key = ed.partition_key
            yield ed
        except StopIteration:
            raise ValueError("batch_event_data must not be empty")
        for ed in ed_iter:
            if ed.partition_key != partition_key:
                raise ValueError("partition key of all EventData must be the same if being sent in a batch")
            yield ed

    async def send(self, event_data):
        """
        Sends an event data and blocks until acknowledgement is
        received or operation times out.

        :param event_data: The event to be sent.
        :type event_data: ~azure.eventhub.common.EventData
        :raises: ~azure.eventhub.common.EventHubError if the message fails to
         send.
        :return: The outcome of the message send.
        :rtype: ~uamqp.constants.MessageSendResult

        Example:
            .. literalinclude:: ../examples/test_examples_eventhub.py
                :start-after: [START eventhub_client_sync_send]
                :end-before: [END eventhub_client_sync_send]
                :language: python
                :dedent: 4
                :caption: Sends an event data and blocks until acknowledgement is received or operation times out.

        """
        if self.error:
            raise self.error
        if isinstance(event_data, EventData):
            wrapper_event_data = event_data
        else:
            wrapper_event_data = _BatchSendEventData(self._verify_partition(event_data))
        wrapper_event_data.message.on_send_complete = self._on_outcome
        await self._send_event_data(wrapper_event_data)

    def queue_message(self, event_data, callback=None):
        """
        Transfers an event data and notifies the callback when the operation is done.

        :param event_data: The event to be sent.
        :type event_data: ~azure.eventhub.common.EventData
        :param callback: Callback to be run once the message has been send.
         This must be a function that accepts two arguments.
        :type callback: callable[~uamqp.constants.MessageSendResult, ~azure.eventhub.common.EventHubError]

        Example:
            .. literalinclude:: ../examples/test_examples_eventhub.py
                :start-after: [START eventhub_client_transfer]
                :end-before: [END eventhub_client_transfer]
                :language: python
                :dedent: 4
                :caption: Transfers an event data and notifies the callback when the operation is done.

        """
        if self.error:
            raise self.error
        if not self.running:
            self._open()
        if event_data.partition_key and self.partition:
            raise ValueError("EventData partition key cannot be used with a partition sender.")
        if callback:
            event_data.message.on_send_complete = lambda o, c: callback(o, Sender._error(o, c))
        self._handler.queue_message(event_data.message)

    async def send_pending_messages(self):
        """
        Wait until all transferred events have been sent.
        """
        if self.error:
            raise self.error
        if not self.running:
            raise ValueError("Unable to send until client has been started.")
        try:
            await self._handler.wait_async()
        except (errors.TokenExpired, errors.AuthenticationException):
            log.info("AsyncSender disconnected due to token error. Attempting reconnect.")
            await self.reconnect()
        except (errors.LinkDetach, errors.ConnectionClose) as shutdown:
            if shutdown.action.retry and self.auto_reconnect:
                log.info("AsyncSender detached. Attempting reconnect.")
                await self.reconnect()
            else:
                log.info("AsyncSender detached. Shutting down.")
                error = EventHubError(str(shutdown), shutdown)
                await self.close(exception=error)
                raise error
        except errors.MessageHandlerError as shutdown:
            if self.auto_reconnect:
                log.info("AsyncSender detached. Attempting reconnect.")
                await self.reconnect()
            else:
                log.info("AsyncSender detached. Shutting down.")
                error = EventHubError(str(shutdown), shutdown)
                await self.close(exception=error)
                raise error
        except Exception as e:
            log.info("Unexpected error occurred (%r).", e)
            raise EventHubError("Send failed: {}".format(e))

    def _on_outcome(self, outcome, condition):
        """
        Called when the outcome is received for a delivery.

        :param outcome: The outcome of the message delivery - success or failure.
        :type outcome: ~uamqp.constants.MessageSendResult
        """
        self._outcome = outcome
        self._condition = condition

    @staticmethod
    def _error(outcome, condition):
        return None if outcome == MessageSendResult.Ok else EventHubError(outcome, condition)

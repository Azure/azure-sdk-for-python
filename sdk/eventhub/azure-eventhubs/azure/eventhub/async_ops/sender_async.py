# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import uuid
import asyncio
import logging

from uamqp import constants, errors
from uamqp import SendClientAsync

from azure.eventhub import EventHubError
from azure.eventhub.sender import Sender
from azure.eventhub.common import _error_handler

log = logging.getLogger(__name__)


class AsyncSender(Sender):
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
        :type client: ~azure.eventhub.async_ops.EventHubClientAsync
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
        self.retry_policy = errors.ErrorPolicy(max_retries=3, on_error=_error_handler)
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
            debug=self.client.debug,
            msg_timeout=self.timeout,
            error_policy=self.retry_policy,
            keep_alive_interval=self.keep_alive,
            client_name=self.name,
            properties=self.client.create_properties(),
            loop=self.loop)
        self._outcome = None
        self._condition = None

    async def open_async(self):
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
                debug=self.client.debug,
                msg_timeout=self.timeout,
                error_policy=self.retry_policy,
                keep_alive_interval=self.keep_alive,
                client_name=self.name,
                properties=self.client.create_properties(),
                loop=self.loop)
        await self._handler.open_async()
        while not await self._handler.client_ready_async():
            await asyncio.sleep(0.05)

    async def _reconnect_async(self):
        await self._handler.close_async()
        unsent_events = self._handler.pending_messages
        self._handler = SendClientAsync(
            self.target,
            auth=self.client.get_auth(),
            debug=self.client.debug,
            msg_timeout=self.timeout,
            error_policy=self.retry_policy,
            keep_alive_interval=self.keep_alive,
            client_name=self.name,
            properties=self.client.create_properties(),
            loop=self.loop)
        try:
            await self._handler.open_async()
            self._handler.queue_message(*unsent_events)
            await self._handler.wait_async()
            return True
        except errors.TokenExpired as shutdown:
            log.info("AsyncSender disconnected due to token expiry. Shutting down.")
            error = EventHubError(str(shutdown), shutdown)
            await self.close_async(exception=error)
            raise error
        except (errors.LinkDetach, errors.ConnectionClose) as shutdown:
            if shutdown.action.retry and self.auto_reconnect:
                log.info("AsyncSender detached. Attempting reconnect.")
                return False
            log.info("AsyncSender reconnect failed. Shutting down.")
            error = EventHubError(str(shutdown), shutdown)
            await self.close_async(exception=error)
            raise error
        except errors.MessageHandlerError as shutdown:
            if self.auto_reconnect:
                log.info("AsyncSender detached. Attempting reconnect.")
                return False
            log.info("AsyncSender reconnect failed. Shutting down.")
            error = EventHubError(str(shutdown), shutdown)
            await self.close_async(exception=error)
            raise error
        except errors.AMQPConnectionError as shutdown:
            if str(shutdown).startswith("Unable to open authentication session") and self.auto_reconnect:
                log.info("AsyncSender couldn't authenticate. Attempting reconnect.")
                return False
            log.info("AsyncSender connection error (%r). Shutting down.", shutdown)
            error = EventHubError(str(shutdown))
            await self.close_async(exception=error)
            raise error
        except Exception as e:
            log.info("Unexpected error occurred (%r). Shutting down.", e)
            error = EventHubError("Sender reconnect failed: {}".format(e))
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

    async def send(self, event_data):
        """
        Sends an event data and asynchronously waits until
        acknowledgement is received or operation times out.

        :param event_data: The event to be sent.
        :type event_data: ~azure.eventhub.common.EventData
        :raises: ~azure.eventhub.common.EventHubError if the message fails to
         send.

        Example:
            .. literalinclude:: ../examples/async_examples/test_examples_eventhub_async.py
                :start-after: [START eventhub_client_async_send]
                :end-before: [END eventhub_client_async_send]
                :language: python
                :dedent: 4
                :caption: Sends an event data and asynchronously waits
                 until acknowledgement is received or operation times out.

        """
        if self.error:
            raise self.error
        if not self.running:
            raise ValueError("Unable to send until client has been started.")
        if event_data.partition_key and self.partition:
            raise ValueError("EventData partition key cannot be used with a partition sender.")
        event_data.message.on_send_complete = self._on_outcome
        try:
            await self._handler.send_message_async(event_data.message)
            if self._outcome != constants.MessageSendResult.Ok:
                raise Sender._error(self._outcome, self._condition)
        except (errors.TokenExpired, errors.AuthenticationException):
            log.info("AsyncSender disconnected due to token error. Attempting reconnect.")
            await self.reconnect_async()
        except (errors.LinkDetach, errors.ConnectionClose) as shutdown:
            if shutdown.action.retry and self.auto_reconnect:
                log.info("AsyncSender detached. Attempting reconnect.")
                await self.reconnect_async()
            else:
                log.info("AsyncSender detached. Shutting down.")
                error = EventHubError(str(shutdown), shutdown)
                await self.close_async(exception=error)
                raise error
        except errors.MessageHandlerError as shutdown:
            if self.auto_reconnect:
                log.info("AsyncSender detached. Attempting reconnect.")
                await self.reconnect_async()
            else:
                log.info("AsyncSender detached. Shutting down.")
                error = EventHubError(str(shutdown), shutdown)
                await self.close_async(exception=error)
                raise error
        except Exception as e:
            log.info("Unexpected error occurred (%r). Shutting down.", e)
            error = EventHubError("Send failed: {}".format(e))
            await self.close_async(exception=error)
            raise error
        else:
            return self._outcome

    async def wait_async(self):
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
            await self.reconnect_async()
        except (errors.LinkDetach, errors.ConnectionClose) as shutdown:
            if shutdown.action.retry and self.auto_reconnect:
                log.info("AsyncSender detached. Attempting reconnect.")
                await self.reconnect_async()
            else:
                log.info("AsyncSender detached. Shutting down.")
                error = EventHubError(str(shutdown), shutdown)
                await self.close_async(exception=error)
                raise error
        except errors.MessageHandlerError as shutdown:
            if self.auto_reconnect:
                log.info("AsyncSender detached. Attempting reconnect.")
                await self.reconnect_async()
            else:
                log.info("AsyncSender detached. Shutting down.")
                error = EventHubError(str(shutdown), shutdown)
                await self.close_async(exception=error)
                raise error
        except Exception as e:
            log.info("Unexpected error occurred (%r).", e)
            raise EventHubError("Send failed: {}".format(e))

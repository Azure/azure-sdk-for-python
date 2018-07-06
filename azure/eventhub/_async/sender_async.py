# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import asyncio

from uamqp import constants, errors
from uamqp import SendClientAsync

from azure.eventhub import EventHubError
from azure.eventhub.sender import Sender

class AsyncSender(Sender):
    """
    Implements the async API of a Sender.
    """

    def __init__(self, client, target, partition=None, loop=None):  # pylint: disable=super-init-not-called
        """
        Instantiate an EventHub event SenderAsync handler.

        :param client: The parent EventHubClientAsync.
        :type client: ~azure.eventhub._async.EventHubClientAsync
        :param target: The URI of the EventHub to send to.
        :type target: str
        :param loop: An event loop.
        """
        self.redirected = None
        self.error = None
        self.debug = client.debug
        self.partition = partition
        if partition:
            target += "/Partitions/" + partition
        self.loop = loop or asyncio.get_event_loop()
        self._handler = SendClientAsync(
            target,
            auth=client.auth,
            debug=self.debug,
            msg_timeout=Sender.TIMEOUT,
            loop=self.loop)
        self._outcome = None
        self._condition = None

    async def open_async(self, connection):
        """
        Open the Sender using the supplied conneciton.
        If the handler has previously been redirected, the redirect
        context will be used to create a new handler before opening it.

        :param connection: The underlying client shared connection.
        :type: connection:~uamqp._async.connection_async.ConnectionAsync
        """
        if self.redirected:
            self._handler = SendClientAsync(
                self.redirected.address,
                auth=None,
                debug=self.debug,
                msg_timeout=Sender.TIMEOUT)
        await self._handler.open_async(connection=connection)

    async def has_started(self):
        """
        Whether the handler has completed all start up processes such as
        establishing the connection, session, link and authentication, and
        is not ready to process messages.

        :rtype: bool
        """
        # pylint: disable=protected-access
        timeout = False
        auth_in_progress = False
        if self._handler._connection.cbs:
            timeout, auth_in_progress = await self._handler._auth.handle_token_async()
        if timeout:
            raise EventHubError("Authorization timeout.")
        elif auth_in_progress:
            return False
        elif not await self._handler._client_ready():
            return False
        else:
            return True

    async def close_async(self, exception=None):
        """
        Close down the handler. If the handler has already closed,
        this will be a no op. An optional exception can be passed in to
        indicate that the handler was shutdown due to error.

        :param exception: An optional exception if the handler is closing
         due to an error.
        :type exception: Exception
        """
        if self.error:
            return
        elif isinstance(exception, errors.LinkRedirect):
            self.redirected = exception
        elif isinstance(exception, EventHubError):
            self.error = exception
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
        """
        if self.error:
            raise self.error
        if event_data.partition_key and self.partition:
            raise ValueError("EventData partition key cannot be used with a partition sender.")
        event_data.message.on_send_complete = self._on_outcome
        try:
            await self._handler.send_message_async(event_data.message)
            if self._outcome != constants.MessageSendResult.Ok:
                raise Sender._error(self._outcome, self._condition)
        except errors.LinkDetach as detach:
            error = EventHubError(str(detach))
            await self.close_async(exception=error)
            raise error
        except Exception as e:
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
        try:
            await self._handler.wait_async()
        except Exception as e:
            raise EventHubError("Send failed: {}".format(e))

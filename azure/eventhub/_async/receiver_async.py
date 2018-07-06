# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import asyncio

from uamqp import errors, types
from uamqp import ReceiveClientAsync

from azure.eventhub import EventHubError, EventData
from azure.eventhub.receiver import Receiver


class AsyncReceiver(Receiver):
    """
    Implements the async API of a Receiver.
    """

    def __init__(self, client, source, prefetch=300, epoch=None, loop=None):  # pylint: disable=super-init-not-called
        """
        Instantiate an async receiver.

        :param client: The parent EventHubClientAsync.
        :type client: ~azure.eventhub._async.EventHubClientAsync
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
        self.redirected = None
        self.error = None
        self.debug = client.debug
        self.offset = None
        self.prefetch = prefetch
        self.properties = None
        self.epoch = epoch
        if epoch:
            self.properties = {types.AMQPSymbol(self._epoch): types.AMQPLong(int(epoch))}
        self._handler = ReceiveClientAsync(
            source,
            auth=client.auth,
            debug=self.debug,
            prefetch=self.prefetch,
            link_properties=self.properties,
            timeout=self.timeout,
            loop=self.loop)

    async def open_async(self, connection):
        """
        Open the Receiver using the supplied conneciton.
        If the handler has previously been redirected, the redirect
        context will be used to create a new handler before opening it.

        :param connection: The underlying client shared connection.
        :type: connection: ~uamqp._async.connection_async.ConnectionAsync
        """
        if self.redirected:
            self._handler = ReceiveClientAsync(
                self.redirected.address,
                auth=None,
                debug=self.debug,
                prefetch=self.prefetch,
                link_properties=self.properties,
                timeout=self.timeout,
                loop=self.loop)
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
        """
        if self.error:
            raise self.error
        try:
            timeout_ms = 1000 * timeout if timeout else 0
            message_batch = await self._handler.receive_message_batch_async(
                max_batch_size=max_batch_size,
                timeout=timeout_ms)
            data_batch = []
            for message in message_batch:
                event_data = EventData(message=message)
                self.offset = event_data.offset
                data_batch.append(event_data)
            return data_batch
        except errors.LinkDetach as detach:
            error = EventHubError(str(detach))
            await self.close_async(exception=error)
            raise error
        except Exception as e:
            error = EventHubError("Receive failed: {}".format(e))
            await self.close_async(exception=error)
            raise error

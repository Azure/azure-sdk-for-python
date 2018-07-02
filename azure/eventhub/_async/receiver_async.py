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
        self.offset = None
        self.prefetch = prefetch
        self.epoch = epoch
        properties = None
        if epoch:
            properties = {types.AMQPSymbol(self._epoch): types.AMQPLong(int(epoch))}
        self._handler = ReceiveClientAsync(
            source,
            auth=client.auth,
            debug=client.debug,
            prefetch=self.prefetch,
            link_properties=properties,
            timeout=self.timeout,
            loop=self.loop)

    async def receive(self, max_batch_size=None, timeout=None):
        """
        Receive events asynchronously from the EventHub.

        :param max_batch_size: Receive a batch of events. Batch size will
         be up to the maximum specified, but will return as soon as service
         returns no new events. If combined with a timeout and no events are
         retrieve before the time, the result will be empty. If no batch
         size is supplied, the prefetch size will be the maximum.
        :type max_batch_size: int
        :rtype: list[~azure.eventhub.EventData]
        """
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
        except errors.AMQPConnectionError as e:
            message = "Failed to open receiver: {}".format(e)
            message += "\nPlease check that the partition key is valid "
            if self.epoch:
                message += "and that a higher epoch receiver is " \
                           "not already running for this partition."
            else:
                message += "and whether an epoch receiver is " \
                           "already running for this partition."
            raise EventHubError(message)
        except Exception as e:
            raise EventHubError("Receive failed: {}".format(e))

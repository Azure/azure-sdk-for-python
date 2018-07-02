# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import asyncio

from uamqp import constants
from uamqp import SendClientAsync

from azure.eventhub import EventHubError
from azure.eventhub.sender import Sender

class AsyncSender(Sender):
    """
    Implements the async API of a Sender.
    """

    def __init__(self, client, target, partition=None, loop=None):  # pylint: disable=super-init-not-called
        """
        Instantiate an EventHub event SenderAsync client.

        :param client: The parent EventHubClientAsync.
        :type client: ~azure.eventhub._async.EventHubClientAsync
        :param target: The URI of the EventHub to send to.
        :type target: str
        :param loop: An event loop.
        """
        self.partition = partition
        if partition:
            target += "/Partitions/" + partition
        self.loop = loop or asyncio.get_event_loop()
        self._handler = SendClientAsync(
            target,
            auth=client.auth,
            debug=client.debug,
            msg_timeout=Sender.TIMEOUT,
            loop=self.loop)
        self._outcome = None
        self._condition = None

    async def send(self, event_data):
        """
        Sends an event data and asynchronously waits until
        acknowledgement is received or operation times out.

        :param event_data: The event to be sent.
        :type event_data: ~azure.eventhub.EventData
        :raises: ~azure.eventhub.EventHubError if the message fails to
         send.
        """
        if event_data.partition_key and self.partition:
            raise ValueError("EventData partition key cannot be used with a partition sender.")
        event_data.message.on_send_complete = self._on_outcome
        try:
            await self._handler.send_message_async(event_data.message)
            if self._outcome != constants.MessageSendResult.Ok:
                raise Sender._error(self._outcome, self._condition)
        except Exception as e:
            raise EventHubError("Send failed: {}".format(e))

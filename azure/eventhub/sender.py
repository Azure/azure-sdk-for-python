# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from uamqp import constants
from uamqp import SendClient

from azure.eventhub.common import EventHubError


class Sender:
    """
    Implements a Sender.
    """
    TIMEOUT = 60.0

    def __init__(self, client, target, partition=None):
        """
        Instantiate an EventHub event Sender client.

        :param client: The parent EventHubClient.
        :type client: ~azure.eventhub.EventHubClient.
        :param target: The URI of the EventHub to send to.
        :type target: str
        """
        self.partition = partition
        if partition:
            target += "/Partitions/" + partition
        self._handler = SendClient(
            target,
            auth=client.auth,
            debug=client.debug,
            msg_timeout=Sender.TIMEOUT)
        self._outcome = None
        self._condition = None

    def send(self, event_data):
        """
        Sends an event data and blocks until acknowledgement is
        received or operation times out.

        :param event_data: The event to be sent.
        :type event_data: ~azure.eventhub.client.EventData
        :raises: ~azure.eventhub.client.EventHubError if the message fails to
         send.
        :return: The outcome of the message send.
        :rtype: ~uamqp.constants.MessageSendResult
        """
        if event_data.partition_key and self.partition:
            raise ValueError("EventData partition key cannot be used with a partition sender.")
        event_data.message.on_send_complete = self._on_outcome
        try:
            self._handler.send_message(event_data.message)
            if self._outcome != constants.MessageSendResult.Ok:
                raise Sender._error(self._outcome, self._condition)
        except Exception as e:
            raise EventHubError("Send failed: {}".format(e))
        else:
            return self._outcome

    def transfer(self, event_data, callback=None):
        """
        Transfers an event data and notifies the callback when the operation is done.

        :param event_data: The event to be sent.
        :type event_data: ~azure.eventhub.client.EventData
        :param callback: Callback to be run once the message has been send.
         This must be a function that accepts two arguments.
        :type callback: func[~uamqp.constants.MessageSendResult, ~azure.eventhub.client.EventHubError]
        """
        if event_data.partition_key and self.partition:
            raise ValueError("EventData partition key cannot be used with a partition sender.")
        if callback:
            event_data.message.on_send_complete = lambda o, c: callback(o, Sender._error(o, c))
        self._handler.queue_message(event_data.message)

    def wait(self):
        """
        Wait until all transferred events have been sent.
        """
        try:
            self._handler.wait()
        except Exception as e:
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
        return None if outcome == constants.MessageSendResult.Ok else EventHubError(outcome, condition)

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from uamqp import types, errors
from uamqp import ReceiveClient

from azure.eventhub.common import EventHubError, EventData, Offset


class Receiver:
    """
    Implements a Receiver.
    """
    timeout = 0
    _epoch = b'com.microsoft:epoch'

    def __init__(self, client, source, prefetch=300, epoch=None):
        """
        Instantiate a receiver.

        :param client: The parent EventHubClient.
        :type client: ~azure.eventhub.client.EventHubClient
        :param source: The source EventHub from which to receive events.
        :type source: ~uamqp.address.Source
        :param prefetch: The number of events to prefetch from the service
         for processing. Default is 300.
        :type prefetch: int
        :param epoch: An optional epoch value.
        :type epoch: int
        """
        self.offset = None
        self.prefetch = prefetch
        self.epoch = epoch
        self.properties = None
        self.redirected = None
        self.debug = client.debug
        self.error = None
        if epoch:
            self.properties = {types.AMQPSymbol(self._epoch): types.AMQPLong(int(epoch))}
        self._handler = ReceiveClient(
            source,
            auth=client.auth,
            debug=self.debug,
            prefetch=self.prefetch,
            link_properties=self.properties,
            timeout=self.timeout)

    def open(self, connection):
        if self.redirected:
            self._handler = ReceiveClient(
                self.redirected.address,
                auth=None,
                debug=self.debug,
                prefetch=self.prefetch,
                link_properties=self.properties,
                timeout=self.timeout)
        self._handler.open(connection)

    def get_handler_state(self):
        # pylint: disable=protected-access
        return self._handler._message_receiver.get_state()

    def has_started(self):
        # pylint: disable=protected-access
        timeout = False
        auth_in_progress = False
        if self._handler._connection.cbs:
            timeout, auth_in_progress = self._handler._auth.handle_token()
        if timeout:
            raise EventHubError("Authorization timeout.")
        elif auth_in_progress:
            return False
        elif not self._handler._client_ready():
            return False
        else:
            return True

    def close(self, exception=None):
        if self.error:
            return
        elif isinstance(exception, errors.LinkRedirect):
            self.redirected = exception
        elif isinstance(exception, EventHubError):
            self.error = exception
        elif exception:
            self.error = EventHubError(str(exception))
        else:
            self.error = EventHubError("This receive client is now closed.")
        self._handler.close()

    @property
    def queue_size(self):
        """
        The current size of the unprocessed message queue.

        :rtype: int
        """
        # pylint: disable=protected-access
        if self._handler._received_messages:
            return self._handler._received_messages.qsize()
        return 0

    def receive(self, max_batch_size=None, timeout=None):
        """
        Receive events from the EventHub.

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
            message_batch = self._handler.receive_message_batch(
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
            self.close(exception=error)
            raise error
        except Exception as e:
            error = EventHubError("Receive failed: {}".format(e))
            self.close(exception=error)
            raise error

    def selector(self, default):
        """
        Create a selector for the current offset if it is set.

        :param default: The fallback receive offset.
        :type default: ~azure.eventhub.common.Offset
        :rtype: ~azure.eventhub.common.Offset
        """
        if self.offset is not None:
            return Offset(self.offset).selector()
        return default

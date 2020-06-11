#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

import logging
import asyncio

from uamqp import constants, errors, receiver
from uamqp.utils import get_running_loop

_logger = logging.getLogger(__name__)


class MessageReceiverAsync(receiver.MessageReceiver):
    """An asynchronous Message Receiver that opens its own exclsuive Link on an
    existing Session.

    :ivar receive_settle_mode: The mode by which to settle message receive
     operations. If set to `PeekLock`, the receiver will lock a message once received until
     the client accepts or rejects the message. If set to `ReceiveAndDelete`, the service
     will assume successful receipt of the message and clear it from the queue. The
     default is `PeekLock`.
    :vartype receive_settle_mode: ~uamqp.constants.ReceiverSettleMode
    :ivar send_settle_mode: The mode by which to settle message send
     operations. If set to `Unsettled`, the client will wait for a confirmation
     from the service that the message was successfully sent. If set to 'Settled',
     the client will not wait for confirmation and assume success.
    :vartype send_settle_mode: ~uamqp.constants.SenderSettleMode
    :ivar max_message_size: The maximum allowed message size negotiated for the Link.
    :vartype max_message_size: int

    :param session: The underlying Session with which to receive.
    :type session: ~uamqp.session.Session
    :param source: The AMQP endpoint to receive from.
    :type source: ~uamqp.address.Source
    :param target: The name of target (i.e. the client).
    :type target: str or bytes
    :param name: A unique name for the receiver. If not specified a GUID will be used.
    :type name: str or bytes
    :param receive_settle_mode: The mode by which to settle message receive
     operations. If set to `PeekLock`, the receiver will lock a message once received until
     the client accepts or rejects the message. If set to `ReceiveAndDelete`, the service
     will assume successful receipt of the message and clear it from the queue. The
     default is `PeekLock`.
    :type receive_settle_mode: ~uamqp.constants.ReceiverSettleMode
    :param send_settle_mode: The mode by which to settle message send
     operations. If set to `Unsettled`, the client will wait for a confirmation
     from the service that the message was successfully sent. If set to 'Settled',
     the client will not wait for confirmation and assume success.
    :type send_settle_mode: ~uamqp.constants.SenderSettleMode
    :param desired_capabilities: The extension capabilities desired from the peer endpoint.
     To create an desired_capabilities object, please do as follows:
        - 1. Create an array of desired capability symbols: `capabilities_symbol_array = [types.AMQPSymbol(string)]`
        - 2. Transform the array to AMQPValue object: `utils.data_factory(types.AMQPArray(capabilities_symbol_array))`
    :type desired_capabilities: ~uamqp.c_uamqp.AMQPValue
    :param max_message_size: The maximum allowed message size negotiated for the Link.
    :type max_message_size: int
    :param prefetch: The receiver Link credit that determines how many
     messages the Link will attempt to handle per connection iteration.
    :type prefetch: int
    :param properties: Metadata to be sent in the Link ATTACH frame.
    :type properties: dict
    :param error_policy: A policy for parsing errors on link, connection and message
     disposition to determine whether the error should be retryable.
    :type error_policy: ~uamqp.errors.ErrorPolicy
    :param debug: Whether to turn on network trace logs. If `True`, trace logs
     will be logged at INFO level. Default is `False`.
    :type debug: bool
    :param encoding: The encoding to use for parameters supplied as strings.
     Default is 'UTF-8'
    :type encoding: str
    :param loop: A user specified event loop.
    :type loop: ~asycnio.AbstractEventLoop
    """

    def __init__(self, session, source, target,
                 on_message_received,
                 name=None,
                 receive_settle_mode=constants.ReceiverSettleMode.PeekLock,
                 send_settle_mode=constants.SenderSettleMode.Unsettled,
                 max_message_size=constants.MAX_MESSAGE_LENGTH_BYTES,
                 prefetch=300,
                 properties=None,
                 error_policy=None,
                 debug=False,
                 encoding='UTF-8',
                 desired_capabilities=None,
                 loop=None):
        self.loop = loop or get_running_loop()
        super(MessageReceiverAsync, self).__init__(
            session, source, target,
            on_message_received,
            name=name,
            receive_settle_mode=receive_settle_mode,
            send_settle_mode=send_settle_mode,
            max_message_size=max_message_size,
            prefetch=prefetch,
            properties=properties,
            error_policy=error_policy,
            debug=debug,
            encoding=encoding,
            desired_capabilities=desired_capabilities)

    async def __aenter__(self):
        """Open the MessageReceiver in an async context manager."""
        await self.open_async()
        return self

    async def __aexit__(self, *args):
        """Close the MessageReceiver when exiting an async context manager."""
        await self.destroy_async()

    async def destroy_async(self):
        """Asynchronously close both the Receiver and the Link. Clean up any C objects."""
        self.destroy()

    async def open_async(self):
        """Asynchronously open the MessageReceiver in order to start
        processing messages.

        :raises: ~uamqp.errors.AMQPConnectionError if the Receiver raises
         an error on opening. This can happen if the source URI is invalid
         or the credentials are rejected.
        """
        try:
            self._receiver.open(self)
        except ValueError:
            raise errors.AMQPConnectionError(
                "Failed to open Message Receiver. "
                "Please confirm credentials and target URI.")

    async def work_async(self):
        """Update the link status."""
        await asyncio.sleep(0, loop=self.loop)
        self._link.do_work()

    async def close_async(self):
        """Close the Receiver asynchronously, leaving the link intact."""
        self.close()

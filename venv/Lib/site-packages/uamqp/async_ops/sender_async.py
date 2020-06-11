#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

import logging
import asyncio

from uamqp import constants, errors, sender
from uamqp.utils import get_running_loop

_logger = logging.getLogger(__name__)


class MessageSenderAsync(sender.MessageSender):
    """An asynchronous Message Sender that opens its own exclsuive Link on an
    existing Session.

    :ivar link_credit: The sender Link credit that determines how many
     messages the Link will attempt to handle per connection iteration.
    :vartype link_credit: int
    :ivar properties: Metadata to be sent in the Link ATTACH frame.
    :vartype properties: dict
    :ivar send_settle_mode: The mode by which to settle message send
     operations. If set to `Unsettled`, the client will wait for a confirmation
     from the service that the message was successfully send. If set to 'Settled',
     the client will not wait for confirmation and assume success.
    :vartype send_settle_mode: ~uamqp.constants.SenderSettleMode
    :ivar receive_settle_mode: The mode by which to settle message receive
     operations. If set to `PeekLock`, the receiver will lock a message once received until
     the client accepts or rejects the message. If set to `ReceiveAndDelete`, the service
     will assume successful receipt of the message and clear it from the queue. The
     default is `PeekLock`.
    :vartype receive_settle_mode: ~uamqp.constants.ReceiverSettleMode
    :ivar max_message_size: The maximum allowed message size negotiated for the Link.
    :vartype max_message_size: int

    :param session: The underlying Session with which to send.
    :type session: ~uamqp.async_ops.session_async.SessionAsync
    :param source: The name of source (i.e. the client).
    :type source: str or bytes
    :param target: The AMQP endpoint to send to.
    :type target: ~uamqp.address.Target
    :param name: A unique name for the sender. If not specified a GUID will be used.
    :type name: str or bytes
    :param send_settle_mode: The mode by which to settle message send
     operations. If set to `Unsettled`, the client will wait for a confirmation
     from the service that the message was successfully send. If set to 'Settled',
     the client will not wait for confirmation and assume success.
    :type send_settle_mode: ~uamqp.constants.SenderSettleMode
    :param receive_settle_mode: The mode by which to settle message receive
     operations. If set to `PeekLock`, the receiver will lock a message once received until
     the client accepts or rejects the message. If set to `ReceiveAndDelete`, the service
     will assume successful receipt of the message and clear it from the queue. The
     default is `PeekLock`.
    :type receive_settle_mode: ~uamqp.constants.ReceiverSettleMode
    :param max_message_size: The maximum allowed message size negotiated for the Link.
    :type max_message_size: int
    :param link_credit: The sender Link credit that determines how many
     messages the Link will attempt to handle per connection iteration.
    :type link_credit: int
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
                 name=None,
                 send_settle_mode=constants.SenderSettleMode.Unsettled,
                 receive_settle_mode=constants.ReceiverSettleMode.PeekLock,
                 max_message_size=constants.MAX_MESSAGE_LENGTH_BYTES,
                 link_credit=None,
                 properties=None,
                 error_policy=None,
                 debug=False,
                 encoding='UTF-8',
                 loop=None):
        self.loop = loop or get_running_loop()
        super(MessageSenderAsync, self).__init__(
            session, source, target,
            name=name,
            send_settle_mode=send_settle_mode,
            receive_settle_mode=receive_settle_mode,
            max_message_size=max_message_size,
            link_credit=link_credit,
            properties=properties,
            error_policy=error_policy,
            debug=debug,
            encoding=encoding)

    async def __aenter__(self):
        """Open the MessageSender in an async context manager."""
        await self.open_async()
        return self

    async def __aexit__(self, *args):
        """Close the MessageSender when exiting an async context manager."""
        await self.destroy_async()

    async def destroy_async(self):
        """Asynchronously close both the Sender and the Link. Clean up any C objects."""
        self.destroy()

    async def open_async(self):
        """Asynchronously open the MessageSender in order to start
        processing messages.

        :raises: ~uamqp.errors.AMQPConnectionError if the Sender raises
         an error on opening. This can happen if the target URI is invalid
         or the credentials are rejected.
        """
        try:
            self._sender.open()
        except ValueError:
            raise errors.AMQPConnectionError(
                "Failed to open Message Sender. "
                "Please confirm credentials and target URI.")

    async def send_async(self, message, callback, timeout=0):
        """Add a single message to the internal pending queue to be processed
        by the Connection without waiting for it to be sent.

        :param message: The message to send.
        :type message: ~uamqp.message.Message
        :param callback: The callback to be run once a disposition is received
         in receipt of the message. The callback must take three arguments, the message,
         the send result and the optional delivery condition (exception).
        :type callback:
         callable[~uamqp.message.Message, ~uamqp.constants.MessageSendResult, ~uamqp.errors.MessageException]
        :param timeout: An expiry time for the message added to the queue. If the
         message is not sent within this timeout it will be discarded with an error
         state. If set to 0, the message will not expire. The default is 0.
        """
        # pylint: disable=protected-access
        try:
            raise self._error
        except TypeError:
            pass
        except Exception as e:
            _logger.warning("%r", e)
            raise
        c_message = message.get_message()
        message._on_message_sent = callback
        try:
            await self._session._connection.lock_async(timeout=None)
            return self._sender.send(c_message, timeout, message)
        finally:
            self._session._connection.release_async()

    async def work_async(self):
        """Update the link status."""
        await asyncio.sleep(0, loop=self.loop)
        self._link.do_work()

    async def close_async(self):
        """Close the sender asynchronously, leaving the link intact."""
        self._sender.close()

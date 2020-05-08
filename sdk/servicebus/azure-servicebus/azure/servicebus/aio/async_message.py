# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------

import datetime
import functools
import uuid

from azure.servicebus.common import message
from azure.servicebus.common.utils import get_running_loop
from azure.servicebus.common.errors import MessageSettleFailed
from azure.servicebus.common.constants import (
    DEADLETTERNAME,
    RECEIVER_LINK_DEAD_LETTER_REASON,
    RECEIVER_LINK_DEAD_LETTER_DESCRIPTION
)


class Message(message.Message):
    """A Service Bus Message.

    :param body: The data to send in a single message. The maximum size per message is 256 kB.
    :type body: str or bytes
    :param encoding: The encoding for string data. Default is UTF-8.
    :type encoding: str

    .. admonition:: Example:
        .. literalinclude:: ../samples/sync_samples/test_examples.py
            :start-after: [START send_complex_message]
            :end-before: [END send_complex_message]
            :language: python
            :dedent: 4
            :caption: Sending a message with additional properties

        .. literalinclude:: ../samples/sync_samples/test_examples.py
            :start-after: [START receive_complex_message]
            :end-before: [END receive_complex_message]
            :language: python
            :dedent: 4
            :caption: Checking the properties on a received message
    """

    def __init__(self, body, *, encoding='UTF-8', loop=None, **kwargs):
        self._loop = loop or get_running_loop()
        super(Message, self).__init__(body, encoding=encoding, **kwargs)

    async def renew_lock(self):
        """Renew the message lock.

        This will maintain the lock on the message to ensure
        it is not returned to the queue to be reprocessed. In order to complete (or otherwise settle)
        the message, the lock must be maintained. Messages received via ReceiveAndDelete mode are not
        locked, and therefore cannot be renewed. This operation can also be performed as an asynchronous
        background task by registering the message with an `azure.servicebus.aio.AutoLockRenew` instance.
        This operation is only available for non-sessionful messages.

        :raises: TypeError if the message is sessionful.
        :raises: ~azure.servicebus.common.errors.MessageLockExpired is message lock has already expired.
        :raises: ~azure.servicebus.common.errors.SessionLockExpired if session lock has already expired.
        :raises: ~azure.servicebus.common.errors.MessageAlreadySettled is message has already been settled.
        """
        if hasattr(self._receiver, 'locked_until'):
            raise TypeError("Session messages cannot be renewed. Please renew the Session lock instead.")
        self._is_live('renew')
        token = self.lock_token
        if not token:
            raise ValueError("Unable to renew lock - no lock token found.")

        expiry = await self._receiver._renew_locks(token)  # pylint: disable=protected-access
        self._expiry = datetime.datetime.fromtimestamp(expiry[b'expirations'][0]/1000.0)

    async def complete(self):
        """Complete the message. This removes the message from the queue.

        :raises: ~azure.servicebus.common.errors.MessageAlreadySettled if the message has been settled.
        :raises: ~azure.servicebus.common.errors.MessageLockExpired if message lock has already expired.
        :raises: ~azure.servicebus.common.errors.SessionLockExpired if session lock has already expired.
        :raises: ~azure.servicebus.common.errors.MessageSettleFailed if message settle operation fails.
        """
        self._is_live('accept')
        try:
            await self._loop.run_in_executor(None, self.message.accept)
        except Exception as e:
            raise MessageSettleFailed("accept", e)

    async def dead_letter(self, description=None, reason=None):
        """Move the message to the Dead Letter queue.

        The Dead Letter queue is a sub-queue that can be
        used to store messages that failed to process correctly, or otherwise require further inspection
        or processing. The queue can also be configured to send expired messages to the Dead Letter queue.
        To receive dead-lettered messages, use `QueueClient.get_deadletter_receiver()` or
        `SubscriptionClient.get_deadletter_receiver()`.

        :param str description: The error description for dead-lettering the message.
        :param str reason: The reason for dead-lettering the message. If `reason` is not set while `description` is
         set, then `reason` would be set the same as `description`.
        :raises: ~azure.servicebus.common.errors.MessageAlreadySettled if the message has been settled.
        :raises: ~azure.servicebus.common.errors.MessageLockExpired if message lock has already expired.
        :raises: ~azure.servicebus.common.errors.SessionLockExpired if session lock has already expired.
        :raises: ~azure.servicebus.common.errors.MessageSettleFailed if message settle operation fails.
        """
        self._is_live('reject')

        info = None
        if description:
            info = {
                RECEIVER_LINK_DEAD_LETTER_REASON: reason or description,
                RECEIVER_LINK_DEAD_LETTER_DESCRIPTION: description
            }
        elif reason:
            info = {
                RECEIVER_LINK_DEAD_LETTER_REASON: reason
            }

        try:
            reject = functools.partial(
                self.message.reject,
                condition=DEADLETTERNAME,
                description=description,
                info=info
            )
            await self._loop.run_in_executor(None, reject)
        except Exception as e:
            raise MessageSettleFailed("reject", e)

    async def abandon(self):
        """Abandon the message.

        This message will be returned to the queue to be reprocessed.

        :raises: ~azure.servicebus.common.errors.MessageAlreadySettled if the message has been settled.
        :raises: ~azure.servicebus.common.errors.MessageLockExpired if message lock has already expired.
        :raises: ~azure.servicebus.common.errors.SessionLockExpired if session lock has already expired.
        :raises: ~azure.servicebus.common.errors.MessageSettleFailed if message settle operation fails.
        """
        self._is_live('abandon')
        try:
            modify = functools.partial(self.message.modify, True, False)
            await self._loop.run_in_executor(None, modify)
        except Exception as e:
            raise MessageSettleFailed("abandon", e)

    async def defer(self):
        """Defer the message.

        This message will remain in the queue but must be received
        specifically by its sequence number in order to be processed.

        :raises: ~azure.servicebus.common.errors.MessageAlreadySettled if the message has been settled.
        :raises: ~azure.servicebus.common.errors.MessageLockExpired if message lock has already expired.
        :raises: ~azure.servicebus.common.errors.SessionLockExpired if session lock has already expired.
        :raises: ~azure.servicebus.common.errors.MessageSettleFailed if message settle operation fails.
        """
        self._is_live('defer')
        try:
            modify = functools.partial(self.message.modify, True, True)
            await self._loop.run_in_executor(None, modify)
        except Exception as e:
            raise MessageSettleFailed("defer", e)


class DeferredMessage(Message):
    """A message that has been deferred.

    A deferred message can be completed,
    abandoned, or dead-lettered, however it cannot be deferred again.
    """

    def __init__(self, deferred, mode):
        self._settled = mode == 0
        super(DeferredMessage, self).__init__(None, message=deferred)

    def _is_live(self, action):
        if not self._receiver:
            raise ValueError("Orphan message had no open connection.")
        super(DeferredMessage, self)._is_live(action)

    @property
    def lock_token(self):
        if self.settled:
            return None
        if hasattr(self.message, 'delivery_tag') and self.message.delivery_tag:
            return uuid.UUID(bytes_le=self.message.delivery_tag)
        delivery_annotations = self.message.delivery_annotations
        if delivery_annotations:
            return delivery_annotations.get(self._x_OPT_LOCK_TOKEN)
        return None

    @property
    def settled(self):
        return self._settled

    async def complete(self):
        """Complete the message.

        This removes the message from the queue.

        :raises: ~azure.servicebus.common.errors.MessageAlreadySettled if the message has been settled.
        :raises: ~azure.servicebus.common.errors.MessageLockExpired if message lock has already expired.
        :raises: ~azure.servicebus.common.errors.SessionLockExpired if session lock has already expired.
        :raises: ~azure.servicebus.common.errors.MessageSettleFailed if message settle operation fails.
        """
        self._is_live('complete')
        await self._receiver._settle_deferred('completed', [self.lock_token])  # pylint: disable=protected-access
        self._settled = True

    async def dead_letter(self, description=None, reason=None):
        """Move the message to the Dead Letter queue.

        The Dead Letter queue is a sub-queue that can be
        used to store messages that failed to process correctly, or otherwise require further inspection
        or processing. The queue can also be configured to send expired messages to the Dead Letter queue.
        To receive dead-lettered messages, use `QueueClient.get_deadletter_receiver()` or
        `SubscriptionClient.get_deadletter_receiver()`.

        :param str description: The error description for dead-lettering the message.
        :param str reason: The reason for dead-lettering the message. If `reason` is not set while `description` is
         set, then `reason` would be set the same as `description`.
        :raises: ~azure.servicebus.common.errors.MessageAlreadySettled if the message has been settled.
        :raises: ~azure.servicebus.common.errors.MessageLockExpired if message lock has already expired.
        :raises: ~azure.servicebus.common.errors.MessageSettleFailed if message settle operation fails.
        """
        self._is_live('dead-letter')
        details = {
            'deadletter-reason': str(reason) if reason else (str(description) if description else ""),
            'deadletter-description': str(description) if description else ""}
        await self._receiver._settle_deferred(  # pylint: disable=protected-access
            'suspended', [self.lock_token], dead_letter_details=details)
        self._settled = True

    async def abandon(self):
        """Abandon the message. This message will be returned to the queue to be reprocessed.

        :raises: ~azure.servicebus.common.errors.MessageAlreadySettled if the message has been settled.
        :raises: ~azure.servicebus.common.errors.MessageLockExpired if message lock has already expired.
        :raises: ~azure.servicebus.common.errors.MessageSettleFailed if message settle operation fails.
        """
        self._is_live('abandon')
        await self._receiver._settle_deferred('abandoned', [self.lock_token])  # pylint: disable=protected-access
        self._settled = True

    async def defer(self):
        """A DeferredMessage cannot be deferred. Raises `ValueError`."""
        raise ValueError("Message is already deferred.")

# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------

import uuid

from .._common import message as sync_message
from .._common.constants import (
    SETTLEMENT_ABANDON,
    SETTLEMENT_COMPLETE,
    SETTLEMENT_DEFER,
    SETTLEMENT_DEADLETTER,
    ReceiveSettleMode,
    _X_OPT_LOCK_TOKEN
)
from .._common.utils import get_running_loop, utc_from_timestamp
from ..exceptions import MessageSettleFailed


class ReceivedMessage(sync_message.ReceivedMessage):
    """A Service Bus Message received from service side.

    """

    def __init__(self, message, mode=ReceiveSettleMode.PeekLock, loop=None):
        self._loop = loop or get_running_loop()
        super(ReceivedMessage, self).__init__(message=message, mode=mode)

    @property
    def lock_token(self):
        if self.settled:
            return None
        if hasattr(self.message, 'delivery_tag') and self.message.delivery_tag:
            return uuid.UUID(bytes_le=self.message.delivery_tag)
        delivery_annotations = self.message.delivery_annotations
        if delivery_annotations:
            return delivery_annotations.get(_X_OPT_LOCK_TOKEN)
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
        # pylint: disable=protected-access
        self._is_live('complete')
        try:
            await self._receiver._settle_message(SETTLEMENT_COMPLETE, [self.lock_token])
        except Exception as e:
            raise MessageSettleFailed("complete", e)
        self._settled = True

    async def dead_letter(self, description=None):
        """Move the message to the Dead Letter queue.

        The Dead Letter queue is a sub-queue that can be
        used to store messages that failed to process correctly, or otherwise require further inspection
        or processing. The queue can also be configured to send expired messages to the Dead Letter queue.
        To receive dead-lettered messages, use `QueueClient.get_deadletter_receiver()` or
        `SubscriptionClient.get_deadletter_receiver()`.

        :param description: The reason for dead-lettering the message.
        :type description: str
        :raises: ~azure.servicebus.common.errors.MessageAlreadySettled if the message has been settled.
        :raises: ~azure.servicebus.common.errors.MessageLockExpired if message lock has already expired.
        :raises: ~azure.servicebus.common.errors.MessageSettleFailed if message settle operation fails.
        """
        # pylint: disable=protected-access
        self._is_live('dead-letter')
        details = {
            'deadletter-reason': str(description) if description else "",
            'deadletter-description': str(description) if description else ""}
        try:
            await self._receiver._settle_message(
                SETTLEMENT_DEADLETTER,
                [self.lock_token],
                dead_letter_details=details
            )
        except Exception as e:
            raise MessageSettleFailed("reject", e)
        self._settled = True

    async def abandon(self):
        """Abandon the message. This message will be returned to the queue to be reprocessed.

        :raises: ~azure.servicebus.common.errors.MessageAlreadySettled if the message has been settled.
        :raises: ~azure.servicebus.common.errors.MessageLockExpired if message lock has already expired.
        :raises: ~azure.servicebus.common.errors.MessageSettleFailed if message settle operation fails.
        """
        # pylint: disable=protected-access
        self._is_live('abandon')
        try:
            await self._receiver._settle_message(SETTLEMENT_ABANDON, [self.lock_token])
        except Exception as e:
            raise MessageSettleFailed("abandon", e)
        self._settled = True

    async def defer(self):
        """Abandon the message. This message will be returned to the queue to be reprocessed.

        :raises: ~azure.servicebus.common.errors.MessageAlreadySettled if the message has been settled.
        :raises: ~azure.servicebus.common.errors.MessageLockExpired if message lock has already expired.
        :raises: ~azure.servicebus.common.errors.MessageSettleFailed if message settle operation fails.
        """
        # pylint: disable=protected-access
        self._is_live('defer')
        try:
            await self._receiver._settle_message(SETTLEMENT_DEFER, [self.lock_token])
        except Exception as e:
            raise MessageSettleFailed("defer", e)
        self._settled = True

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
        if self._receiver._session_id:  # pylint: disable=protected-access
            raise TypeError("Session messages cannot be renewed. Please renew the Session lock instead.")
        self._is_live('renew')
        token = self.lock_token
        if not token:
            raise ValueError("Unable to renew lock - no lock token found.")

        expiry = await self._receiver._renew_locks(token)  # pylint: disable=protected-access
        self._expiry = utc_from_timestamp(expiry[b'expirations'][0]/1000.0)

# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
from typing import Optional

from .._common import message as sync_message
from .._common.constants import (
    SETTLEMENT_ABANDON,
    SETTLEMENT_COMPLETE,
    SETTLEMENT_DEFER,
    SETTLEMENT_DEADLETTER,
    ReceiveSettleMode,
    MGMT_RESPONSE_MESSAGE_EXPIRATION,
    MGMT_REQUEST_DEAD_LETTER_REASON,
    MGMT_REQUEST_DEAD_LETTER_DESCRIPTION,
    MESSAGE_COMPLETE,
    MESSAGE_DEAD_LETTER,
    MESSAGE_ABANDON,
    MESSAGE_DEFER,
    MESSAGE_RENEW_LOCK
)
from .._common.utils import get_running_loop, utc_from_timestamp
from ..exceptions import MessageSettleFailed


class ReceivedMessage(sync_message.ReceivedMessage):
    """A Service Bus Message received from service side.

    """

    def __init__(self, message, mode=ReceiveSettleMode.PeekLock, loop=None):
        self._loop = loop or get_running_loop()
        super(ReceivedMessage, self).__init__(message=message, mode=mode)

    async def complete(self):
        # type: () -> None
        """Complete the message.

        This removes the message from the queue.

        :rtype: None
        :raises: ~azure.servicebus.common.errors.MessageAlreadySettled if the message has been settled.
        :raises: ~azure.servicebus.common.errors.MessageLockExpired if message lock has already expired.
        :raises: ~azure.servicebus.common.errors.SessionLockExpired if session lock has already expired.
        :raises: ~azure.servicebus.common.errors.MessageSettleFailed if message settle operation fails.
        """
        # pylint: disable=protected-access
        self._is_live(MESSAGE_COMPLETE)
        try:
            await self._receiver._settle_message(SETTLEMENT_COMPLETE, [self.lock_token])
        except Exception as e:
            raise MessageSettleFailed(MESSAGE_COMPLETE, e)
        self._settled = True

    async def dead_letter(self, reason=None, description=None):
        # type: (Optional[str], Optional[str]) -> None
        """Move the message to the Dead Letter queue.

        The Dead Letter queue is a sub-queue that can be
        used to store messages that failed to process correctly, or otherwise require further inspection
        or processing. The queue can also be configured to send expired messages to the Dead Letter queue.

        :param str reason: The reason for dead-lettering the message.
        :param str description: The detailed description for dead-lettering the message.
        :rtype: None
        :raises: ~azure.servicebus.common.errors.MessageAlreadySettled if the message has been settled.
        :raises: ~azure.servicebus.common.errors.MessageLockExpired if message lock has already expired.
        :raises: ~azure.servicebus.common.errors.MessageSettleFailed if message settle operation fails.
        """
        # pylint: disable=protected-access
        self._is_live(MESSAGE_DEAD_LETTER)
        details = {
            MGMT_REQUEST_DEAD_LETTER_REASON: str(reason) if reason else "",
            MGMT_REQUEST_DEAD_LETTER_DESCRIPTION: str(description) if description else ""}
        try:
            await self._receiver._settle_message(
                SETTLEMENT_DEADLETTER,
                [self.lock_token],
                dead_letter_details=details
            )
        except Exception as e:
            raise MessageSettleFailed(MESSAGE_DEAD_LETTER, e)
        self._settled = True

    async def abandon(self):
        # type: () -> None
        """Abandon the message. This message will be returned to the queue to be reprocessed.

        :rtype: None
        :raises: ~azure.servicebus.common.errors.MessageAlreadySettled if the message has been settled.
        :raises: ~azure.servicebus.common.errors.MessageLockExpired if message lock has already expired.
        :raises: ~azure.servicebus.common.errors.MessageSettleFailed if message settle operation fails.
        """
        # pylint: disable=protected-access
        self._is_live(MESSAGE_ABANDON)
        try:
            await self._receiver._settle_message(SETTLEMENT_ABANDON, [self.lock_token])
        except Exception as e:
            raise MessageSettleFailed(MESSAGE_ABANDON, e)
        self._settled = True

    async def defer(self):
        # type: () -> None
        """Abandon the message. This message will be returned to the queue to be reprocessed.

        :rtype: None
        :raises: ~azure.servicebus.common.errors.MessageAlreadySettled if the message has been settled.
        :raises: ~azure.servicebus.common.errors.MessageLockExpired if message lock has already expired.
        :raises: ~azure.servicebus.common.errors.MessageSettleFailed if message settle operation fails.
        """
        # pylint: disable=protected-access
        self._is_live(MESSAGE_DEFER)
        try:
            await self._receiver._settle_message(SETTLEMENT_DEFER, [self.lock_token])
        except Exception as e:
            raise MessageSettleFailed(MESSAGE_DEFER, e)
        self._settled = True

    async def renew_lock(self):
        # type: () -> None
        """Renew the message lock.

        This will maintain the lock on the message to ensure
        it is not returned to the queue to be reprocessed. In order to complete (or otherwise settle)
        the message, the lock must be maintained. Messages received via ReceiveAndDelete mode are not
        locked, and therefore cannot be renewed. This operation can also be performed as an asynchronous
        background task by registering the message with an `azure.servicebus.aio.AutoLockRenew` instance.
        This operation is only available for non-sessionful messages.

        :rtype: None
        :raises: TypeError if the message is sessionful.
        :raises: ~azure.servicebus.common.errors.MessageLockExpired is message lock has already expired.
        :raises: ~azure.servicebus.common.errors.SessionLockExpired if session lock has already expired.
        :raises: ~azure.servicebus.common.errors.MessageAlreadySettled is message has already been settled.
        """
        if self._receiver._session_id:  # pylint: disable=protected-access
            raise TypeError("Session messages cannot be renewed. Please renew the Session lock instead.")
        self._is_live(MESSAGE_RENEW_LOCK)
        token = self.lock_token
        if not token:
            raise ValueError("Unable to renew lock - no lock token found.")

        expiry = await self._receiver._renew_locks(token)  # pylint: disable=protected-access
        self._expiry = utc_from_timestamp(expiry[MGMT_RESPONSE_MESSAGE_EXPIRATION][0]/1000.0)

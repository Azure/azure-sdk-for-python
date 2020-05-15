# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import logging
from typing import Optional

from .._common import message as sync_message
from .._common.constants import (
    ReceiveSettleMode,
    MGMT_RESPONSE_MESSAGE_EXPIRATION,
    MESSAGE_COMPLETE,
    MESSAGE_DEAD_LETTER,
    MESSAGE_ABANDON,
    MESSAGE_DEFER,
    MESSAGE_RENEW_LOCK
)
from .._common.utils import get_running_loop, utc_from_timestamp
from ..exceptions import MessageSettleFailed

_LOGGER = logging.getLogger(__name__)


class ReceivedMessage(sync_message.ReceivedMessage):
    """A Service Bus Message received from service side.

    """

    def __init__(self, message, mode=ReceiveSettleMode.PeekLock, loop=None, **kwargs):
        self._loop = loop or get_running_loop()
        super(ReceivedMessage, self).__init__(message=message, mode=mode, **kwargs)

    async def _settle_message(
            self,
            settle_operation,
            dead_letter_details=None
    ):
        try:
            if not self._is_deferred_message:
                try:
                    await self._loop.run_in_executor(
                        None,
                        self._settle_via_receiver_link(settle_operation, dead_letter_details)
                    )
                    return
                except RuntimeError as exception:
                    _LOGGER.info(
                        "Message settling: %r has encountered an exception (%r)."
                        "Trying to settle through management link",
                        settle_operation,
                        exception
                    )
            await self._settle_via_mgmt_link(settle_operation, dead_letter_details)()
        except Exception as e:
            raise MessageSettleFailed(settle_operation, e)

    async def complete(self):
        # type: () -> None
        """Complete the message.

        This removes the message from the queue.

        :rtype: None
        :raises: ~azure.servicebus.exceptions.MessageAlreadySettled if the message has been settled.
        :raises: ~azure.servicebus.exceptions.MessageLockExpired if message lock has already expired.
        :raises: ~azure.servicebus.exceptions.SessionLockExpired if session lock has already expired.
        :raises: ~azure.servicebus.exceptions.MessageSettleFailed if message settle operation fails.
        """
        # pylint: disable=protected-access
        self._check_live(MESSAGE_COMPLETE)
        await self._settle_message(MESSAGE_COMPLETE)
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
        :raises: ~azure.servicebus.exceptions.MessageAlreadySettled if the message has been settled.
        :raises: ~azure.servicebus.exceptions.MessageLockExpired if message lock has already expired.
        :raises: ~azure.servicebus.exceptions.MessageSettleFailed if message settle operation fails.
        """
        # pylint: disable=protected-access
        self._check_live(MESSAGE_DEAD_LETTER)
        await self._settle_message(MESSAGE_DEAD_LETTER)
        self._settled = True

    async def abandon(self):
        # type: () -> None
        """Abandon the message. 
        
        This message will be returned to the queue and made available to be received again.

        :rtype: None
        :raises: ~azure.servicebus.exceptions.MessageAlreadySettled if the message has been settled.
        :raises: ~azure.servicebus.exceptions.MessageLockExpired if message lock has already expired.
        :raises: ~azure.servicebus.exceptions.MessageSettleFailed if message settle operation fails.
        """
        # pylint: disable=protected-access
        self._check_live(MESSAGE_ABANDON)
        await self._settle_message(MESSAGE_ABANDON)
        self._settled = True

    async def defer(self):
        # type: () -> None
        """Defers the message.
        
        This message will remain in the queue but must be requested
        specifically by its sequence number in order to be received.

        :rtype: None
        :raises: ~azure.servicebus.exceptions.MessageAlreadySettled if the message has been settled.
        :raises: ~azure.servicebus.exceptions.MessageLockExpired if message lock has already expired.
        :raises: ~azure.servicebus.exceptions.MessageSettleFailed if message settle operation fails.
        """
        # pylint: disable=protected-access
        self._check_live(MESSAGE_DEFER)
        await self._settle_message(MESSAGE_DEFER)
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
        :raises: ~azure.servicebus.exceptions.MessageLockExpired is message lock has already expired.
        :raises: ~azure.servicebus.exceptions.SessionLockExpired if session lock has already expired.
        :raises: ~azure.servicebus.exceptions.MessageAlreadySettled is message has already been settled.
        """
        try:
            if self._receiver.session:  # pylint: disable=protected-access
                raise TypeError("Session messages cannot be renewed. Please renew the Session lock instead.")
        except AttributeError:
            pass
        self._check_live(MESSAGE_RENEW_LOCK)
        token = self.lock_token
        if not token:
            raise ValueError("Unable to renew lock - no lock token found.")

        expiry = await self._receiver._renew_locks(token)  # pylint: disable=protected-access
        self._expiry = utc_from_timestamp(expiry[MGMT_RESPONSE_MESSAGE_EXPIRATION][0]/1000.0)

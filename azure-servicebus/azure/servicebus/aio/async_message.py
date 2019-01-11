#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

import datetime
import functools

from azure.servicebus.common import message
from azure.servicebus.common.utils import get_running_loop
from azure.servicebus.common.errors import MessageSettleFailed
from azure.servicebus.common.constants import DEADLETTERNAME


class Message(message.Message):

    def __init__(self, body, *, encoding='UTF-8', loop=None, **kwargs):
        self._loop = loop or get_running_loop()
        super(Message, self).__init__(body, encoding=encoding, **kwargs)

    async def renew_lock(self):
        """Renew the message lock.
        This operation is only available for non-sessionful messages.

        :raises: TypeError is the mesage is sessionful.
        :raises: ~azure.servicebus.common.errors.MessageLockExpired is message lock has already expired.
        :raises: ~azure.servicebus.common.errors.SessionLockExpired if session lock has already expired.
        :raises: ~azure.servicebus.common.errors.MessageAlreadySettled is message has already been settled.
        """
        if hasattr(self._receiver, 'locked_until'):
            raise TypeError("Session messages cannot be renewed. Please renew the Session lock instead.")
        self._is_live('renew')
        expiry = await self._receiver._renew_locks(self.lock_token)  # pylint: disable=protected-access
        self._expiry = datetime.datetime.fromtimestamp(expiry[b'expirations'][0]/1000.0)

    async def complete(self):
        """Complete the message.

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

    async def dead_letter(self, description=None):
        """Move the message to the Dead Letter queue.

        :param description: Additional details.
        :type description: str
        :raises: ~azure.servicebus.common.errors.MessageAlreadySettled if the message has been settled.
        :raises: ~azure.servicebus.common.errors.MessageLockExpired if message lock has already expired.
        :raises: ~azure.servicebus.common.errors.SessionLockExpired if session lock has already expired.
        :raises: ~azure.servicebus.common.errors.MessageSettleFailed if message settle operation fails.
        """
        self._is_live('reject')
        try:
            reject = functools.partial(self.message.reject, condition=DEADLETTERNAME, description=description)
            await self._loop.run_in_executor(None, reject)
        except Exception as e:
            raise MessageSettleFailed("reject", e)

    async def abandon(self):
        """Abandon the message. This message will be returned to the queue to be reprocessed.

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
        """Defer the message. This message will remain in the queue but must be received
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
        delivery_annotations = self.message.delivery_annotations
        if delivery_annotations:
            return delivery_annotations.get(self._x_OPT_LOCK_TOKEN)
        return None

    @property
    def settled(self):
        return self._settled

    async def complete(self):
        self._is_live('complete')
        await self._receiver._settle_deferred('completed', [self.lock_token])  # pylint: disable=protected-access
        self._settled = True

    async def dead_letter(self, description=None):
        self._is_live('dead-letter')
        details = {
            'deadletter-reason': str(description) if description else "",
            'deadletter-description': str(description) if description else ""}
        await self._receiver._settle_deferred('suspended', [self.lock_token], dead_letter_details=details)  # pylint: disable=protected-access
        self._settled = True

    async def abandon(self):
        self._is_live('abandon')
        await self._receiver._settle_deferred('abandoned', [self.lock_token])  # pylint: disable=protected-access
        self._settled = True

    async def defer(self):
        raise ValueError("Message is already deferred.")

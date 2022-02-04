#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

import uuid
import logging
import time

from ._link_async import Link
from .._encode import encode_payload
from ..endpoints import Source
from ..constants import (
    SessionState,
    SessionTransferState,
    LinkDeliverySettleReason,
    LinkState,
    Role,
    SenderSettleMode
)
from ..performatives import (
    AttachFrame,
    DetachFrame,
    TransferFrame,
    DispositionFrame,
    FlowFrame,
)

_LOGGER = logging.getLogger(__name__)


class PendingDelivery(object):

    def __init__(self, **kwargs):
        self.message = kwargs.get('message')
        self.sent = False
        self.frame = None
        self.on_delivery_settled = kwargs.get('on_delivery_settled')
        self.link = kwargs.get('link')
        self.start = time.time()
        self.transfer_state = None
        self.timeout = kwargs.get('timeout')
        self.settled = kwargs.get('settled', False)
    
    async def on_settled(self, reason, state):
        if self.on_delivery_settled and not self.settled:
            try:
                await self.on_delivery_settled(reason, state)
            except Exception as e:
                _LOGGER.warning("Message 'on_send_complete' callback failed: %r", e)


class SenderLink(Link):

    def __init__(self, session, handle, target_address, **kwargs):
        name = kwargs.pop('name', None) or str(uuid.uuid4())
        role = Role.Sender
        if 'source_address' not in kwargs:
            kwargs['source_address'] = "sender-link-{}".format(name)
        super(SenderLink, self).__init__(session, handle, name, role, target_address=target_address, **kwargs)
        self._unsent_messages = []

    async def _incoming_attach(self, frame):
        await super(SenderLink, self)._incoming_attach(frame)
        self.current_link_credit = self.link_credit
        await self._outgoing_flow()
        await self._update_pending_delivery_status()

    async def _incoming_flow(self, frame):
        rcv_link_credit = frame[6]
        rcv_delivery_count = frame[5]
        if frame[4] is not None:
            if rcv_link_credit is None or rcv_delivery_count is None:
                _LOGGER.info("Unable to get link-credit or delivery-count from incoming ATTACH. Detaching link.")
                await self._remove_pending_deliveries()
                await self._set_state(LinkState.DETACHED)  # TODO: Send detach now?
            else:
                self.current_link_credit = rcv_delivery_count + rcv_link_credit - self.delivery_count
        if self.current_link_credit > 0:
            await self._send_unsent_messages()

    async def _outgoing_transfer(self, delivery):
        output = bytearray()
        encode_payload(output, delivery.message)
        delivery_count = self.delivery_count + 1
        delivery.frame = {
            'handle': self.handle,
            'delivery_tag': bytes(delivery_count),
            'message_format': delivery.message._code,
            'settled': delivery.settled,
            'more': False,
            'rcv_settle_mode': None,
            'state': None,
            'resume': None,
            'aborted': None,
            'batchable': None,
            'payload': output
        }
        if self.network_trace:
            _LOGGER.info("-> %r", TransferFrame(delivery_id='<pending>', **delivery.frame), extra=self.network_trace_params)
        await self._session._outgoing_transfer(delivery)
        if delivery.transfer_state == SessionTransferState.OKAY:
            self.delivery_count = delivery_count
            self.current_link_credit -= 1
            delivery.sent = True
            if delivery.settled:
                await delivery.on_settled(LinkDeliverySettleReason.SETTLED, None)
            else:
                self._pending_deliveries[delivery.frame['delivery_id']] = delivery
        elif delivery.transfer_state == SessionTransferState.ERROR:
            raise ValueError("Message failed to send")
        if self.current_link_credit <= 0:
            self.current_link_credit = self.link_credit
            await self._outgoing_flow()

    async def _incoming_disposition(self, frame):
        if self.network_trace:
            _LOGGER.info("<- %r", DispositionFrame(*frame), extra=self.network_trace_params)
        if not frame[3]:
            return
        range_end = (frame[2] or frame[1]) + 1
        settled_ids = [i for i in range(frame[1], range_end)]
        for settled_id in settled_ids:
            delivery = self._pending_deliveries.pop(settled_id, None)
            if delivery:
                await delivery.on_settled(LinkDeliverySettleReason.DISPOSITION_RECEIVED, frame[4])

    async def _update_pending_delivery_status(self):
        now = time.time()
        expired = []
        for delivery in self._pending_deliveries.values():
            if delivery.timeout and (now - delivery.start) >= delivery.timeout:
                expired.append(delivery.frame['delivery_id'])
                await delivery.on_settled(LinkDeliverySettleReason.TIMEOUT, None)
        self._pending_deliveries = {i: d for i, d in self._pending_deliveries.items() if i not in expired}

    async def _send_unsent_messages(self):
        unsent = []
        for delivery in self._unsent_messages:
            if not delivery.sent:
                await self._outgoing_transfer(delivery)
                if not delivery.sent:
                    unsent.append(delivery)
        self._unsent_messages = unsent

    async def send_transfer(self, message, **kwargs):
        if self._is_closed:
            raise ValueError("Link already closed.")
        if self.state != LinkState.ATTACHED:
            raise ValueError("Link is not attached.")
        settled = self.send_settle_mode == SenderSettleMode.Settled
        if self.send_settle_mode == SenderSettleMode.Mixed:
            settled = kwargs.pop('settled', True)
        delivery = PendingDelivery(
            on_delivery_settled=kwargs.get('on_send_complete'),
            timeout=kwargs.get('timeout'),
            link=self,
            message=message,
            settled=settled,
        )
        if self.current_link_credit == 0:
            self._unsent_messages.append(delivery)
        else:
            await self._outgoing_transfer(delivery)
            if not delivery.sent:
                self._unsent_messages.append(delivery)
        return delivery

    async def cancel_transfer(self, delivery):
        try:
            delivery = self._pending_deliveries.pop(delivery.frame['delivery_id'])
            await delivery.on_settled(LinkDeliverySettleReason.CANCELLED, None)
            return
        except KeyError:
            pass
        # todo remove from unset messages
        raise ValueError("No pending delivery with ID '{}' found.".format(delivery.frame['delivery_id']))

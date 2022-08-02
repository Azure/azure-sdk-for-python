#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------
import struct
import uuid
import logging
import time

from ._encode import encode_payload
from .link import Link
from .constants import (
    SessionTransferState,
    LinkDeliverySettleReason,
    LinkState,
    Role,
    SenderSettleMode,
    SessionState
)
from .performatives import (
    TransferFrame,
)
from .error import AMQPLinkError, ErrorCondition, MessageException

_LOGGER = logging.getLogger(__name__)


class PendingDelivery(object):

    def __init__(self, **kwargs):
        self.message = kwargs.get('message')
        self.sent = False
        self.frame = None
        self.on_delivery_settled = kwargs.get('on_delivery_settled')
        self.start = time.time()
        self.transfer_state = None
        self.timeout = kwargs.get('timeout')
        self.settled = kwargs.get('settled', False)

    def on_settled(self, reason, state):
        if self.on_delivery_settled and not self.settled:
            try:
                self.on_delivery_settled(reason, state)
            except Exception as e: # pylint:disable=broad-except
                # TODO: this swallows every error in on_delivery_settled, which mean we
                #  1. only handle errors we care about in the callback
                #  2. ignore errors we don't care
                #  We should revisit this:
                #  -- "Errors should never pass silently." unless "Unless explicitly silenced."
                _LOGGER.warning("Message 'on_send_complete' callback failed: %r", e)
        self.settled = True


class SenderLink(Link):

    def __init__(self, session, handle, target_address, **kwargs):
        name = kwargs.pop('name', None) or str(uuid.uuid4())
        role = Role.Sender
        if 'source_address' not in kwargs:
            kwargs['source_address'] = "sender-link-{}".format(name)
        super(SenderLink, self).__init__(session, handle, name, role, target_address=target_address, **kwargs)
        self._pending_deliveries = []

    # In theory we should not need to purge pending deliveries on attach/dettach - as a link should
    # be resume-able, however this is not yet supported.
    def _incoming_attach(self, frame):
        try:
            super(SenderLink, self)._incoming_attach(frame)
        except ValueError:  # TODO: This should NOT be a ValueError
            self._remove_pending_deliveries()
            raise
        self.current_link_credit = self.link_credit
        self._outgoing_flow()
        self.update_pending_deliveries()

    def _incoming_detach(self, frame):
        super(SenderLink, self)._incoming_attach(frame)
        self._remove_pending_deliveries()

    def _incoming_flow(self, frame):
        rcv_link_credit = frame[6]  # link_credit
        rcv_delivery_count = frame[5]  # delivery_count
        if frame[4] is not None:  # handle
            if rcv_link_credit is None or rcv_delivery_count is None:
                _LOGGER.info("Unable to get link-credit or delivery-count from incoming ATTACH. Detaching link.")
                self._remove_pending_deliveries()
                self._set_state(LinkState.DETACHED)  # TODO: Send detach now?
            else:
                self.current_link_credit = rcv_delivery_count + rcv_link_credit - self.delivery_count
        self.update_pending_deliveries()

    def _outgoing_transfer(self, delivery):
        output = bytearray()
        encode_payload(output, delivery.message)
        delivery_count = self.delivery_count + 1
        delivery.frame = {
            'handle': self.handle,
            'delivery_tag': struct.pack('>I', abs(delivery_count)),
            'message_format': delivery.message._code, # pylint:disable=protected-access
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
            # TODO: whether we should move frame tracing into centralized place e.g. connection.py
            _LOGGER.info("-> %r", TransferFrame(delivery_id='<pending>', **delivery.frame), extra=self.network_trace_params) # pylint:disable=line-to-long
            _LOGGER.info("   %r", delivery.message, extra=self.network_trace_params)
        self._session._outgoing_transfer(delivery) # pylint:disable=protected-access
        sent_and_settled = False
        if delivery.transfer_state == SessionTransferState.OKAY:
            self.delivery_count = delivery_count
            self.current_link_credit -= 1
            delivery.sent = True
            if delivery.settled:
                delivery.on_settled(LinkDeliverySettleReason.SETTLED, None)
                sent_and_settled = True
        # elif delivery.transfer_state == SessionTransferState.ERROR:
        # TODO: Session wasn't mapped yet - re-adding to the outgoing delivery queue?
        return sent_and_settled

    def _incoming_disposition(self, frame):
        if not frame[3]:  # settled
            return
        range_end = (frame[2] or frame[1]) + 1  # first or last
        settled_ids = list(range(frame[1], range_end))
        unsettled = []
        for delivery in self._pending_deliveries:
            if delivery.sent and delivery.frame['delivery_id'] in settled_ids:
                delivery.on_settled(LinkDeliverySettleReason.DISPOSITION_RECEIVED, frame[4])  # state
                continue
            unsettled.append(delivery)
        self._pending_deliveries = unsettled

    def _remove_pending_deliveries(self):
        for delivery in self._pending_deliveries:
            delivery.on_settled(LinkDeliverySettleReason.NOT_DELIVERED, None)
        self._pending_deliveries = []
    
    def _on_session_state_change(self):
        if self._session.state == SessionState.DISCARDING:
            self._remove_pending_deliveries()
        super()._on_session_state_change()

    def update_pending_deliveries(self):
        if self.current_link_credit <= 0:
            self.current_link_credit = self.link_credit
            self._outgoing_flow()
        now = time.time()
        pending = []
        for delivery in self._pending_deliveries:
            if delivery.timeout and (now - delivery.start) >= delivery.timeout:
                delivery.on_settled(LinkDeliverySettleReason.TIMEOUT, None)
                continue
            if not delivery.sent:
                sent_and_settled = self._outgoing_transfer(delivery)
                if sent_and_settled:
                    continue
            pending.append(delivery)
        self._pending_deliveries = pending

    def send_transfer(self, message, *, send_async=False, **kwargs):
        self._check_if_closed()
        if self.state != LinkState.ATTACHED:
            raise AMQPLinkError(  # TODO: should we introduce MessageHandler to indicate the handler is in wrong state
                condition=ErrorCondition.ClientError,  # TODO: should this be a ClientError?
                description="Link is not attached."
            )
        settled = self.send_settle_mode == SenderSettleMode.Settled
        if self.send_settle_mode == SenderSettleMode.Mixed:
            settled = kwargs.pop('settled', True)
        delivery = PendingDelivery(
            on_delivery_settled=kwargs.get('on_send_complete'),
            timeout=kwargs.get('timeout'),
            message=message,
            settled=settled,
        )
        if self.current_link_credit == 0 or send_async:
            self._pending_deliveries.append(delivery)
        else:
            sent_and_settled = self._outgoing_transfer(delivery)
            if not sent_and_settled:
                self._pending_deliveries.append(delivery)
        return delivery

    def cancel_transfer(self, delivery):
        try:
            index = self._pending_deliveries.index(delivery)
        except ValueError:
            raise ValueError("Found no matching pending transfer.")
        delivery = self._pending_deliveries[index]
        if delivery.sent:
            raise MessageException(
                ErrorCondition.ClientError,
                message="Transfer cannot be cancelled. Message has already been sent and awaiting disposition.")
        delivery.on_settled(LinkDeliverySettleReason.CANCELLED, None)
        self._pending_deliveries.pop(index)

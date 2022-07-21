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
from .endpoints import Source
from .link import Link
from .constants import (
    SessionState,
    SessionTransferState,
    LinkDeliverySettleReason,
    LinkState,
    Role,
    SenderSettleMode
)
from .performatives import (
    AttachFrame,
    DetachFrame,
    TransferFrame,
    DispositionFrame,
    FlowFrame,
)
from .error import AMQPLinkError, ErrorCondition

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
    
    def on_settled(self, reason, state):
        if self.on_delivery_settled and not self.settled:
            try:
                self.on_delivery_settled(reason, state)
            except Exception as e:
                # TODO: this swallows every error in on_delivery_settled, which mean we
                #  1. only handle errors we care about in the callback
                #  2. ignore errors we don't care
                #  We should revisit this:
                #  -- "Errors should never pass silently." unless "Unless explicitly silenced."
                _LOGGER.warning("Message 'on_send_complete' callback failed: %r", e)


class SenderLink(Link):

    def __init__(self, session, handle, target_address, **kwargs):
        name = kwargs.pop('name', None) or str(uuid.uuid4())
        role = Role.Sender
        if 'source_address' not in kwargs:
            kwargs['source_address'] = "sender-link-{}".format(name)
        super(SenderLink, self).__init__(session, handle, name, role, target_address=target_address, **kwargs)
        self._unsent_messages = []

    def _incoming_attach(self, frame):
        super(SenderLink, self)._incoming_attach(frame)
        self.current_link_credit = self.link_credit
        self._outgoing_flow()
        self._update_pending_delivery_status()

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
        if self.current_link_credit > 0:
            self._send_unsent_messages()

    def _outgoing_transfer(self, delivery):
        output = bytearray()
        encode_payload(output, delivery.message)
        delivery_count = self.delivery_count + 1
        delivery.frame = {
            'handle': self.handle,
            'delivery_tag': struct.pack('>I', abs(delivery_count)),
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
            # TODO: whether we should move frame tracing into centralized place e.g. connection.py
            _LOGGER.info("-> %r", TransferFrame(delivery_id='<pending>', **delivery.frame), extra=self.network_trace_params)
        self._session._outgoing_transfer(delivery)
        if delivery.transfer_state == SessionTransferState.OKAY:
            self.delivery_count = delivery_count
            self.current_link_credit -= 1
            delivery.sent = True
            if delivery.settled:
                delivery.on_settled(LinkDeliverySettleReason.SETTLED, None)
            else:
                self._pending_deliveries[delivery.frame['delivery_id']] = delivery
        elif delivery.transfer_state == SessionTransferState.ERROR:
            # TODO: This shouldn't raise here - we should call the delivery callback
            raise ValueError("Message failed to send")
        if self.current_link_credit <= 0:
            self.current_link_credit = self.link_credit
            self._outgoing_flow()

    def _incoming_disposition(self, frame):
        if not frame[3]:  # settled
            return
        range_end = (frame[2] or frame[1]) + 1  # first or last
        settled_ids = [i for i in range(frame[1], range_end)]
        for settled_id in settled_ids:
            delivery = self._pending_deliveries.pop(settled_id, None)
            if delivery:
                delivery.on_settled(LinkDeliverySettleReason.DISPOSITION_RECEIVED, frame[4])  # state

    def _update_pending_delivery_status(self):  # TODO
        now = time.time()
        expired = []
        for delivery in self._pending_deliveries.values():
            if delivery.timeout and (now - delivery.start) >= delivery.timeout:
                expired.append(delivery.frame['delivery_id'])
                delivery.on_settled(LinkDeliverySettleReason.TIMEOUT, None)
        self._pending_deliveries = {i: d for i, d in self._pending_deliveries.items() if i not in expired}

    def _send_unsent_messages(self):
        unsent = []
        for delivery in self._unsent_messages:
            if not delivery.sent:
                self._outgoing_transfer(delivery)
                if not delivery.sent:
                    unsent.append(delivery)
        self._unsent_messages = unsent

    def send_transfer(self, message, **kwargs):
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
            link=self,
            message=message,
            settled=settled,
        )
        if self.current_link_credit == 0:
            self._unsent_messages.append(delivery)
        else:
            self._outgoing_transfer(delivery)
            if not delivery.sent:
                self._unsent_messages.append(delivery)
        return delivery

    def cancel_transfer(self, delivery):
        try:
            delivery = self._pending_deliveries.pop(delivery.frame['delivery_id'])
            delivery.on_settled(LinkDeliverySettleReason.CANCELLED, None)
            return
        except KeyError:
            pass
        # todo remove from unset messages
        raise ValueError("No pending delivery with ID '{}' found.".format(delivery.frame['delivery_id']))

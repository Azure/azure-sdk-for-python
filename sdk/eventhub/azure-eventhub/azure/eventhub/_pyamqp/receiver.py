#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

import uuid
import logging
from io import BytesIO

from ._decode import decode_payload
from .constants import DEFAULT_LINK_CREDIT, Role
from .endpoints import Target
from .link import Link
from .message import Message, Properties, Header
from .constants import (
    DEFAULT_LINK_CREDIT,
    SessionState,
    SessionTransferState,
    LinkDeliverySettleReason,
    LinkState
)
from .performatives import (
    AttachFrame,
    DetachFrame,
    TransferFrame,
    DispositionFrame,
    FlowFrame,
)


_LOGGER = logging.getLogger(__name__)


class ReceiverLink(Link):

    def __init__(self, session, handle, source_address, **kwargs):
        name = kwargs.pop('name', None) or str(uuid.uuid4())
        role = Role.Receiver
        if 'target_address' not in kwargs:
            kwargs['target_address'] = "receiver-link-{}".format(name)
        super(ReceiverLink, self).__init__(session, handle, name, role, source_address=source_address, **kwargs)
        self.on_message_received = kwargs.get('on_message_received')
        self.on_transfer_received = kwargs.get('on_transfer_received')
        if not self.on_message_received and not self.on_transfer_received:
            raise ValueError("Must specify either a message or transfer handler.")

    def _process_incoming_message(self, frame, message):
        try:
            if self.on_message_received:
                return self.on_message_received(message)
            elif self.on_transfer_received:
                return self.on_transfer_received(frame, message)
        except Exception as e:
            _LOGGER.error("Handler function failed with error: %r", e)
        return None

    def _incoming_attach(self, frame):
        super(ReceiverLink, self)._incoming_attach(frame)
        if frame[9] is None:  # initial_delivery_count
            _LOGGER.info("Cannot get initial-delivery-count. Detaching link")
            self._remove_pending_deliveries()
            self._set_state(LinkState.DETACHED)  # TODO: Send detach now?
        self.delivery_count = frame[9]
        self.current_link_credit = self.link_credit
        self._outgoing_flow()

    def _incoming_transfer(self, frame):
        if self.network_trace:
            _LOGGER.info("<- %r", TransferFrame(*frame), extra=self.network_trace_params)
        self.current_link_credit -= 1
        self.delivery_count += 1
        self.received_delivery_id = frame[1]  # delivery_id
        if not self.received_delivery_id and not self._received_payload:
            pass  # TODO: delivery error
        if self._received_payload or frame[5]:  # more
            self._received_payload.extend(frame[11])
        if not frame[5]:
            if self._received_payload:
                message = decode_payload(memoryview(self._received_payload))
                self._received_payload = bytearray()
            else:
                message = decode_payload(frame[11])
            delivery_state = self._process_incoming_message(frame, message)
            if not frame[4] and delivery_state:  # settled
                self._outgoing_disposition(frame[1], delivery_state)
        if self.current_link_credit <= 0:
            self.current_link_credit = self.link_credit
            self._outgoing_flow()

    def _outgoing_disposition(self, delivery_id, delivery_state):
        disposition_frame = DispositionFrame(
            role=self.role,
            first=delivery_id,
            last=delivery_id,
            settled=True,
            state=delivery_state,
            batchable=None
        )
        if self.network_trace:
            _LOGGER.info("-> %r", DispositionFrame(*disposition_frame), extra=self.network_trace_params)
        self._session._outgoing_disposition(disposition_frame)

    def send_disposition(self, delivery_id, delivery_state=None):
        if self._is_closed:
            raise ValueError("Link already closed.")
        self._outgoing_disposition(delivery_id, delivery_state)

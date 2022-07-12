#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

import uuid
import logging
from typing import Optional, Union, TYPE_CHECKING, Callable

from ._decode import decode_payload
from .endpoints import Source, Target
from .link import Link
from .message import Message, Properties, Header
from .constants import (
    DEFAULT_LINK_CREDIT,
    SessionState,
    SessionTransferState,
    LinkDeliverySettleReason,
    LinkState,
    Role
)
from .performatives import (
    AttachFrame,
    DetachFrame,
    TransferFrame,
    DispositionFrame,
    FlowFrame,
)
from .outcomes import SETTLEMENT_TYPES

if TYPE_CHECKING:
    from .session import Session
_LOGGER = logging.getLogger(__name__)


class ReceiverLink(Link):
    """A definition of a Link that has the predefined role of a receiver."""

    def __init__(
            self,
            *
            session: "Session",
            handle: int,
            source: Union[str, Source],
            on_transfer: Callable[[TransferFrame, Message], Optional[SETTLEMENT_TYPES]],
            target: Optional[Union[str, Target]] = None,
            name: Optional[str] = None,
            **kwargs):
        """Create a new Receiver link.

        This constructor should not be called directly - instead this object will be returned
        from calling :func:~pyamqp.Session.create_receiver_link().

        :param ~pyamqp.Session session: The session to which this link will be established within.
        :param int handle: The next available handle within the session to assign to the link.
        :param source: The source endpoint to connect to and start receiving from. This could
         be just a string address, or a fully formed AMQP 'source' type.
        :paramtype source: Union[str, ~pyamqp.Source]
        :param on_transfer: A callback function to be run with ever incoming Transfer frame and it's
         message payload. Optionally this function can return an Outcome object, in which case the Message
         will be immediately settled. Otherwise if None is returned, the message will not be actively
         settled.
        :paramtype on_transfer: Callable[[TransferFrame, Message], None]
        :keyword target: An optional target for the receiver link. If supplied, it will be used as the
         target address, if omitted a value will be generated in the format 'receiver-link-[name]'.
        :paramtype target: Union[str, ~pyamqp.Target`]
        :keyword str name: An optional name for the receiver link. If omitted, a UUID will be generated.
        """
        name = name or str(uuid.uuid4())
        self._on_transfer = on_transfer
        if not target:
            target = "receiver-link-{}".format(name)
        super().__init__(
            session=session,
            handle=handle,
            name=name,
            role=Role.Receiver,
            source=source,
            target=target,
            **kwargs
        )

    def _incoming_message(
            self,
            frame: TransferFrame,
            message: Message
        ) -> Optional[SETTLEMENT_TYPES]:
        try:
            return self._on_transfer(frame, message)
        except Exception as e:
            _LOGGER.error(
                "Handler function 'on_transfer' failed with error: %r",
                e,
                extra=self.network_trace_params
            )
        return None

    def _incoming_attach(self, frame: AttachFrame) -> None:
        super()._incoming_attach(frame)
        if frame[9] is None:  # initial_delivery_count
            _LOGGER.info("Cannot get initial-delivery-count. Detaching link.", extra=self.network_trace_params)
            self._remove_pending_deliveries()
            self._set_state(LinkState.DETACHED)  # TODO: Send detach now?
        self.delivery_count = frame[9]
        self.current_link_credit = self.link_credit
        self._outgoing_flow()

    def _incoming_transfer(self, frame: TransferFrame) -> None:
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
            delivery_state = self._incoming_message(frame, message)
            if not frame[4] and delivery_state:  # settled
                self._outgoing_disposition(first=frame[1], settled=True, state=delivery_state)
        if self.current_link_credit <= 0:
            self.current_link_credit = self.link_credit
            self._outgoing_flow()

    def _outgoing_disposition(
            self,
            first: int,
            last: Optional[int],
            settled: Optional[bool],
            state: Optional[SETTLEMENT_TYPES],
            batchable: Optional[bool]
    ) -> None:
        disposition_frame = DispositionFrame(
            role=self.role,
            first=first,
            last=last,
            settled=settled,
            state=state,
            batchable=batchable
        )
        if self.network_trace:
            _LOGGER.info("-> %r", DispositionFrame(*disposition_frame), extra=self.network_trace_params)
        self._session._outgoing_disposition(disposition_frame)

    def send_disposition(
            self,
            *,
            first_delivery_id: int,
            last_delivery_id: Optional[int] = None,
            settled: Optional[bool] = None,
            delivery_state: Optional[SETTLEMENT_TYPES] = None,
            batchable: Optional[bool] = None
        ) -> None:
        """Send a message disposition to a received transfer.
        
        :keyword int first_delivery_id: The delivery ID of the message to be settled. If settling a
         range of messages, this will be the ID of the first.
        :keyword int last_delivery_id: If a range of delivery IDs are being settled, this is the last
         ID in the range. Default is None, meaning only the first delivery ID will be settled.
        :keyword bool settled: Whether the disposition indicates that the message is settled.
        :keyword delivery_state: If the message is being settled, the outcome of the settlement.
        :paramtype delivery_state: Union[~pyamqp.Received, ~pyamqp.Rejected, ~pyamqp.Accepted, ~pyamqp.Modified, ~pyamqp.Released]
        :keyword bool batchable:
        :rtype: None
        """
        if self._is_closed:
            raise ValueError("Link already closed.")
        self._outgoing_disposition(
            first_delivery_id,
            last_delivery_id,
            settled,
            delivery_state,
            batchable
        )

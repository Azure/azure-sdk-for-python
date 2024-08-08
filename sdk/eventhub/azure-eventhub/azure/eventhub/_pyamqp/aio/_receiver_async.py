# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import uuid
import logging
import time
from typing import Optional, Union, TYPE_CHECKING, Callable

from .._decode import decode_payload
from ._link_async import Link
from ..constants import LinkState, Role, LinkDeliverySettleReason
from ..performatives import (
    TransferFrame,
    DispositionFrame,
)
from ..outcomes import Received, Accepted, Rejected, Released, Modified

if TYPE_CHECKING:
    from ..message import _MessageDelivery


_LOGGER = logging.getLogger(__name__)

class PendingDisposition(object):
    def __init__(self, **kwargs):
        self.sent = kwargs.get("sent", False)
        self.frame = kwargs.get("frame", None)
        self.on_delivery_settled = kwargs.get("on_delivery_settled")
        self.start = time.time()
        self.transfer_state = kwargs.get("transfer_state", None)
        self.timeout = kwargs.get("timeout")
        self.settled = kwargs.get("settled", False)
        self._network_trace_params = kwargs.get('network_trace_params')

    async def on_settled(self, reason, state):
        if self.on_delivery_settled and not self.settled:
            try:
                await self.on_delivery_settled(reason, state)
            except Exception as e:  # pylint:disable=broad-except
                _LOGGER.warning(
                    "Disposition 'on_delivery_settled' callback failed: %r",
                    e,
                    extra=self._network_trace_params
                )
        self.settled = True

class ReceiverLink(Link):
    def __init__(self, session, handle, source_address, **kwargs):
        name = kwargs.pop("name", None) or str(uuid.uuid4())
        role = Role.Receiver
        if "target_address" not in kwargs:
            kwargs["target_address"] = "receiver-link-{}".format(name)
        super(ReceiverLink, self).__init__(session, handle, name, role, source_address=source_address, **kwargs)
        self._on_transfer = kwargs.pop("on_transfer")
        self._received_payload = bytearray()
        self._first_frame = None
        self._pending_receipts = []

    @classmethod
    def from_incoming_frame(cls, session, handle, frame):
        # TODO: Assuming we establish all links for now...
        # check link_create_from_endpoint in C lib
        raise NotImplementedError("Pending")

    async def _process_incoming_message(self, frame, message):
        try:
            return await self._on_transfer(frame, message)
        except Exception as e:  # pylint: disable=broad-except
            _LOGGER.error("Transfer callback function failed with error: %r", e, extra=self.network_trace_params)
        return None

    async def _incoming_attach(self, frame):
        await super(ReceiverLink, self)._incoming_attach(frame)
        if frame[9] is None:  # initial_delivery_count
            _LOGGER.info("Cannot get initial-delivery-count. Detaching link", extra=self.network_trace_params)
            await self._remove_pending_receipts(frame)
            await self._set_state(LinkState.DETACHED)  # TODO: Send detach now?
        self.delivery_count = frame[9]
        self.current_link_credit = self.link_credit
        await self._outgoing_flow()

    async def _incoming_flow(self, frame):
        drain = frame[8]  # drain
        async with self._drain_lock:
            # If the link is in drain mode, trigger if the drain is received
            if self._drain_state and drain:
                self._drain_state = False
                self._received_drain_response = True
                self.current_link_credit = frame[6]  # link_credit

    async def _incoming_transfer(self, frame):
        if self.network_trace:
            _LOGGER.debug("<- %r", TransferFrame(payload=b"***", *frame[:-1]), extra=self.network_trace_params)
        self.received_delivery_id = frame[1] # delivery_id
        # If more is false --> this is the last frame of the message
        if not frame[5]:
            self.delivery_count += 1
            self.current_link_credit -= 1
        if self.received_delivery_id is not None:
            self._first_frame = frame
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
            delivery_state = await self._process_incoming_message(self._first_frame, message)
            if not frame[4] and delivery_state:  # settled
                await self._outgoing_disposition(
                    first=self._first_frame[1],
                    last=self._first_frame[1],
                    settled=True,
                    state=delivery_state,
                    batchable=None
                )

    async def _outgoing_disposition(
        self,
        first: int,
        last: Optional[int],
        settled: Optional[bool],
        state: Optional[Union[Received, Accepted, Rejected, Released, Modified]],
        batchable: Optional[bool],
        *,
        on_disposition: Optional[Callable] = None,
    ):
        disposition_frame = DispositionFrame(
            role=self.role, first=first, last=last, settled=settled, state=state, batchable=batchable
        )
        if self.network_trace:
            _LOGGER.debug("-> %r", DispositionFrame(*disposition_frame), extra=self.network_trace_params)

        # If trying to settle a message, keep track of the disposition
        if on_disposition:
            delivery = PendingDisposition(
                on_delivery_settled = on_disposition,
                frame=disposition_frame,
                settled=settled,
                transfer_state=state,
                start=time.time(),
                sent=True,
            )
            self._pending_receipts.append(delivery)

        await self._session._outgoing_disposition(disposition_frame) # pylint: disable=protected-access

    async def _incoming_disposition(self, frame):
        range_end = (frame[2] or frame[1]) + 1  # first or last
        settled_ids = list(range(frame[1], range_end))
        unsettled = []
        for delivery in self._pending_receipts:
            if delivery.sent and delivery.frame[1] in settled_ids:
                await delivery.on_settled(LinkDeliverySettleReason.DISPOSITION_RECEIVED, frame[4])  # state
                continue
            unsettled.append(delivery)
        self._pending_receipts = unsettled

    async def attach(self):
        await super().attach()
        self._received_payload = bytearray()

    async def _remove_pending_receipts(self, frame):

        # TODO: Coming from detach with an error do we want to raise in the callback?
        # for delivery in self._pending_receipts:
        #     await delivery.on_settled(LinkDeliverySettleReason.NOT_DELIVERED, frame[2])
        self._pending_receipts = []

    async def _incoming_detach(self, frame):
        await super(ReceiverLink, self)._incoming_detach(frame)
        await self._remove_pending_receipts(frame)

    async def send_disposition(
        self,
        *,
        wait: Union[bool, float] = False, # pylint: disable=unused-argument
        first_delivery_id: int,
        last_delivery_id: Optional[int] = None,
        settled: Optional[bool] = None,
        delivery_state: Optional[Union[Received, Accepted, Rejected, Released, Modified]] = None,
        batchable: Optional[bool] = None,
        on_disposition: Optional[Callable] = None,
    ):
        self._check_if_closed()
        await self._outgoing_disposition(
            first_delivery_id,
            last_delivery_id,
            settled,
            delivery_state,
            batchable,
            on_disposition=on_disposition
        )

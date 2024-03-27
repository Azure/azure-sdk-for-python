# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import uuid
import logging
import time
from functools import partial
from typing import Optional, Union, TYPE_CHECKING

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
        self.message = kwargs.get("message")
        self.sent = False
        self.frame = None
        self.on_delivery_settled = kwargs.get("on_delivery_settled")
        self.start = time.time()
        self.transfer_state = None
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
            await self._set_state(LinkState.DETACHED)  # TODO: Send detach now?
        self.delivery_count = frame[9]
        self.current_link_credit = self.link_credit
        await self._outgoing_flow()

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
            # TODO: investigate if the following is needed
            if not frame[4] and delivery_state:  # settled
                await self._outgoing_disposition(
                    first=self._first_frame[1],
                    last=self._first_frame[1],
                    settled=True,
                    state=delivery_state,
                    batchable=None
                )

    async def _wait_for_response(self, wait: Union[bool, float]) -> None:
        # TODO: Can we remove this method?
        if wait is True:
            await self._session._connection.listen(wait=False) # pylint: disable=protected-access
            if self.state == LinkState.ERROR:
                if self._error:
                    raise self._error
        elif wait:
            await self._session._connection.listen(wait=wait) # pylint: disable=protected-access
            if self.state == LinkState.ERROR:
                if self._error:
                    raise self._error

    async def _outgoing_disposition(
        self,
        first: int,
        last: Optional[int],
        settled: Optional[bool],
        state: Optional[Union[Received, Accepted, Rejected, Released, Modified]],
        batchable: Optional[bool],
        *,
        message: Optional["_MessageDelivery"] = None,
        on_disposition: Optional[callable] = None,
    ):
        disposition_frame = DispositionFrame(
            role=self.role, first=first, last=last, settled=settled, state=state, batchable=batchable
        )

        if self.network_trace:
            _LOGGER.debug("-> %r", DispositionFrame(*disposition_frame), extra=self.network_trace_params)
        await self._session._outgoing_disposition(disposition_frame) # pylint: disable=protected-access

        # If trying to settle a message, keep track of the disposition
        if message:
            delivery = PendingDisposition(
                message = message,
                on_delivery_settled = on_disposition,
            )
            delivery.frame = disposition_frame
            delivery.settled = settled
            delivery.transfer_state = state
            delivery.start = time.time()
            delivery.sent = True

            self._pending_receipts.append(delivery)

    async def _incoming_disposition(self, frame):
        # If delivery_id is not settled, return
        if not frame[3]:  # settled
            return
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

    async def send_disposition(
        self,
        *,
        wait: Union[bool, float] = False,
        first_delivery_id: int,
        last_delivery_id: Optional[int] = None,
        settled: Optional[bool] = None,
        delivery_state: Optional[Union[Received, Accepted, Rejected, Released, Modified]] = None,
        batchable: Optional[bool] = None,
        message_delivery: Optional["_MessageDelivery"] = None,
        on_disposition: Optional[callable] = None,
    ):
        if self._is_closed:
            raise ValueError("Link already closed.")
        await self._outgoing_disposition(first_delivery_id, last_delivery_id, settled, delivery_state, batchable, message=message_delivery, on_disposition=on_disposition)
        if not settled:
            await self._wait_for_response(wait)
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import uuid
import logging
from typing import Optional, Union

from .._decode import decode_payload
from ._link_async import Link
from ..constants import LinkState, Role
from ..performatives import (
    TransferFrame,
    DispositionFrame,
)
from ..outcomes import Received, Accepted, Rejected, Released, Modified
from ..error import AMQPException, ErrorCondition


_LOGGER = logging.getLogger(__name__)


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
        self._received_delivery_tags = set()

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
        self.received_delivery_id = frame[1]  # delivery_id
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
            self._received_delivery_tags.add(self._first_frame[2])
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
                    delivery_tag=self._first_frame[2],
                    settled=True,
                    state=delivery_state,
                    batchable=None,
                )

    async def _wait_for_response(self, wait: Union[bool, float]) -> None:
        if wait is True:
            await self._session._connection.listen(wait=False)  # pylint: disable=protected-access
            if self.state == LinkState.ERROR:
                if self._error:
                    raise self._error
        elif wait:
            await self._session._connection.listen(wait=wait)  # pylint: disable=protected-access
            if self.state == LinkState.ERROR:
                if self._error:
                    raise self._error

    async def _outgoing_disposition(
        self,
        first: int,
        last: Optional[int],
        delivery_tag: bytes,
        settled: Optional[bool],
        state: Optional[Union[Received, Accepted, Rejected, Released, Modified]],
        batchable: Optional[bool],
    ):
        disposition_frame = DispositionFrame(
            role=self.role, first=first, last=last, settled=settled, state=state, batchable=batchable
        )
        if delivery_tag not in self._received_delivery_tags:
            raise AMQPException(condition=ErrorCondition.IllegalState, description="Delivery tag not found.")

        if self.network_trace:
            _LOGGER.debug("-> %r", DispositionFrame(*disposition_frame), extra=self.network_trace_params)
        await self._session._outgoing_disposition(disposition_frame)  # pylint: disable=protected-access
        self._received_delivery_tags.remove(delivery_tag)

    async def attach(self):
        await super().attach()
        self._received_payload = bytearray()

    async def send_disposition(
        self,
        *,
        wait: Union[bool, float] = False,
        first_delivery_id: int,
        last_delivery_id: Optional[int] = None,
        delivery_tag: bytes,
        settled: Optional[bool] = None,
        delivery_state: Optional[Union[Received, Accepted, Rejected, Released, Modified]] = None,
        batchable: Optional[bool] = None
    ):
        if self._is_closed:
            raise ValueError("Link already closed.")
        await self._outgoing_disposition(
            first_delivery_id, last_delivery_id, delivery_tag, settled, delivery_state, batchable
        )
        if not settled:
            await self._wait_for_response(wait)

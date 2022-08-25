#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

import uuid
import logging
from typing import Optional, Union

from .._decode import decode_payload
from ..endpoints import Target
from ._link_async import Link
from ..message import Message, Properties, Header
from ..constants import (
    DEFAULT_LINK_CREDIT,
    SessionState,
    SessionTransferState,
    LinkDeliverySettleReason,
    LinkState,
    Role
)
from ..performatives import (
    AttachFrame,
    DetachFrame,
    TransferFrame,
    DispositionFrame,
    FlowFrame,
)
from ..outcomes import (
    Received,
    Accepted,
    Rejected,
    Released,
    Modified
)


_LOGGER = logging.getLogger(__name__)


class ReceiverLink(Link):

    def __init__(self, session, handle, source_address, **kwargs):
        name = kwargs.pop('name', None) or str(uuid.uuid4())
        role = Role.Receiver
        if 'target_address' not in kwargs:
            kwargs['target_address'] = "receiver-link-{}".format(name)
        super(ReceiverLink, self).__init__(session, handle, name, role, source_address=source_address, **kwargs)
        self._on_transfer = kwargs.pop('on_transfer')
        self._received_payload = bytearray()

    async def _process_incoming_message(self, frame, message):
        try:
            return await self._on_transfer(frame, message)
        except Exception as e:
            _LOGGER.error("Handler function failed with error: %r", e)
        return None

    async def _incoming_attach(self, frame):
        await super(ReceiverLink, self)._incoming_attach(frame)
        if frame[9] is None:  # initial_delivery_count
            _LOGGER.info("Cannot get initial-delivery-count. Detaching link")
            await self._set_state(LinkState.DETACHED)  # TODO: Send detach now?
        self.delivery_count = frame[9]
        self.current_link_credit = self.link_credit
        await self._outgoing_flow()

    async def _incoming_transfer(self, frame):
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
                if self.network_trace:
                    _LOGGER.info("   %r", message, extra=self.network_trace_params)
            delivery_state = await self._process_incoming_message(frame, message)
            if not frame[4] and delivery_state:  # settled
                await self._outgoing_disposition(first=frame[1], settled=True, state=delivery_state)

    async def _wait_for_response(self, wait: Union[bool, float]) -> None:
        if wait == True:
            await self._session._connection.listen(wait=False)
            if self.state == LinkState.ERROR:
                raise self._error    
        elif wait:
            await self._session._connection.listen(wait=wait)
            if self.state == LinkState.ERROR:
                raise self._error   

    async def _outgoing_disposition(
            self,
            first: int,
            last: Optional[int],
            settled: Optional[bool],
            state: Optional[Union[Received, Accepted, Rejected, Released, Modified]],
            batchable: Optional[bool]
    ):
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
        await self._session._outgoing_disposition(disposition_frame)

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
            batchable: Optional[bool] = None
        ):
        if self._is_closed:
            raise ValueError("Link already closed.")
        await self._outgoing_disposition(
            first_delivery_id,
            last_delivery_id,
            settled,
            delivery_state,
            batchable
        )
        await self._wait_for_response(wait)

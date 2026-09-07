# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import time
import uuid
import logging
from typing import Any, Dict, List, Optional, Union

from .._decode import decode_payload
from ._link_async import Link
from ..constants import LinkState, Role
from ..performatives import (
    TransferFrame,
    DispositionFrame,
)
from ..outcomes import Received, Accepted, Rejected, Released, Modified
from ..error import AMQPException, ErrorCondition, MessageSettlementUnconfirmed
from ..constants import SEND_DISPOSITION_ACCEPT
from ..receiver import DEFAULT_SETTLEMENT_OUTCOME_TIMEOUT, check_disposition_outcome, outcome_name


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
        # Awaited settlements by delivery ID; empty on the default fire-and-forget path.
        self._pending_dispositions: Dict[int, Dict[str, Any]] = {}

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

    async def _incoming_disposition(self, frame):
        # Nothing to resolve unless an outcome is being awaited.
        if not self._pending_dispositions:
            return
        # Our deliveries are settled by the remote sender; ignore anything else.
        if frame[0] != Role.Sender:
            return
        # An unsettled disposition does not confirm settlement, even when it carries an
        # outcome -- rcv-settle-mode Second is only satisfied once the sender settles.
        if not frame[3]:  # settled
            return
        outcome = frame[4]  # state
        last_delivery_id = frame[2] if frame[2] is not None else frame[1]
        # `first`/`last` are peer-controlled 32-bit values: walk what we track, not the range.
        for delivery_id, pending in self._pending_dispositions.items():
            if frame[1] <= delivery_id <= last_delivery_id:
                pending["outcome"] = outcome
                pending["settled"] = True

    async def _wait_for_disposition_outcome(
        self, delivery_ids: List[int], timeout: Optional[float], expected: str = SEND_DISPOSITION_ACCEPT
    ) -> None:
        """Wait until the remote endpoint reports a terminal outcome for every delivery.

        Raises `MessageSettlementUnconfirmed` if no outcome arrives, so the caller can
        distinguish "the remote endpoint said no" from "we do not know".

        :param list[int] delivery_ids: The delivery IDs awaiting an outcome.
        :param timeout: Seconds to wait before giving up on the outcome.
        :type timeout: float or None
        :param str expected: The outcome name the service is expected to echo back, derived from
         the delivery state that was sent.
        :rtype: None
        """
        timeout = timeout or DEFAULT_SETTLEMENT_OUTCOME_TIMEOUT
        start_time = time.time()
        try:
            while not all(self._pending_dispositions[delivery_id]["settled"] for delivery_id in delivery_ids):
                if (time.time() - start_time) >= timeout:
                    raise MessageSettlementUnconfirmed(
                        condition=ErrorCondition.ClientError,
                        description=(
                            "Timed out waiting for the settlement outcome. The settlement was sent but "
                            "not confirmed, so it may not have been applied."
                        ),
                    )
                await self._session._connection.listen(wait=False)  # pylint: disable=protected-access
                if self.state in (LinkState.DETACHED, LinkState.ERROR):
                    # Unconfirmed, not failed: only this routes the caller to the mgmt-link fallback.
                    raise MessageSettlementUnconfirmed(
                        condition=ErrorCondition.LinkDetachForced,
                        description=(
                            "The link detached before the settlement was confirmed, so it may not have been applied."
                        ),
                    ) from self._error
            for delivery_id in delivery_ids:
                check_disposition_outcome(delivery_id, self._pending_dispositions[delivery_id]["outcome"], expected)
        finally:
            for delivery_id in delivery_ids:
                self._pending_dispositions.pop(delivery_id, None)

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
        batchable: Optional[bool] = None,
        await_outcome: bool = False,
        outcome_timeout: Optional[float] = None
    ):
        """Send a disposition frame for one or more received deliveries.

        With ``await_outcome=True`` the disposition is sent unsettled and this call waits until
        the remote endpoint reports a terminal outcome, raising unless that outcome matches the one
        requested (the service echoes what it applied: `modified` for abandon/defer, `rejected` for
        dead-letter). A `rejected` outcome carrying an error always raises.
        This requires the link to have been attached with
        ``rcv_settle_mode=ReceiverSettleMode.Second``.

        :keyword wait: How long to block waiting for the frame to be sent when the disposition is
         sent unsettled and ``await_outcome`` is `False`.
        :paramtype wait: bool or float
        :keyword int first_delivery_id: The first delivery ID in the range to settle.
        :keyword last_delivery_id: The last delivery ID in the range, or `None` to settle only
         ``first_delivery_id``.
        :paramtype last_delivery_id: int or None
        :keyword bytes delivery_tag: The delivery tag of the delivery being settled.
        :keyword settled: Whether the disposition itself is pre-settled. Must not be `True` when
         ``await_outcome`` is `True`.
        :paramtype settled: bool or None
        :keyword delivery_state: The terminal outcome to apply to the deliveries.
        :paramtype delivery_state: ~pyamqp.outcomes.Received or ~pyamqp.outcomes.Accepted or
         ~pyamqp.outcomes.Rejected or ~pyamqp.outcomes.Released or ~pyamqp.outcomes.Modified or None
        :keyword batchable: The batchable flag on the disposition frame.
        :paramtype batchable: bool or None
        :keyword bool await_outcome: Whether to wait for the remote endpoint to confirm the
         settlement. Defaults to `False`, which sends the disposition pre-settled so no outcome
         is observable.
        :keyword outcome_timeout: Seconds to wait for the outcome when ``await_outcome`` is `True`.
        :paramtype outcome_timeout: float or None
        """
        if self._is_closed:
            raise ValueError("Link already closed.")
        if not await_outcome:
            await self._outgoing_disposition(
                first_delivery_id, last_delivery_id, delivery_tag, settled, delivery_state, batchable
            )
            if not settled:
                await self._wait_for_response(wait)
            return

        if settled:
            raise ValueError("A settlement outcome cannot be awaited when the disposition is pre-settled.")
        last = last_delivery_id if last_delivery_id is not None else first_delivery_id
        if last < first_delivery_id:
            # An empty range would register nothing, then "confirm" instantly: a false success.
            raise ValueError("last_delivery_id cannot be lower than first_delivery_id.")
        delivery_ids = list(range(first_delivery_id, last + 1))
        for delivery_id in delivery_ids:
            self._pending_dispositions[delivery_id] = {"settled": False, "outcome": None}
        try:
            await self._outgoing_disposition(
                first_delivery_id, last_delivery_id, delivery_tag, settled, delivery_state, batchable
            )
        except BaseException:  # pylint: disable=broad-except
            for delivery_id in delivery_ids:
                self._pending_dispositions.pop(delivery_id, None)
            raise
        await self._wait_for_disposition_outcome(delivery_ids, outcome_timeout, outcome_name(delivery_state))

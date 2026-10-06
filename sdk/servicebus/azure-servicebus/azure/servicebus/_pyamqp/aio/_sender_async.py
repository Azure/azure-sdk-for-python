# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import struct
import uuid
import logging
import time
import asyncio # pylint:disable=do-not-import-asyncio

from .._encode import encode_payload
from ._link_async import Link
from ..constants import SessionTransferState, LinkDeliverySettleReason, LinkState, Role, SenderSettleMode, SessionState
from ..error import AMQPLinkError, ErrorCondition, MessageException

_LOGGER = logging.getLogger(__name__)


class PendingDelivery(object):
    def __init__(self, **kwargs):
        self.message = kwargs.get("message")
        self.sent = False
        self.frame = None
        self.early_disposition_received = False
        self.early_disposition_state = None
        self.abort_pending = False
        self.abort_requested = False
        self.cancel_requested = False
        self._inflight_more = None
        self.on_delivery_settled = kwargs.get("on_delivery_settled")
        self.start = time.time()
        self.transfer_state = None
        self.timeout = kwargs.get("timeout")
        self.settled = kwargs.get("settled", False)
        self._network_trace_params = kwargs.get("network_trace_params")

    async def on_settled(self, reason, state):
        if self.on_delivery_settled and not self.settled:
            try:
                await self.on_delivery_settled(reason, state)
            except Exception as e:  # pylint:disable=broad-except
                _LOGGER.warning("Message 'on_send_complete' callback failed: %r", e, extra=self._network_trace_params)
        self.settled = True


class SenderLink(Link):
    def __init__(self, session, handle, target_address, **kwargs):
        name = kwargs.pop("name", None) or str(uuid.uuid4())
        role = Role.Sender
        if "source_address" not in kwargs:
            kwargs["source_address"] = "sender-link-{}".format(name)
        super(SenderLink, self).__init__(session, handle, name, role, target_address=target_address, **kwargs)
        self._pending_deliveries = []
        self._updating_deliveries = False
        self._update_requested = False

    @classmethod
    def from_incoming_frame(cls, session, handle, frame):
        # TODO: Assuming we establish all links for now...
        # check link_create_from_endpoint in C lib
        raise NotImplementedError("Pending")

    # In theory we should not need to purge pending deliveries on attach/dettach - as a link should
    # be resume-able, however this is not yet supported.
    async def _incoming_attach(self, frame):
        try:
            await super(SenderLink, self)._incoming_attach(frame)
        except AMQPLinkError:
            await self._remove_pending_deliveries()
            raise
        self.current_link_credit = self.link_credit
        await self._outgoing_flow()
        await self.update_pending_deliveries()

    async def _incoming_detach(self, frame):
        await super(SenderLink, self)._incoming_detach(frame)
        await self._remove_pending_deliveries()

    async def _incoming_flow(self, frame):
        rcv_link_credit = frame[6]  # link_credit
        rcv_delivery_count = frame[5]  # delivery_count
        if frame[4] is not None:  # handle
            if rcv_link_credit is None or rcv_delivery_count is None:
                _LOGGER.info(
                    "Unable to get link-credit or delivery-count from incoming ATTACH. Detaching link.",
                    extra=self.network_trace_params,
                )
                await self._remove_pending_deliveries()
                await self._set_state(LinkState.DETACHED)  # TODO: Send detach now?
            else:
                self.current_link_credit = rcv_delivery_count + rcv_link_credit - self.delivery_count
        await self.update_pending_deliveries()

    async def _outgoing_transfer(self, delivery):
        delivery_count = self.delivery_count + 1
        if not delivery.frame or not delivery.frame["more"]:
            output = bytearray()
            try:
                encode_payload(output, delivery.message)
            except Exception:
                if delivery in self._pending_deliveries:
                    self._pending_deliveries.remove(delivery)
                raise
            delivery.frame = {
                "handle": self.handle,
                "delivery_tag": struct.pack(">I", abs(delivery_count)),
                "message_format": delivery.message._code,  # pylint:disable=protected-access
                "settled": delivery.settled,
                "more": False,
                "rcv_settle_mode": None,
                "state": None,
                "resume": None,
                "aborted": None,
                "batchable": None,
                "payload": output,
            }
        sent_and_settled = False
        try:
            await self._session._outgoing_transfer(  # pylint:disable=protected-access
                delivery, self.network_trace_params if self.network_trace else None
            )
        finally:
            if delivery.transfer_state == SessionTransferState.OKAY and not delivery.sent:
                self.delivery_count = delivery_count
                self.current_link_credit -= 1
                delivery.sent = True
                if delivery.settled:
                    await delivery.on_settled(LinkDeliverySettleReason.SETTLED, None)
                    sent_and_settled = True
                elif delivery.early_disposition_received:
                    await delivery.on_settled(
                        LinkDeliverySettleReason.DISPOSITION_RECEIVED, delivery.early_disposition_state
                    )
                    sent_and_settled = True
                if sent_and_settled and delivery in self._pending_deliveries:
                    self._pending_deliveries.remove(delivery)
            await self._session._notify_discarding_links()  # pylint: disable=protected-access
        # elif delivery.transfer_state == SessionTransferState.ERROR:
        # TODO: Session wasn't mapped yet - re-adding to the outgoing delivery queue?
        return sent_and_settled

    async def _incoming_disposition(self, frame):
        if not frame[3]:  # settled
            return
        range_end = (frame[2] or frame[1]) + 1  # first or last
        settled_ids = list(range(frame[1], range_end))
        for delivery in list(self._pending_deliveries):
            if delivery.frame and delivery.frame.get("delivery_id") in settled_ids:
                if not delivery.sent:
                    delivery.early_disposition_received = True
                    delivery.early_disposition_state = frame[4]
                else:
                    await delivery.on_settled(LinkDeliverySettleReason.DISPOSITION_RECEIVED, frame[4])  # state
                    if delivery in self._pending_deliveries:
                        self._pending_deliveries.remove(delivery)

    async def _remove_pending_deliveries(self):
        futures = []
        for delivery in self._pending_deliveries:
            futures.append(asyncio.ensure_future(delivery.on_settled(LinkDeliverySettleReason.NOT_DELIVERED, None)))
        await asyncio.gather(*futures)
        self._pending_deliveries = []

    async def _on_session_state_change(self):
        if self._session.state == SessionState.DISCARDING:
            await self._remove_pending_deliveries()
        await super()._on_session_state_change()

    async def update_pending_deliveries(self):
        if self._updating_deliveries:
            self._update_requested = True
            return
        self._updating_deliveries = True
        try:
            if self.current_link_credit <= 0:
                self.current_link_credit = self.link_credit
                await self._outgoing_flow()
            now = time.time()
            blocked = False
            index = 0
            while index < len(self._pending_deliveries):
                delivery = self._pending_deliveries[index]
                if not delivery.abort_pending and delivery.timeout and (now - delivery.start) >= delivery.timeout:
                    if not delivery.frame or not delivery.frame["more"]:
                        self._pending_deliveries.pop(index)
                        await delivery.on_settled(LinkDeliverySettleReason.TIMEOUT, None)
                        continue
                    delivery.abort_pending = True
                    delivery.frame["aborted"] = True
                    delivery.frame["payload"] = b""
                    await delivery.on_settled(LinkDeliverySettleReason.TIMEOUT, None)
                    if delivery not in self._pending_deliveries:
                        index = 0
                        continue
                    index = self._pending_deliveries.index(delivery)
                if not delivery.sent and not blocked:
                    try:
                        sent_and_settled = await self._outgoing_transfer(delivery)
                    except asyncio.CancelledError:
                        if delivery in self._pending_deliveries and not delivery.sent:
                            if delivery.frame and delivery.frame["more"]:
                                delivery.abort_pending = True
                                delivery.frame["aborted"] = True
                                delivery.frame["payload"] = b""
                            elif not delivery.frame or "delivery_id" not in delivery.frame:
                                delivery.cancel_requested = True
                                self._pending_deliveries.remove(delivery)
                            await delivery.on_settled(LinkDeliverySettleReason.CANCELLED, None)
                        raise
                    if delivery not in self._pending_deliveries:
                        index = 0
                        continue
                    index = self._pending_deliveries.index(delivery)
                    if sent_and_settled or (
                        delivery.abort_pending and delivery.transfer_state == SessionTransferState.OKAY
                    ):
                        self._pending_deliveries.pop(index)
                        continue
                if delivery.transfer_state == SessionTransferState.BUSY or delivery.abort_pending:
                    blocked = True
                    if (
                        delivery.abort_pending
                        and delivery.transfer_state == SessionTransferState.BUSY
                        and self._session.remote_incoming_window > 0
                        and self._session.outgoing_window > 0
                    ):
                        self._update_requested = True
                index += 1
        finally:
            self._updating_deliveries = False
        if self._update_requested:
            self._update_requested = False
            await self.update_pending_deliveries()

    async def send_transfer(self, message, *, send_async=False, **kwargs):
        self._check_if_closed()
        if self.state != LinkState.ATTACHED:
            raise AMQPLinkError(condition=ErrorCondition.ClientError, description="Link is not attached.")
        settled = self.send_settle_mode == SenderSettleMode.Settled
        if self.send_settle_mode == SenderSettleMode.Mixed:
            settled = kwargs.pop("settled", True)
        delivery = PendingDelivery(
            on_delivery_settled=kwargs.get("on_send_complete"),
            timeout=kwargs.get("timeout"),
            message=message,
            settled=settled,
            network_trace_params=self.network_trace_params,
        )
        self._pending_deliveries.append(delivery)
        try:
            if not send_async and self.current_link_credit != 0:
                drain = asyncio.create_task(self.update_pending_deliveries())
                try:
                    await asyncio.shield(drain)
                except asyncio.CancelledError:
                    if delivery in self._pending_deliveries and not delivery.sent:
                        if delivery._inflight_more is not None:  # pylint: disable=protected-access
                            drain.cancel()
                            try:
                                await drain
                            except asyncio.CancelledError:
                                pass
                        else:
                            await self.cancel_transfer(delivery)
                            drain.add_done_callback(self._log_cancelled_send_drain)
                    else:
                        drain.add_done_callback(self._log_cancelled_send_drain)
                    raise
        except Exception:
            if delivery in self._pending_deliveries and not delivery.sent and (
                delivery.frame is None or delivery.transfer_state == SessionTransferState.ERROR
            ):
                self._pending_deliveries.remove(delivery)
            raise
        return delivery

    def _log_cancelled_send_drain(self, drain):
        try:
            drain.result()
        except asyncio.CancelledError:
            return
        except Exception:
            _LOGGER.exception("Queued delivery drain failed after send cancellation.", extra=self.network_trace_params)

    async def cancel_transfer(self, delivery):
        try:
            index = self._pending_deliveries.index(delivery)
        except ValueError:
            raise ValueError("Found no matching pending transfer.") from None
        delivery = self._pending_deliveries[index]
        if delivery.sent:
            raise MessageException(
                ErrorCondition.ClientError,
                message="Transfer cannot be cancelled. Message has already been sent and awaiting disposition.",
            )
        if delivery.abort_pending or delivery.abort_requested:
            raise MessageException(ErrorCondition.ClientError, message="Transfer cancellation is already pending.")
        if delivery._inflight_more is not None:  # pylint: disable=protected-access
            if not delivery._inflight_more:  # pylint: disable=protected-access
                raise MessageException(ErrorCondition.ClientError, message="Final Transfer frame is already in flight.")
            delivery.abort_requested = True
            await delivery.on_settled(LinkDeliverySettleReason.CANCELLED, None)
            return
        if delivery.frame and delivery.frame["more"]:
            delivery.abort_pending = True
            delivery.frame["aborted"] = True
            delivery.frame["payload"] = b""
        else:
            delivery.cancel_requested = True
            self._pending_deliveries.remove(delivery)
        await delivery.on_settled(LinkDeliverySettleReason.CANCELLED, None)

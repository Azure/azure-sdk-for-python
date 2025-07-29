# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from typing import Any, Optional, TYPE_CHECKING
import uuid
import logging

from ..endpoints import Source, Target
from ..constants import DEFAULT_LINK_CREDIT, SessionState, LinkState, Role, SenderSettleMode, ReceiverSettleMode
from ..performatives import (
    AttachFrame,
    DetachFrame,
)

from ..error import AMQPError, ErrorCondition, AMQPLinkError, AMQPLinkRedirect, AMQPConnectionError

if TYPE_CHECKING:
    from ._session_async import Session

_LOGGER = logging.getLogger(__name__)


class Link:  # pylint: disable=too-many-instance-attributes
    """An AMQP Link.

    This object should not be used directly - instead use one of directional
    derivatives: Sender or Receiver.
    """

    def __init__(
        self, session: "Session", handle: int, name: Optional[str] = None, role: bool = Role.Receiver, **kwargs: Any
    ) -> None:
        self.state = LinkState.DETACHED
        self.name = name or str(uuid.uuid4())
        self.handle = handle
        self.remote_handle = None
        self.role = role
        source_address = kwargs["source_address"]
        target_address = kwargs["target_address"]
        self.source = (
            source_address
            if isinstance(source_address, Source)
            else Source(
                address=kwargs["source_address"],
                durable=kwargs.get("source_durable"),
                expiry_policy=kwargs.get("source_expiry_policy"),
                timeout=kwargs.get("source_timeout"),
                dynamic=kwargs.get("source_dynamic"),
                dynamic_node_properties=kwargs.get("source_dynamic_node_properties"),
                distribution_mode=kwargs.get("source_distribution_mode"),
                filters=kwargs.get("source_filters"),
                default_outcome=kwargs.get("source_default_outcome"),
                outcomes=kwargs.get("source_outcomes"),
                capabilities=kwargs.get("source_capabilities"),
            )
        )
        self.target = (
            target_address
            if isinstance(target_address, Target)
            else Target(
                address=kwargs["target_address"],
                durable=kwargs.get("target_durable"),
                expiry_policy=kwargs.get("target_expiry_policy"),
                timeout=kwargs.get("target_timeout"),
                dynamic=kwargs.get("target_dynamic"),
                dynamic_node_properties=kwargs.get("target_dynamic_node_properties"),
                capabilities=kwargs.get("target_capabilities"),
            )
        )
        link_credit = kwargs.get("link_credit")
        self.link_credit = link_credit if link_credit is not None else DEFAULT_LINK_CREDIT
        self.current_link_credit = self.link_credit
        self.send_settle_mode = kwargs.pop("send_settle_mode", SenderSettleMode.Mixed)
        self.rcv_settle_mode = kwargs.pop("rcv_settle_mode", ReceiverSettleMode.First)
        self.unsettled = kwargs.pop("unsettled", None)
        self.incomplete_unsettled = kwargs.pop("incomplete_unsettled", None)
        self.initial_delivery_count = kwargs.pop("initial_delivery_count", 0)
        self.delivery_count = self.initial_delivery_count
        self.received_delivery_id = None
        self.max_message_size = kwargs.pop("max_message_size", None)
        self.remote_max_message_size = None
        self.available = kwargs.pop("available", None)
        self.properties = kwargs.pop("properties", None)
        self.remote_properties = None
        self.offered_capabilities = None
        self.desired_capabilities = kwargs.pop("desired_capabilities", None)

        self.network_trace = kwargs["network_trace"]
        self.network_trace_params = kwargs["network_trace_params"]
        self.network_trace_params["amqpLink"] = self.name
        self._session = session
        self._is_closed = False
        self._on_link_state_change = kwargs.get("on_link_state_change")
        self._on_attach = kwargs.get("on_attach")
        self._error: Optional[AMQPLinkError] = None

    async def __aenter__(self) -> "Link":
        await self.attach()
        return self

    async def __aexit__(self, *args) -> None:
        await self.detach(close=True)

    @classmethod
    def from_incoming_frame(cls, session, handle, frame):
        # check link_create_from_endpoint in C lib
        raise NotImplementedError("Pending")  # TODO: Assuming we establish all links for now...

    def get_state(self) -> LinkState:
        if self._error:
            raise self._error

        return self.state

    def _check_if_closed(self) -> None:
        if self._is_closed:
            if self._error:
                raise self._error
            raise AMQPConnectionError(
                condition=ErrorCondition.InternalError, description="Link already closed."
            ) from None

    async def _set_state(self, new_state: LinkState) -> None:
        """Update the session state.
        :param ~pyamqp.constants.LinkState new_state: The new state.
        :return: None
        :rtype: None
        """
        if new_state is None:
            return
        previous_state = self.state
        self.state = new_state
        _LOGGER.info("Link state changed: %r -> %r", previous_state, new_state, extra=self.network_trace_params)
        try:
            if self._on_link_state_change is not None:
                await self._on_link_state_change(previous_state, new_state)
        except Exception as e:  # pylint: disable=broad-except
            _LOGGER.error("Link state change callback failed: '%r'", e, extra=self.network_trace_params)

    async def _on_session_state_change(self) -> None:
        if self._session.state == SessionState.MAPPED:
            if not self._is_closed and self.state == LinkState.DETACHED:
                await self._outgoing_attach()
                await self._set_state(LinkState.ATTACH_SENT)
        elif self._session.state == SessionState.DISCARDING:
            await self._set_state(LinkState.DETACHED)

    async def _outgoing_attach(self) -> None:
        self.delivery_count = self.initial_delivery_count
        attach_frame = AttachFrame(
            name=self.name,
            handle=self.handle,
            role=self.role,
            send_settle_mode=self.send_settle_mode,
            rcv_settle_mode=self.rcv_settle_mode,
            source=self.source,
            target=self.target,
            unsettled=self.unsettled,
            incomplete_unsettled=self.incomplete_unsettled,
            initial_delivery_count=self.initial_delivery_count if self.role == Role.Sender else None,
            max_message_size=self.max_message_size,
            offered_capabilities=self.offered_capabilities if self.state == LinkState.ATTACH_RCVD else None,
            desired_capabilities=self.desired_capabilities if self.state == LinkState.DETACHED else None,
            properties=self.properties,
        )
        if self.network_trace:
            _LOGGER.debug("-> %r", attach_frame, extra=self.network_trace_params)
        await self._session._outgoing_attach(attach_frame)  # pylint: disable=protected-access

    async def _incoming_attach(self, frame) -> None:
        if self.network_trace:
            _LOGGER.debug("<- %r", AttachFrame(*frame), extra=self.network_trace_params)
        if self._is_closed:
            raise ValueError("Invalid link")
        if not frame[5] or not frame[6]:
            _LOGGER.info("Cannot get source or target. Detaching link", extra=self.network_trace_params)
            await self._set_state(LinkState.DETACHED)
            raise ValueError("Invalid link")
        self.remote_handle = frame[1]  # handle
        self.remote_max_message_size = frame[10]  # max_message_size
        self.offered_capabilities = frame[11]  # offered_capabilities
        self.remote_properties = frame[13]
        if self.state == LinkState.DETACHED:
            await self._set_state(LinkState.ATTACH_RCVD)
        elif self.state == LinkState.ATTACH_SENT:
            await self._set_state(LinkState.ATTACHED)
        if self._on_attach:
            try:
                if frame[5]:
                    frame[5] = Source(*frame[5])
                if frame[6]:
                    frame[6] = Target(*frame[6])
                await self._on_attach(AttachFrame(*frame))
            except Exception as e:  # pylint: disable=broad-except
                _LOGGER.warning("Callback for link attach raised error: %s", e, extra=self.network_trace_params)

    async def _outgoing_flow(self, **kwargs: Any) -> None:
        flow_frame = {
            "handle": self.handle,
            "delivery_count": self.delivery_count,
            "link_credit": self.current_link_credit,
            "available": kwargs.get("available"),
            "drain": kwargs.get("drain"),
            "echo": kwargs.get("echo"),
            "properties": kwargs.get("properties"),
        }
        await self._session._outgoing_flow(flow_frame)  # pylint: disable=protected-access

    async def _incoming_flow(self, frame):
        pass

    async def _incoming_disposition(self, frame):
        pass

    async def _outgoing_detach(self, close: bool = False, error: Optional[AMQPError] = None) -> None:
        detach_frame = DetachFrame(handle=self.handle, closed=close, error=error)
        if self.network_trace:
            _LOGGER.debug("-> %r", detach_frame, extra=self.network_trace_params)
        await self._session._outgoing_detach(detach_frame)  # pylint: disable=protected-access
        if close:
            self._is_closed = True

    async def _incoming_detach(self, frame) -> None:
        if self.network_trace:
            _LOGGER.debug("<- %r", DetachFrame(*frame), extra=self.network_trace_params)
        if self.state == LinkState.ATTACHED:
            await self._outgoing_detach(close=frame[1])  # closed
        elif frame[1] and not self._is_closed and self.state in [LinkState.ATTACH_SENT, LinkState.ATTACH_RCVD]:
            # Received a closing detach after we sent a non-closing detach.
            # In this case, we MUST signal that we closed by reattaching and then sending a closing detach.
            await self._outgoing_attach()
            await self._outgoing_detach(close=True)
        # TODO: on_detach_hook
        if frame[2]:  # error
            # frame[2][0] is condition, frame[2][1] is description, frame[2][2] is info
            condition = frame[2][0]
            error_cls = AMQPLinkRedirect if condition == ErrorCondition.LinkRedirect else AMQPLinkError
            # description and info are optional fields, from the AMQP spec.
            # https://docs.oasis-open.org/amqp/core/v1.0/os/amqp-core-transport-v1.0-os.html#type-error
            description = None if len(frame[2]) < 2 else frame[2][1]
            info = None if len(frame[2]) < 3 else frame[2][2]
            self._error = error_cls(condition=condition, description=description, info=info)
            await self._set_state(LinkState.ERROR)
        else:
            if self.state != LinkState.DETACH_SENT:
                # Handle the case of when the remote side detaches without sending an error.
                # We should detach as per the spec but then retry connecting
                self._error = AMQPLinkError(
                    condition=ErrorCondition.UnknownError, description="Link detached unexpectedly.", retryable=True
                )
            await self._set_state(LinkState.DETACHED)

    async def attach(self) -> None:
        if self._is_closed:
            raise ValueError("Link already closed.")
        await self._outgoing_attach()
        await self._set_state(LinkState.ATTACH_SENT)

    async def detach(self, close: bool = False, error: Optional[AMQPError] = None) -> None:
        if self.state in (LinkState.DETACHED, LinkState.DETACH_SENT, LinkState.ERROR):
            return
        try:
            self._check_if_closed()
            if self.state in [LinkState.ATTACH_SENT, LinkState.ATTACH_RCVD]:
                await self._outgoing_detach(close=close, error=error)
                await self._set_state(LinkState.DETACHED)
            elif self.state == LinkState.ATTACHED:
                await self._outgoing_detach(close=close, error=error)
                await self._set_state(LinkState.DETACH_SENT)
        except Exception as exc:  # pylint: disable=broad-except
            _LOGGER.info("An error occurred when detaching the link: %r", exc, extra=self.network_trace_params)
            await self._set_state(LinkState.DETACHED)

    async def flow(self, *, link_credit: Optional[int] = None, **kwargs) -> None:
        # Reset link credit to the default and flow
        self.current_link_credit = link_credit if link_credit is not None else self.link_credit
        await self._outgoing_flow(**kwargs)

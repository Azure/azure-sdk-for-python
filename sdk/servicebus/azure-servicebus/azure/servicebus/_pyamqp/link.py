#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

import threading
import struct
from typing import Optional
import uuid
import logging
import time
from enum import Enum
from io import BytesIO
from urllib.parse import urlparse

from .endpoints import Source, Target
from .constants import (
    DEFAULT_LINK_CREDIT,
    SessionState,
    SessionTransferState,
    LinkDeliverySettleReason,
    LinkState,
    Role,
    SenderSettleMode,
    ReceiverSettleMode
)
from .performatives import (
    AttachFrame,
    DetachFrame,
    TransferFrame,
    DispositionFrame,
    FlowFrame,
)

from .error import (
    ErrorCondition,
    AMQPLinkError,
    AMQPLinkRedirect,
    AMQPConnectionError
)

_LOGGER = logging.getLogger(__name__)


class Link(object):
    """

    """

    def __init__(self, session, handle, name, role, **kwargs):
        self.state = LinkState.DETACHED
        self.name = name or str(uuid.uuid4())
        self.handle = handle
        self.remote_handle = None
        self.role = role
        source_address = kwargs['source_address']
        target_address = kwargs["target_address"]
        self.source = source_address if isinstance(source_address, Source) else Source(
            address=kwargs['source_address'],
            durable=kwargs.get('source_durable'),
            expiry_policy=kwargs.get('source_expiry_policy'),
            timeout=kwargs.get('source_timeout'),
            dynamic=kwargs.get('source_dynamic'),
            dynamic_node_properties=kwargs.get('source_dynamic_node_properties'),
            distribution_mode=kwargs.get('source_distribution_mode'),
            filters=kwargs.get('source_filters'),
            default_outcome=kwargs.get('source_default_outcome'),
            outcomes=kwargs.get('source_outcomes'),
            capabilities=kwargs.get('source_capabilities')
        )
        self.target = target_address if isinstance(target_address,Target) else Target(
            address=kwargs['target_address'],
            durable=kwargs.get('target_durable'),
            expiry_policy=kwargs.get('target_expiry_policy'),
            timeout=kwargs.get('target_timeout'),
            dynamic=kwargs.get('target_dynamic'),
            dynamic_node_properties=kwargs.get('target_dynamic_node_properties'),
            capabilities=kwargs.get('target_capabilities')
        )
        self.link_credit = kwargs.pop('link_credit', None) or DEFAULT_LINK_CREDIT
        self.current_link_credit = self.link_credit
        self.send_settle_mode = kwargs.pop('send_settle_mode', SenderSettleMode.Mixed)
        self.rcv_settle_mode = kwargs.pop('rcv_settle_mode', ReceiverSettleMode.First)
        self.unsettled = kwargs.pop('unsettled', None)
        self.incomplete_unsettled = kwargs.pop('incomplete_unsettled', None)
        self.initial_delivery_count = kwargs.pop('initial_delivery_count', 0)
        self.delivery_count = self.initial_delivery_count
        self.received_delivery_id = None
        self.max_message_size = kwargs.pop('max_message_size', None)
        self.remote_max_message_size = None
        self.available = kwargs.pop('available', None)
        self.properties = kwargs.pop('properties', None)
        self.offered_capabilities = None
        self.desired_capabilities = kwargs.pop('desired_capabilities', None)

        self.network_trace = kwargs['network_trace']
        self.network_trace_params = kwargs['network_trace_params']
        self.network_trace_params['link'] = self.name
        self._session = session
        self._is_closed = False
        self._on_link_state_change = kwargs.get('on_link_state_change')
        self._on_attach = kwargs.get('on_attach')
        self._error = None

    def __enter__(self):
        self.attach()
        return self

    def __exit__(self, *args):
        self.detach(close=True)

    @classmethod
    def from_incoming_frame(cls, session, handle, frame):
        # check link_create_from_endpoint in C lib
        raise NotImplementedError('Pending')  # TODO: Assuming we establish all links for now...

    def get_state(self):
        try:
            raise self._error
        except TypeError:
            pass
        return self.state

    def _check_if_closed(self):
        if self._is_closed:
            try:
                raise self._error
            except TypeError:
                raise AMQPConnectionError(
                    condition=ErrorCondition.InternalError,
                    description="Link already closed."
                )

    def _set_state(self, new_state):
        # type: (LinkState) -> None
        """Update the session state."""
        if new_state is None:
            return
        previous_state = self.state
        self.state = new_state
        _LOGGER.info("Link state changed: %r -> %r", previous_state, new_state, extra=self.network_trace_params)
        try:
            self._on_link_state_change(previous_state, new_state)
        except TypeError:
            pass
        except Exception as e:  # pylint: disable=broad-except
            _LOGGER.error("Link state change callback failed: '%r'", e, extra=self.network_trace_params)
    
    def _on_session_state_change(self):
        if self._session.state == SessionState.MAPPED:
            if not self._is_closed and self.state == LinkState.DETACHED:
                self._outgoing_attach()
                self._set_state(LinkState.ATTACH_SENT)
        elif self._session.state == SessionState.DISCARDING:
            self._set_state(LinkState.DETACHED)

    def _outgoing_attach(self):
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
            properties=self.properties
        )
        if self.network_trace:
            _LOGGER.info("-> %r", attach_frame, extra=self.network_trace_params)
        self._session._outgoing_attach(attach_frame)

    def _incoming_attach(self, frame):
        if self.network_trace:
            _LOGGER.info("<- %r", AttachFrame(*frame), extra=self.network_trace_params)
        if self._is_closed:
            raise ValueError("Invalid link")
        elif not frame[5] or not frame[6]:  # TODO: not sure if we should source + target check here
            _LOGGER.info("Cannot get source or target. Detaching link")
            self._set_state(LinkState.DETACHED)  # TODO: Send detach now?
            raise ValueError("Invalid link")
        self.remote_handle = frame[1]  # handle
        self.remote_max_message_size = frame[10]  # max_message_size
        self.offered_capabilities = frame[11]  # offered_capabilities
        if self.properties:
            self.properties.update(frame[13])  # properties
        else:
            self.properties = frame[13]
        if self.state == LinkState.DETACHED:
            self._set_state(LinkState.ATTACH_RCVD)
        elif self.state == LinkState.ATTACH_SENT:
            self._set_state(LinkState.ATTACHED)
        if self._on_attach:
            try:
                if frame[5]:
                    frame[5] = Source(*frame[5])
                if frame[6]:
                    frame[6] = Target(*frame[6])
                self._on_attach(AttachFrame(*frame))
            except Exception as e:
                _LOGGER.warning("Callback for link attach raised error: {}".format(e))

    def _outgoing_flow(self, **kwargs):
        flow_frame = {
            'handle': self.handle,
            'delivery_count':  self.delivery_count,
            'link_credit': self.current_link_credit,
            'available': kwargs.get('available'),
            'drain': kwargs.get('drain'),
            'echo': kwargs.get('echo'),
            'properties': kwargs.get('properties')
        }
        self._session._outgoing_flow(flow_frame)

    def _incoming_flow(self, frame):
        pass
    
    def _incoming_disposition(self, frame):
        pass

    def _outgoing_detach(self, close=False, error=None):
        detach_frame = DetachFrame(handle=self.handle, closed=close, error=error)
        if self.network_trace:
            _LOGGER.info("-> %r", detach_frame, extra=self.network_trace_params)
        self._session._outgoing_detach(detach_frame)
        if close:
            self._is_closed = True

    def _incoming_detach(self, frame):
        if self.network_trace:
            _LOGGER.info("<- %r", DetachFrame(*frame), extra=self.network_trace_params)
        if self.state == LinkState.ATTACHED:
            self._outgoing_detach(close=frame[1])  # closed
        elif frame[1] and not self._is_closed and self.state in [LinkState.ATTACH_SENT, LinkState.ATTACH_RCVD]:
            # Received a closing detach after we sent a non-closing detach.
            # In this case, we MUST signal that we closed by reattaching and then sending a closing detach.
            self._outgoing_attach()
            self._outgoing_detach(close=True)
        # TODO: on_detach_hook
        if frame[2]:  # error
            # frame[2][0] is condition, frame[2][1] is description, frame[2][2] is info
            error_cls = AMQPLinkRedirect if frame[2][0] == ErrorCondition.LinkRedirect else AMQPLinkError
            self._error = error_cls(condition=frame[2][0], description=frame[2][1], info=frame[2][2])
            self._set_state(LinkState.ERROR)
        else:
            self._set_state(LinkState.DETACHED)

    def attach(self):
        if self._is_closed:
            raise ValueError("Link already closed.")
        self._outgoing_attach()
        self._set_state(LinkState.ATTACH_SENT)

    def detach(self, close=False, error=None):
        if self.state in (LinkState.DETACHED, LinkState.ERROR):
            return
        try:
            self._check_if_closed()
            if self.state in [LinkState.ATTACH_SENT, LinkState.ATTACH_RCVD]:
                self._outgoing_detach(close=close, error=error)
                self._set_state(LinkState.DETACHED)
            elif self.state == LinkState.ATTACHED:
                self._outgoing_detach(close=close, error=error)
                self._set_state(LinkState.DETACH_SENT)
        except Exception as exc:
            _LOGGER.info("An error occurred when detaching the link: %r", exc)
            self._set_state(LinkState.DETACHED)

    def flow(
            self,
            *,
            link_credit: Optional[int] = None,
            **kwargs
        ) -> None:
        self.current_link_credit = link_credit if link_credit is not None else self.link_credit
        self._outgoing_flow(**kwargs)

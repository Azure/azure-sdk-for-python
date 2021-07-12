#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

import logging
from collections import namedtuple

from .sender import SenderLink
from .receiver import ReceiverLink
from .constants import (
    ManagementLinkState,
    LinkState,
    SenderSettleMode,
    ReceiverSettleMode,
    ManagementExecuteOperationResult,
    ManagementOpenResult,
    SEND_DISPOSITION_REJECT
)

_LOGGER = logging.getLogger(__name__)

PendingMgmtOperation = namedtuple('PendingMgmtOperation', ['message', 'on_execute_operation_complete'])


class ManagementLink(object):
    """

    """
    def __init__(self, session, endpoint, **kwargs):
        self.next_message_id = 0
        self.state = ManagementLinkState.IDLE
        self._pending_operations = []
        self._session = session
        self._request_link = session.create_sender_link(  # type: SenderLink
            endpoint,
            on_link_state_change=self._on_sender_state_change,
            send_settle_mode=SenderSettleMode.Unsettled,
            rcv_settle_mode=ReceiverSettleMode.First
        )
        self._response_link = session.create_receiver_link(  # type: ReceiverLink
            endpoint,
            on_link_state_change=self._on_receiver_state_change,
            on_message_received=self._on_message_received,
            send_settle_mode=SenderSettleMode.Unsettled,
            rcv_settle_mode=ReceiverSettleMode.First
        )
        self._on_amqp_management_error = kwargs.get('on_amqp_management_error')
        self._on_amqp_management_open_complete = kwargs.get('on_amqp_management_open_complete')

        self._status_code_field = kwargs.pop('status_code_field', b'statusCode')
        self._status_description_field = kwargs.pop('status_description_field', b'statusDescription')

        self._sender_connected = False
        self._receiver_connected = False

    def __enter__(self):
        self.open()
        return self
    
    def __exit__(self, *args):
        self.close()

    def _on_sender_state_change(self, previous_state, new_state):
        _LOGGER.info("Management link sender state changed: %r -> %r", previous_state, new_state)
        if new_state == previous_state:
            return
        if self.state == ManagementLinkState.OPENING:
            if new_state == LinkState.ATTACHED:
                self._sender_connected = True
                if self._receiver_connected:
                    self.state = ManagementLinkState.OPEN
                    self._on_amqp_management_open_complete(ManagementOpenResult.OK)
            elif new_state in [LinkState.DETACHED, LinkState.DETACH_SENT, LinkState.DETACH_RCVD, LinkState.ERROR]:
                self.state = ManagementLinkState.IDLE
                self._on_amqp_management_open_complete(ManagementOpenResult.ERROR)
        elif self.state == ManagementLinkState.OPEN:
            if new_state is not LinkState.ATTACHED:
                self.state = ManagementLinkState.ERROR
                self._on_amqp_management_error()
        elif self.state == ManagementLinkState.CLOSING:
            if new_state not in [LinkState.DETACHED, LinkState.DETACH_SENT, LinkState.DETACH_RCVD]:
                self.state = ManagementLinkState.ERROR
                self._on_amqp_management_error()
        elif self.state == ManagementLinkState.ERROR:
            # All state transitions shall be ignored.
            return
    
    def _on_receiver_state_change(self, previous_state, new_state):
        _LOGGER.info("Management link receiver state changed: %r -> %r", previous_state, new_state)
        if new_state == previous_state:
            return
        if self.state == ManagementLinkState.OPENING:
            if new_state == LinkState.ATTACHED:
                self._receiver_connected = True
                if self._sender_connected:
                    self.state = ManagementLinkState.OPEN
                    self._on_amqp_management_open_complete(ManagementOpenResult.OK)
            elif new_state in [LinkState.DETACHED, LinkState.DETACH_SENT, LinkState.DETACH_RCVD, LinkState.ERROR]:
                self.state = ManagementLinkState.IDLE
                self._on_amqp_management_open_complete(ManagementOpenResult.ERROR)
        elif self.state == ManagementLinkState.OPEN:
            if new_state is not LinkState.ATTACHED:
                self.state = ManagementLinkState.ERROR
                self._on_amqp_management_error()
        elif self.state == ManagementLinkState.CLOSING:
            if new_state not in [LinkState.DETACHED, LinkState.DETACH_SENT, LinkState.DETACH_RCVD]:
                self.state = ManagementLinkState.ERROR
                self._on_amqp_management_error()
        elif self.state == ManagementLinkState.ERROR:
            # All state transitions shall be ignored.
            return

    def _on_message_received(self, message):
        message_properties = message.get("properties")
        correlation_id = message_properties[5]
        response_detail = message.get("application_properties")

        status_code = response_detail.get(self._status_code_field)
        status_description = response_detail.get(self._status_description_field)

        to_remove_operation = None
        for operation in self._pending_operations:
            if operation.message.properties.message_id == correlation_id:
                to_remove_operation = operation
                break
        if to_remove_operation:
            mgmt_result = ManagementExecuteOperationResult.OK \
                if 200 <= status_code <= 299 else ManagementExecuteOperationResult.FAILED_BAD_STATUS
            to_remove_operation.on_execute_operation_complete(
                mgmt_result,
                status_code,
                status_description,
                message,
                response_detail.get(b'error-condition')
            )
            self._pending_operations.remove(to_remove_operation)

    def _on_send_complete(self, message, reason, state):
        if SEND_DISPOSITION_REJECT in state:  # either rejected or accepted
            to_remove_operation = None
            for operation in self._pending_operations:
                if message == operation.message:
                    to_remove_operation = operation
                    break
            self._pending_operations.remove(to_remove_operation)
            to_remove_operation.on_execute_operation_complete(
                ManagementExecuteOperationResult.ERROR, None, None, message)

    def open(self):
        if self.state != ManagementLinkState.IDLE:
            raise ValueError("Management links are already open or opening.")
        self.state = ManagementLinkState.OPENING
        self._response_link.attach()
        self._request_link.attach()

    def execute_operation(
            self,
            message,
            on_execute_operation_complete,
            timeout=None,
            operation=None,
            type=None,
            locales=None
    ):

        self._request_link.send_transfer(
            message,
            on_send_complete=self._on_send_complete,
            timeout=timeout
        )
        self._pending_operations.append(PendingMgmtOperation(message, on_execute_operation_complete))

    def close(self):
        if self.state != ManagementLinkState.IDLE:
            self.state = ManagementLinkState.CLOSING
            self._response_link.detach(close=True)
            self._request_link.detach(close=True)
            self._pending_operations = []
        self.state = ManagementLinkState.IDLE

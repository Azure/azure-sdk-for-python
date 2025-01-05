# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------

import logging

from .message import ServiceBusReceivedMessage
from .constants import ServiceBusReceiveMode, MGMT_RESPONSE_MESSAGE_ERROR_CONDITION

_LOGGER = logging.getLogger(__name__)


def default(status_code, message, description, amqp_transport):  # pylint: disable=inconsistent-return-statements
    condition = message.application_properties.get(MGMT_RESPONSE_MESSAGE_ERROR_CONDITION)
    if status_code == 200:
        return message.value

    amqp_transport.handle_amqp_mgmt_error(
        _LOGGER, "Service request failed.", condition, description, status_code
    )


def session_lock_renew_op(  # pylint: disable=inconsistent-return-statements
    status_code, message, description, amqp_transport
):
    condition = message.application_properties.get(MGMT_RESPONSE_MESSAGE_ERROR_CONDITION)
    if status_code == 200:
        return message.value

    amqp_transport.handle_amqp_mgmt_error(
        _LOGGER, "Session lock renew failed.", condition, description, status_code
    )


def message_lock_renew_op(  # pylint: disable=inconsistent-return-statements
    status_code, message, description, amqp_transport
):
    condition = message.application_properties.get(MGMT_RESPONSE_MESSAGE_ERROR_CONDITION)
    if status_code == 200:
        # TODO: will this always be body type ValueType?
        return message.value

    amqp_transport.handle_amqp_mgmt_error(
        _LOGGER, "Message lock renew failed.", condition, description, status_code
    )


def peek_op(  # pylint: disable=inconsistent-return-statements
    status_code, message, description, receiver, amqp_transport
):
    condition = message.application_properties.get(MGMT_RESPONSE_MESSAGE_ERROR_CONDITION)
    if status_code == 200:
        return amqp_transport.parse_received_message(
            message, message_type=ServiceBusReceivedMessage, receiver=receiver, is_peeked_message=True
        )
    if status_code in [202, 204]:
        return []

    amqp_transport.handle_amqp_mgmt_error(
        _LOGGER, "Message peek failed.", condition, description, status_code
    )


def list_sessions_op(  # pylint: disable=inconsistent-return-statements
    status_code, message, description, amqp_transport
):
    condition = message.application_properties.get(MGMT_RESPONSE_MESSAGE_ERROR_CONDITION)
    if status_code == 200:
        parsed = []
        for m in amqp_transport.get_message_value(message)[b"sessions-ids"]:
            parsed.append(m.decode("UTF-8"))
        return parsed
    if status_code in [202, 204]:
        return []

    amqp_transport.handle_amqp_mgmt_error(_LOGGER, "List sessions failed.", condition, description, status_code)


def deferred_message_op(  # pylint: disable=inconsistent-return-statements
    status_code,
    message,
    description,
    receiver,
    amqp_transport,
    receive_mode=ServiceBusReceiveMode.PEEK_LOCK,
    message_type=ServiceBusReceivedMessage,
):
    condition = message.application_properties.get(MGMT_RESPONSE_MESSAGE_ERROR_CONDITION)
    if status_code == 200:
        return amqp_transport.parse_received_message(
            message, message_type=message_type, receiver=receiver, receive_mode=receive_mode, is_deferred_message=True
        )
    if status_code in [202, 204]:
        return []

    amqp_transport.handle_amqp_mgmt_error(
        _LOGGER,
        "Retrieving deferred messages failed.",
        condition,
        description,
        status_code,
    )


def schedule_op(status_code, message, description, amqp_transport):  # pylint: disable=inconsistent-return-statements
    condition = message.application_properties.get(MGMT_RESPONSE_MESSAGE_ERROR_CONDITION)
    if status_code == 200:
        return message.value[b"sequence-numbers"]

    amqp_transport.handle_amqp_mgmt_error(_LOGGER, "Scheduling messages failed.", condition, description, status_code)

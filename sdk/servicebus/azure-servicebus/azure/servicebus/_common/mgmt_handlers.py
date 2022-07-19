# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------

import logging

from .._pyamqp._decode import decode_payload

from .message import ServiceBusReceivedMessage
from ..exceptions import _handle_amqp_mgmt_error
from .constants import ServiceBusReceiveMode, MGMT_RESPONSE_MESSAGE_ERROR_CONDITION

_LOGGER = logging.getLogger(__name__)


def default(  # pylint: disable=inconsistent-return-statements
    status_code, message, description
):
    condition = message.application_properties.get(
        MGMT_RESPONSE_MESSAGE_ERROR_CONDITION
    )
    if status_code == 200:
        return message.get_data()

    _handle_amqp_mgmt_error(
        _LOGGER, "Service request failed.", condition, description, status_code
    )


def session_lock_renew_op(  # pylint: disable=inconsistent-return-statements
    status_code, message, description
):
    condition = message.application_properties.get(
        MGMT_RESPONSE_MESSAGE_ERROR_CONDITION
    )
    if status_code == 200:
        return message.get_data()

    _handle_amqp_mgmt_error(
        _LOGGER, "Session lock renew failed.", condition, description, status_code
    )


def message_lock_renew_op(  # pylint: disable=inconsistent-return-statements
    status_code, message, description
):
    condition = message.application_properties.get(
        MGMT_RESPONSE_MESSAGE_ERROR_CONDITION
    )
    if status_code == 200:
        return message.get_data()

    _handle_amqp_mgmt_error(
        _LOGGER, "Message lock renew failed.", condition, description, status_code
    )


def peek_op(  # pylint: disable=inconsistent-return-statements
    status_code, message, description, receiver
):
    condition = message.application_properties.get(
        MGMT_RESPONSE_MESSAGE_ERROR_CONDITION
    )
    if status_code == 200:
        parsed = []
        for m in message.value[b"messages"]:
            wrapped = decode_payload(memoryview(m[b"message"]))
            parsed.append(
                ServiceBusReceivedMessage(
                    wrapped, is_peeked_message=True, receiver=receiver
                )
            )
        return parsed
    if status_code in [202, 204]:
        return []

    _handle_amqp_mgmt_error(
        _LOGGER, "Message peek failed.", condition, description, status_code
    )


def list_sessions_op(  # pylint: disable=inconsistent-return-statements
    status_code, message, description
):
    condition = message.application_properties.get(
        MGMT_RESPONSE_MESSAGE_ERROR_CONDITION
    )
    if status_code == 200:
        parsed = []
        for m in message.get_data()[b"sessions-ids"]:
            parsed.append(m.decode("UTF-8"))
        return parsed
    if status_code in [202, 204]:
        return []

    _handle_amqp_mgmt_error(
        _LOGGER, "List sessions failed.", condition, description, status_code
    )


def deferred_message_op(  # pylint: disable=inconsistent-return-statements
    status_code,
    message,
    description,
    receiver,
    receive_mode=ServiceBusReceiveMode.PEEK_LOCK,
    message_type=ServiceBusReceivedMessage,
):
    condition = message.application_properties.get(
        MGMT_RESPONSE_MESSAGE_ERROR_CONDITION
    )
    if status_code == 200:
        parsed = []
        for m in message.value[b"messages"]:
            wrapped = decode_payload(memoryview(m[b"message"]))
            parsed.append(
                message_type(
                    wrapped, receive_mode, is_deferred_message=True, receiver=receiver
                )
            )
        return parsed
    if status_code in [202, 204]:
        return []

    _handle_amqp_mgmt_error(
        _LOGGER,
        "Retrieving deferred messages failed.",
        condition,
        description,
        status_code,
    )


def schedule_op(  # pylint: disable=inconsistent-return-statements
    status_code, message, description
):
    condition = message.application_properties.get(
        MGMT_RESPONSE_MESSAGE_ERROR_CONDITION
    )
    if status_code == 200:
        return message.get_data()[b"sequence-numbers"]

    _handle_amqp_mgmt_error(
        _LOGGER, "Scheduling messages failed.", condition, description, status_code
    )

# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------

import uamqp
from .message import ServiceBusReceivedMessage
from ..exceptions import ServiceBusError, MessageLockExpired, SessionLockExpired
from .constants import (
    ReceiveMode,
    MGMT_RESPONSE_MESSAGE_ERROR_CONDITION,
    ERROR_CODE_SESSION_LOCK_LOST,
    ERROR_CODE_MESSAGE_LOCK_LOST
)


def default(status_code, message, description):
    condition = message.application_properties.get(MGMT_RESPONSE_MESSAGE_ERROR_CONDITION)
    if status_code == 200:
        return message.get_data()
    raise ServiceBusError(
        "Service request returned status code: {}. Condition: {}, Description: {}".format(
            status_code, condition, description))


def session_lock_renew_op(status_code, message, description):
    condition = message.application_properties.get(MGMT_RESPONSE_MESSAGE_ERROR_CONDITION)
    if status_code == 200:
        return message.get_data()
    if condition == ERROR_CODE_SESSION_LOCK_LOST or status_code == 410:
        raise SessionLockExpired(message=description)
    raise ServiceBusError(
        "Session lock renew request returned status code: {}. Description: {}, Data: {}".format(
            status_code, description, message.get_data()))


def message_lock_renew_op(status_code, message, description):
    condition = message.application_properties.get(MGMT_RESPONSE_MESSAGE_ERROR_CONDITION)
    if status_code == 200:
        return message.get_data()
    if condition == ERROR_CODE_MESSAGE_LOCK_LOST or status_code == 410:
        raise MessageLockExpired(message=description)
    raise ServiceBusError(
        "Message Lock renew request returned status code: {}. Description: {}, Data: {}".format(
            status_code, description, message.get_data()))


def peek_op(status_code, message, description, receiver):
    if status_code == 200:
        parsed = []
        for m in message.get_data()[b'messages']:
            wrapped = uamqp.Message.decode_from_bytes(bytearray(m[b'message']))
            parsed.append(ServiceBusReceivedMessage(wrapped, is_peeked_message=True, receiver=receiver))
        return parsed
    if status_code in [202, 204]:
        return []
    error_msg = "Message peek failed with status code: {}.\n".format(status_code)
    if description:
        error_msg += "{}.".format(description)
    raise ServiceBusError(error_msg)


def list_sessions_op(status_code, message, description):
    if status_code == 200:
        parsed = []
        for m in message.get_data()[b'sessions-ids']:
            parsed.append(m.decode('UTF-8'))
        return parsed
    if status_code in [202, 204]:
        return []
    error_msg = "List sessions failed with status code: {}.\n".format(status_code)
    if description:
        error_msg += "{}.".format(description)
    raise ServiceBusError(error_msg)


def deferred_message_op(
        status_code,
        message,
        description,
        receiver,
        receive_mode=ReceiveMode.PeekLock,
        message_type=ServiceBusReceivedMessage
):
    if status_code == 200:
        parsed = []
        for m in message.get_data()[b'messages']:
            wrapped = uamqp.Message.decode_from_bytes(bytearray(m[b'message']))
            parsed.append(message_type(wrapped, receive_mode, is_deferred_message=True, receiver=receiver))
        return parsed
    if status_code in [202, 204]:
        return []
    error_msg = "Retrieving deferred messages failed with status code: {}.\n".format(status_code)
    if description:
        error_msg += "{}.".format(description)
    raise ServiceBusError(error_msg)


def schedule_op(status_code, message, description):
    if status_code == 200:
        return message.get_data()[b'sequence-numbers']
    error_msg = "Scheduling messages failed with status code: {}.\n".format(status_code)
    if description:
        error_msg += "{}.".format(description)
    raise ServiceBusError(error_msg)

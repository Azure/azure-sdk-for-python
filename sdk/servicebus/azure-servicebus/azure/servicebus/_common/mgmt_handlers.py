# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------

import uamqp

from .message import PeekMessage, ReceivedMessage
from ..exceptions import ServiceBusError, MessageLockExpired
from .constants import ReceiveSettleMode


def default(status_code, message, description):
    if status_code == 200:
        return message.get_data()
    raise ServiceBusError(
        "Management request returned status code: {}. Description: {}, Data: {}".format(
            status_code, description, message.get_data()))


def lock_renew_op(status_code, message, description):
    if status_code == 200:
        return message.get_data()
    if status_code == 410:
        raise MessageLockExpired(message=description)
    raise ServiceBusError(
        "Management request returned status code: {}. Description: {}, Data: {}".format(
            status_code, description, message.get_data()))


def peek_op(status_code, message, description):
    if status_code == 200:
        parsed = []
        for m in message.get_data()[b'messages']:
            wrapped = uamqp.Message.decode_from_bytes(bytearray(m[b'message']))
            parsed.append(PeekMessage(wrapped))
        return parsed
    if status_code in [202, 204]:
        return []
    error = "Message peek failed with status code: {}.\n".format(status_code)
    if description:
        error += "{}.".format(description)
    raise ServiceBusError(error)


def list_sessions_op(status_code, message, description):
    if status_code == 200:
        parsed = []
        for m in message.get_data()[b'sessions-ids']:
            parsed.append(m.decode('UTF-8'))
        return parsed
    if status_code in [202, 204]:
        return []
    error = "List sessions failed with status code: {}.\n".format(status_code)
    if description:
        error += "{}.".format(description)
    raise ServiceBusError(error)


def deferred_message_op(
        status_code,
        message,
        description,
        mode=ReceiveSettleMode.PeekLock,
        message_type=ReceivedMessage
):
    if status_code == 200:
        parsed = []
        for m in message.get_data()[b'messages']:
            wrapped = uamqp.Message.decode_from_bytes(bytearray(m[b'message']))
            parsed.append(message_type(wrapped, mode))
        return parsed
    if status_code in [202, 204]:
        return []
    error = "Retrieving deferred messages failed with status code: {}.\n".format(status_code)
    if description:
        error += "{}.".format(description)
    raise ServiceBusError(error)


def schedule_op(status_code, message, description):
    if status_code == 200:
        return message.get_data()[b'sequence-numbers']
    error = "Scheduling messages failed with status code: {}.\n".format(status_code)
    if description:
        error += "{}.".format(description)
    raise ServiceBusError(error)

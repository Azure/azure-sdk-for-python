# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------

import logging
import uamqp
from .message import ServiceBusReceivedMessage
from ..exceptions import _handle_amqp_mgmt_error
from .constants import ServiceBusReceiveMode, MGMT_RESPONSE_MESSAGE_ERROR_CONDITION
from azure.servicebus.management import (
    CorrelationRuleFilter,
    SqlRuleFilter,
    SqlRuleAction,
    RuleProperties,
)
from datetime import datetime


_LOGGER = logging.getLogger(__name__)


def default(status_code, message, description):  # pylint: disable=inconsistent-return-statements
    condition = message.application_properties.get(MGMT_RESPONSE_MESSAGE_ERROR_CONDITION)
    if status_code == 200:
        return message.get_data()

    _handle_amqp_mgmt_error(_LOGGER, "Service request failed.", condition, description, status_code)


def session_lock_renew_op(status_code, message, description):  # pylint: disable=inconsistent-return-statements
    condition = message.application_properties.get(MGMT_RESPONSE_MESSAGE_ERROR_CONDITION)
    if status_code == 200:
        return message.get_data()

    _handle_amqp_mgmt_error(_LOGGER, "Session lock renew failed.", condition, description, status_code)


def message_lock_renew_op(status_code, message, description):  # pylint: disable=inconsistent-return-statements
    condition = message.application_properties.get(MGMT_RESPONSE_MESSAGE_ERROR_CONDITION)
    if status_code == 200:
        return message.get_data()

    _handle_amqp_mgmt_error(_LOGGER, "Message lock renew failed.", condition, description, status_code)


def peek_op(status_code, message, description, receiver):  # pylint: disable=inconsistent-return-statements
    condition = message.application_properties.get(MGMT_RESPONSE_MESSAGE_ERROR_CONDITION)
    if status_code == 200:
        parsed = []
        for m in message.get_data()[b"messages"]:
            wrapped = uamqp.Message.decode_from_bytes(bytearray(m[b"message"]))
            parsed.append(ServiceBusReceivedMessage(wrapped, is_peeked_message=True, receiver=receiver))
        return parsed
    if status_code in [202, 204]:
        return []

    _handle_amqp_mgmt_error(_LOGGER, "Message peek failed.", condition, description, status_code)


def list_sessions_op(status_code, message, description):  # pylint: disable=inconsistent-return-statements
    condition = message.application_properties.get(MGMT_RESPONSE_MESSAGE_ERROR_CONDITION)
    if status_code == 200:
        parsed = []
        for m in message.get_data()[b"sessions-ids"]:
            parsed.append(m.decode("UTF-8"))
        return parsed
    if status_code in [202, 204]:
        return []

    _handle_amqp_mgmt_error(_LOGGER, "List sessions failed.", condition, description, status_code)


def deferred_message_op(  # pylint: disable=inconsistent-return-statements
    status_code,
    message,
    description,
    receiver,
    receive_mode=ServiceBusReceiveMode.PEEK_LOCK,
    message_type=ServiceBusReceivedMessage,
):
    condition = message.application_properties.get(MGMT_RESPONSE_MESSAGE_ERROR_CONDITION)
    if status_code == 200:
        parsed = []
        for m in message.get_data()[b"messages"]:
            wrapped = uamqp.Message.decode_from_bytes(bytearray(m[b"message"]))
            parsed.append(message_type(wrapped, receive_mode, is_deferred_message=True, receiver=receiver))
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


def schedule_op(status_code, message, description):  # pylint: disable=inconsistent-return-statements
    condition = message.application_properties.get(MGMT_RESPONSE_MESSAGE_ERROR_CONDITION)
    if status_code == 200:
        return message.get_data()[b"sequence-numbers"]

    _handle_amqp_mgmt_error(_LOGGER, "Scheduling messages failed.", condition, description, status_code)


def list_rules_op(status_code, rules, description):
    condition = rules.application_properties.get(MGMT_RESPONSE_MESSAGE_ERROR_CONDITION)

    rule_descriptions = []

    if status_code == 200:
        for entry in rules.value[b"rules"]:
            amqp_rule = entry[b"rule-description"]
            rule_description = build_rule_description(amqp_rule)
            rule_descriptions.append(rule_description)

        return rule_descriptions

    if status_code in [202, 204]:
        return rules

    _handle_amqp_mgmt_error(
        _LOGGER,
        "Retrieving rules failed.",
        condition,
        description,
        status_code,
    )


def delete_rule_op(status_code, message, description):
    if status_code != 200:
        _handle_amqp_mgmt_error(
            _LOGGER,
            "Deleting rule failed.",
            description,
            status_code,
        )


def create_rule_op(status_code, message, description):
    if status_code != 200:
        _handle_amqp_mgmt_error(
            _LOGGER,
            "Creating rule failed.",
            description,
            status_code,
        )


def build_rule_description(description):
    rule_filter = build_filter(description[0])
    rule_action = build_rule_action(description[1])

    rule_description = RuleProperties(
        name=description[2],
        filter=rule_filter,
        action=rule_action,
        created_at_utc=datetime.fromtimestamp(int(description[3] / 1000)),
    )

    return rule_description


def build_filter(filter):
    filter_obj = None
    if len(filter) == 2 and filter[1] == 20:  # this is a sql filter
        filter_obj = SqlRuleFilter(sql_expression=filter[0])
        return filter_obj
    if len(filter) == 9:  # correlation filter
        correlation_id = filter[0]
        message_id = filter[1]
        to = filter[2]
        reply_to = filter[3]
        label = filter[4]
        session_id = filter[5]
        reply_to_session_id = filter[6]
        content_type = filter[7]
        properties = filter[8]

        filter_obj = CorrelationRuleFilter(
            correlation_id=correlation_id,
            message_id=message_id,
            to=to,
            reply_to=reply_to,
            session_id=session_id,
            reply_to_session_id=reply_to_session_id,
            label=label,
            content_type=content_type,
            properties=properties,
        )
        return filter_obj
    pass


def build_rule_action(action):
    action_obj = None

    if action:
        action_obj = SqlRuleAction(sql_expression=action[0])

    return action_obj

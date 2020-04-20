# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import time
import logging
from typing import TYPE_CHECKING

from uamqp import AMQPClient, types, c_uamqp

from ._base_handler import BaseHandler
from ._common.mgmt_handlers import (
    add_rule_op,
    delete_rule_op,
    list_rules_op
)
from ._common.utils import create_authentication
from ._common.constants import (
    MGMT_REQUEST_RULE_NAME,
    MGMT_REQUEST_RULE_DESCRIPTION,
    MGMT_REQUEST_RULE_SQL_FILTER,
    MGMT_REQUEST_RULE_CORRELATION_FILTER,
    MGMT_REQUEST_RULE_SQL_RULE_ACTION,
    MGMT_REQUEST_RULE_EXPRESSION,
    MGMT_REQUEST_CORRELATION_FILTER_CORRELATION_ID,
    MGMT_REQUEST_CORRELATION_FILTER_MESSAGE_ID,
    MGMT_REQUEST_CORRELATION_FILTER_TO,
    MGMT_REQUEST_CORRELATION_FILTER_REPLY_TO,
    MGMT_REQUEST_CORRELATION_FILTER_LABEL,
    MGMT_REQUEST_CORRELATION_FILTER_SESSION_ID,
    MGMT_REQUEST_CORRELATION_FILTER_REPLY_TO_SESSION_ID,
    MGMT_REQUEST_CORRELATION_FILTER_CONTENT_TYPE,
    MGMT_REQUEST_CORRELATION_FILTER_USER_PROPERTIES,
    MGMT_REQUEST_GET_RULES_TOP,
    MGMT_REQUEST_GET_RULES_SKIP,
    MGMT_REQUEST_RULE_TRUE_FILTER,
    MGMT_REQUEST_RULE_FALSE_FILTER,
    REQUEST_RESPONSE_ADD_RULE_OPERATION,
    REQUEST_RESPONSE_REMOVE_RULE_OPERATION,
    REQUEST_RESPONSE_GET_RULES_OPERATION,
    MAX_32BIT_INTEGER,
    RULE_FILTER_TYPE_CORRELATION_FILTER,
    RULE_FILTER_TYPE_FALSE_FILTER,
    RULE_FILTER_TYPE_TRUE_FILTER,
    RULE_FILTER_TYPE_SQL_FILTER
)

if TYPE_CHECKING:
    from azure.core.credentials import TokenCredential

_LOGGER = logging.getLogger(__name__)


class CorrelationFilter:
    # TODO: This is the simplistic implementation
    def __init__(self, **kwargs):
        self._correlation_id = kwargs.get("correlation_id")
        self._message_id = kwargs.get("message_id")
        self._to = kwargs.get("to")
        self._reply_to = kwargs.get("reply_to")
        self._label = kwargs.get("label")
        self._session_id = kwargs.get("session_id")
        self._reply_to_session_id = kwargs.get("reply_to_session_id")
        self._content_type = kwargs.get("content_type")
        self._user_properties = kwargs.get("user_properties")

    def __str__(self):
        pass

    @property
    def correlation_id(self):
        return self._correlation_id

    @correlation_id.setter
    def correlation_id(self, val):
        self._correlation_id = val

    @property
    def message_id(self):
        return self._message_id

    @message_id.setter
    def message_id(self, val):
        self._message_id = val

    @property
    def to(self):
        return self._to

    @to.setter
    def to(self, val):
        self._to = val

    @property
    def reply_to(self):
        return self._reply_to

    @reply_to.setter
    def reply_to(self, val):
        self._reply_to = val

    @property
    def label(self):
        return self._label

    @label.setter
    def label(self, val):
        self._label = val

    @property
    def session_id(self):
        return self._session_id

    @session_id.setter
    def session_id(self, val):
        self._session_id = val

    @property
    def reply_to_session_id(self):
        return self._reply_to_session_id

    @reply_to_session_id.setter
    def reply_to_session_id(self, val):
        self._reply_to_session_id = val

    @property
    def content_type(self):
        return self._content_type

    @content_type.setter
    def content_type(self, val):
        self._content_type = val

    @property
    def user_properties(self):
        return self._user_properties

    @user_properties.setter
    def user_properties(self, val):
        self._user_properties = val


class RuleDescription:
    def __init__(self, rule_name, rule_filter, sql_rule_action_expression):
        self.rule_name = rule_name
        self.rule_filter = rule_filter
        self.sql_rule_action_expression = sql_rule_action_expression


class SubscriptionRuleManager(BaseHandler):
    def __init__(
        self,
        fully_qualified_namespace,
        topic_name,
        subscription_name,
        credential,
        **kwargs
    ):
        # type: (str, str, str, TokenCredential, Any) -> None
        super(SubscriptionRuleManager, self).__init__(
            fully_qualified_namespace=fully_qualified_namespace,
            credential=credential,
            entity_name=topic_name,
            subscription_name=subscription_name,
            **kwargs
        )
        self._entity_uri = "amqps://{}/{}/Subscriptions/{}".format(
            self.fully_qualified_namespace,
            topic_name,
            subscription_name
        )
        self._auth_uri = "sb://{}/{}/Subscriptions/{}".format(
            self.fully_qualified_namespace,
            topic_name,
            subscription_name
        )
        self._connection = kwargs.get("connection")

    def _create_handler(self, auth):
        self._handler = AMQPClient(
            self._entity_uri,
            auth=auth,
            debug=self._config.logging_enable,
            properties=self._properties,
            encoding=self._config.encoding,
        )

    def _open(self):
        if self._running:
            return
        if self._handler:
            self._handler.close()

        auth = None if self._connection else create_authentication(self)
        self._create_handler(auth)
        self._handler.open(connection=self._connection)
        while not self._handler.client_ready():
            time.sleep(0.05)
        self._running = True

    @classmethod
    def _parse_list_rules_response(cls, message):
        raw_data = message._message.get_body_value()  # pylint: disable=protected-access
        rule_key_string = c_uamqp.StringValue()
        rule_key_string.create(b"rules")
        rules = raw_data[rule_key_string]
        rule_key_string.destroy()

        rule_description_key_string = c_uamqp.StringValue()
        rule_description_key_string.create(b"rule-description")

        out_res = []
        for rule in rules:
            rule_description = rule[rule_description_key_string]
            inner_rule_data = rule_description.data

            # Handle rule filter
            rule_filter = inner_rule_data[0]
            rule_filter_type = rule_filter.description.value
            rule_filter_data = rule_filter.data  # type of described array
            if rule_filter_type == RULE_FILTER_TYPE_SQL_FILTER:
                out_filter = rule_filter_data[0].value
            elif rule_filter_type == RULE_FILTER_TYPE_CORRELATION_FILTER:
                out_filter = CorrelationFilter(
                    correlation_id=rule_filter_data[0].value,
                    message_id=rule_filter_data[1].value,
                    to=rule_filter_data[2].value,
                    reply_to=rule_filter_data[3].value,
                    label=rule_filter_data[4].value,
                    session_id=rule_filter_data[5].value,
                    reply_to_session_id=rule_filter_data[6].value,
                    content_type=rule_filter_data[7].value,
                    user_properties=rule_filter_data[8].value
                )
                pass
            elif rule_filter_type == RULE_FILTER_TYPE_TRUE_FILTER:
                out_filter = bytes(MGMT_REQUEST_RULE_TRUE_FILTER)
            elif rule_filter_type == RULE_FILTER_TYPE_FALSE_FILTER:
                out_filter = bytes(MGMT_REQUEST_RULE_FALSE_FILTER)

            # Handle rule action
            rule_action_raw_data = inner_rule_data[1].data
            rule_action = rule_action_raw_data[0].value if len(rule_action_raw_data) > 0 else None
            rule_name = inner_rule_data[2].value

            out_rule_description = RuleDescription(
                rule_name,
                out_filter,
                rule_action
            )
            out_res.append(out_rule_description)

        rule_description_key_string.destroy()
        return out_res

    @classmethod
    def _construct_add_rule_message(cls, rule_name, rule_filter, sql_rule_action_expression=None):
        rule_description = {}
        if type(rule_filter) is bool:
            rule_description[MGMT_REQUEST_RULE_SQL_FILTER] = {
                MGMT_REQUEST_RULE_EXPRESSION:
                    (MGMT_REQUEST_RULE_TRUE_FILTER if rule_filter else MGMT_REQUEST_RULE_FALSE_FILTER)
            }
        elif type(rule_filter) is str:
            rule_description[MGMT_REQUEST_RULE_SQL_FILTER] = {
                MGMT_REQUEST_RULE_EXPRESSION: rule_filter
            }
        elif type(rule_filter) is CorrelationFilter:
            rule_description[MGMT_REQUEST_RULE_CORRELATION_FILTER] = {
                MGMT_REQUEST_CORRELATION_FILTER_CORRELATION_ID: rule_filter.correlation_id,
                MGMT_REQUEST_CORRELATION_FILTER_MESSAGE_ID: rule_filter.message_id,
                MGMT_REQUEST_CORRELATION_FILTER_TO: rule_filter.to,
                MGMT_REQUEST_CORRELATION_FILTER_REPLY_TO: rule_filter.reply_to,
                MGMT_REQUEST_CORRELATION_FILTER_LABEL: rule_filter.label,
                MGMT_REQUEST_CORRELATION_FILTER_SESSION_ID: rule_filter.session_id,
                MGMT_REQUEST_CORRELATION_FILTER_REPLY_TO_SESSION_ID: rule_filter.reply_to_session_id,
                MGMT_REQUEST_CORRELATION_FILTER_CONTENT_TYPE: rule_filter.content_type,
                MGMT_REQUEST_CORRELATION_FILTER_USER_PROPERTIES: rule_filter.user_properties
            }
        else:
            raise ValueError("Invalid filter type.")

        if sql_rule_action_expression:
            rule_description[MGMT_REQUEST_RULE_SQL_RULE_ACTION] = {
                MGMT_REQUEST_RULE_EXPRESSION: sql_rule_action_expression
            }

        message = {
            MGMT_REQUEST_RULE_NAME: rule_name,
            MGMT_REQUEST_RULE_DESCRIPTION: rule_description
        }

    def add_rule(self, rule_name, rule_filter, sql_rule_action_expression=None, **kwargs):
        timeout = kwargs.get("timeout")
        message = self._construct_add_rule_message(rule_name, rule_filter, sql_rule_action_expression)
        self._mgmt_request_response_with_retry(
            REQUEST_RESPONSE_ADD_RULE_OPERATION,
            message,
            add_rule_op
        )

    def list_rules(self, **kwargs):
        message = {
            MGMT_REQUEST_GET_RULES_TOP: types.AMQPInt(MAX_32BIT_INTEGER),
            MGMT_REQUEST_GET_RULES_SKIP: 0
        }

        raw_message = self._mgmt_request_response_with_retry(
            REQUEST_RESPONSE_GET_RULES_OPERATION,
            message,
            list_rules_op
        )

        return self._parse_list_rules_response(raw_message)

    def delete_rule(self, rule_name, **kwargs):
        message = {
            MGMT_REQUEST_RULE_NAME: rule_name
        }

        self._mgmt_request_response_with_retry(
            REQUEST_RESPONSE_REMOVE_RULE_OPERATION,
            message,
            delete_rule_op
        )

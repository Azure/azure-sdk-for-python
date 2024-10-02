# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import asyncio
from abc import abstractmethod
from retry import retry
import warnings
from _shared.utils import get_http_logging_policy
from azure.communication.messages.aio import (
    NotificationMessagesClient,
    MessageTemplateClient,
)
from devtools_testutils import AzureRecordedTestCase


class AsyncMessagesRecordedTestCase(AzureRecordedTestCase):

    def create_notification_message_client(self) -> NotificationMessagesClient:
        return NotificationMessagesClient.from_connection_string(
            conn_str=self.connection_string, http_logging_policy=get_http_logging_policy()
        )

    def create_notification_message_client_from_token(self) -> NotificationMessagesClient:
        return NotificationMessagesClient.from_token_credentials(
            endpoint=self.endpoint_str, http_logging_policy=get_http_logging_policy()
        )

    def create_message_template_client(self) -> MessageTemplateClient:
        return MessageTemplateClient.from_connection_string(
            conn_str=self.connection_string, http_logging_policy=get_http_logging_policy()
        )

    def create_message_template_client_from_token(self) -> MessageTemplateClient:
        return MessageTemplateClient.from_token_credentials(
            endpoint=self.endpoint_str, http_logging_policy=get_http_logging_policy()
        )

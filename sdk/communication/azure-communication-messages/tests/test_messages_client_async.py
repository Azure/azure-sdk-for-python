# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import os
import asyncio
from devtools_testutils.aio import recorded_by_proxy_async
from _decorators_async import MessagesPreparersAsync
from azure.core.credentials import AccessToken
from azure.communication.messages.aio import NotificationMessagesClient
from azure.communication.messages.models import (
    TextNotificationContent,
    MediaNotificationContent,
    TemplateNotificationContent,
    MessageReceipt
    )
from _shared.utils import get_http_logging_policy
from _messages_test_case_async import AsyncMessagesRecordedTestCase
from azure.communication.messages._shared.utils import parse_connection_str
    
class TestNotificationMessageClientForTextAsync(AsyncMessagesRecordedTestCase):

    @MessagesPreparersAsync.messages_test_decorator_async
    @recorded_by_proxy_async
    async def test_text_send_message_async(self):
        phone_number: str = "+14254360097"
        raised = False

        message_client = self.create_notification_message_client()

        text_options = TextNotificationContent(
            channel_registration_id="b045be8c-45cd-492a-b2a2-47bae7c36959",
            to= [phone_number],
            content="Thanks for your feedback.")

        message_response : MessageReceipt = None
        try:
            message_responses = await message_client.send(text_options)
            message_response = message_responses.receipts[0]
        except:
            raised = True
            raise
        assert raised is False
        assert message_response.message_id is not None
        assert message_response.to == phone_number




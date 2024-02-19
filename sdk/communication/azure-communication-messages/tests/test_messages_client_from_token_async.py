# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import os
import asyncio
from typing import List
from devtools_testutils.aio import recorded_by_proxy_async
from _decorators_async import MessagesPreparersAsync
from azure.core.credentials import AccessToken
from azure.communication.messages.aio import NotificationMessagesClient
from azure.communication.messages.models import (
    TextNotificationContent,
    MediaNotificationContent,
    TemplateNotificationContent,
    MessageReceipt,
    )
from _messages_test_case_async import AsyncMessagesRecordedTestCase
    
class TestNotificationMessageClientFromTokenAsync(AsyncMessagesRecordedTestCase):

    @MessagesPreparersAsync.messages_test_decorator_for_token_async  
    @recorded_by_proxy_async 
    async def test_text_send_message_with_token_credentials_async(self):
        phone_number: str = "+14254360097"
        raised = False

        text_options = TextNotificationContent(
            channel_registration_id="b045be8c-45cd-492a-b2a2-47bae7c36959",
            to= [phone_number],
            content="Thanks for your feedback.Notification based on Token.")

        message_response : MessageReceipt = None
        message_client: NotificationMessagesClient = self.create_notification_message_client_from_token()

        try:
            async with message_client:
                message_responses = await message_client.send(text_options)
                message_response = message_responses.receipts[0]
        except:
            raised = True
            raise
        assert raised is False
        assert message_response.message_id is not None
        assert message_response.to == phone_number


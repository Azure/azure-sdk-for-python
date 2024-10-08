# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from devtools_testutils.aio import recorded_by_proxy_async
from _decorators_async import MessagesPreparersAsync
from azure.communication.messages.models import MessageTemplateItem, MessageTemplate
from _shared.utils import get_http_logging_policy
from _messages_test_case_async import AsyncMessagesRecordedTestCase
from azure.communication.messages._shared.utils import parse_connection_str


class TestMessageTemplateClientToGetTemplatesAsync(AsyncMessagesRecordedTestCase):

    @MessagesPreparersAsync.messages_test_decorator_async
    @recorded_by_proxy_async
    async def test_get_templates_async(self):
        channel_id = "b045be8c-45cd-492a-b2a2-47bae7c36959"
        raised = False

        message_template_client = self.create_message_template_client()

        try:
            async with message_template_client:
                message_template_item_list = message_template_client.list_templates(channel_id)
        except:
            raised = True
            raise

        assert raised is False
        assert message_template_item_list is not None

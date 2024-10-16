# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from devtools_testutils import recorded_by_proxy
from _decorators import MessagesPreparers
from azure.communication.messages.models import MessageTemplateItem, MessageTemplate
from _shared.utils import get_http_logging_policy
from _messages_test_case import MessagesRecordedTestCase
from azure.communication.messages._shared.utils import parse_connection_str


class TestMessageTemplateClientToGetTemplates(MessagesRecordedTestCase):

    @MessagesPreparers.messages_test_decorator
    @recorded_by_proxy
    def test_get_templates(self):
        channel_id = "b045be8c-45cd-492a-b2a2-47bae7c36959"
        raised = False

        message_template_client = self.create_message_template_client()

        try:
            with message_template_client:
                message_template_item_list = message_template_client.list_templates(channel_id)
        except:
            raised = True
            raise

        assert raised is False
        assert message_template_item_list is not None

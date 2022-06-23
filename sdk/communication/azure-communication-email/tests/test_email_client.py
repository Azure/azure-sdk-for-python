# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import unittest
from unittest.mock import Mock

from unittest_helpers import mock_response
from azure.communication.email import (
    EmailClient,
    EmailMessage,
    EmailContent,
    EmailRecipients,
    EmailAddress
)


class TestEmailClient(unittest.TestCase):
    def test_send(self):

        message = EmailMessage(
            sender="someSender@contoso.com",
            content=EmailContent(subject="This is the subject", plain_text="This is the body"),
            recipients=EmailRecipients(
                to=[EmailAddress(email="someRecipient@domain.com", display_name="Customer Name")]
            )
        )

        def mock_send(*_, **__):
            return mock_response(status_code=202, headers={
                'x-ms-request-id': "testMessageId"
            })

        email_client = EmailClient(
            conn_str="endpoint=https://someEndpoint/;accesskey=someAccessKeyw==",
            transport = Mock(send=mock_send)
        )

        response = None
        raised = False
        try:
            response = email_client.send(message)
        except:
            raised = True
            raise

        self.assertFalse(raised, 'Expected is no exception raised')
        self.assertIsNotNone(response.message_id)

    def test_get_send_status(self):

        def mock_get_send_status(*_, **__):
            return mock_response(status_code=200, json_payload={"test": "test"})

        email_client = EmailClient(
            conn_str="endpoint=https://someEndpoint/;accesskey=someAccessKeyw==",
            transport = Mock(send=mock_get_send_status)
        )
        response = None
        raised = False
        try:
            response = email_client.get_send_status("testMessageId")
        except:
            raised = True
            raise

        self.assertFalse(raised, 'Expected is no exception raised')
        self.assertIsNotNone(response)
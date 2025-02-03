# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from azure.communication.email import EmailClient
from devtools_testutils import AzureRecordedTestCase, recorded_by_proxy
from preparers import email_decorator


class TestEmailClient(AzureRecordedTestCase):
    @email_decorator
    @recorded_by_proxy
    def test_send_email_single_recipient(self):
        email_client = EmailClient.from_connection_string(self.communication_connection_string)

        message = {
            "content": {
                "subject": "This is the subject",
                "plainText": "This is the body",
            },
            "recipients": {"to": [{"address": self.recipient_address, "displayName": "Customer Name"}]},
            "senderAddress": self.sender_address,
        }

        poller = email_client.begin_send(message)
        response = poller.result()
        assert response["status"] == "Succeeded"

    @email_decorator
    @recorded_by_proxy
    def test_send_email_multiple_recipients(self):
        email_client = EmailClient.from_connection_string(self.communication_connection_string)

        message = {
            "content": {
                "subject": "This is the subject",
                "plainText": "This is the body",
            },
            "recipients": {
                "to": [
                    {"address": self.recipient_address, "displayName": "Customer Name"},
                    {"address": self.recipient_address, "displayName": "Customer Name 2"},
                ]
            },
            "senderAddress": self.sender_address,
        }

        poller = email_client.begin_send(message)
        response = poller.result()
        assert response["status"] == "Succeeded"

    @email_decorator
    @recorded_by_proxy
    def test_send_email_attachment(self):
        email_client = EmailClient.from_connection_string(self.communication_connection_string)

        message = {
            "content": {
                "subject": "This is the subject",
                "plainText": "This is the body",
            },
            "recipients": {"to": [{"address": self.recipient_address, "displayName": "Customer Name"}]},
            "senderAddress": self.sender_address,
            "attachments": [
                {
                    "name": "readme.txt",
                    "contentType": "text/plain",
                    "contentInBase64": "ZW1haWwgdGVzdCBhdHRhY2htZW50",  # cspell:disable-line
                }
            ],
        }

        poller = email_client.begin_send(message)
        response = poller.result()
        assert response["status"] == "Succeeded"

    @email_decorator
    @recorded_by_proxy
    def test_send_email_inline_attachment(self):
        email_client = EmailClient.from_connection_string(self.communication_connection_string)

        message = {
            "content": {
                "subject": "This is the subject",
                "plainText": "This is the body",
                "html": '<html>This is the body<br /><img src="cid:my-inline-image" /></html>',
            },
            "recipients": {"to": [{"address": self.recipient_address, "displayName": "Customer Name"}]},
            "senderAddress": self.sender_address,
            "attachments": [
                {
                    "name": "inline_image.bmp",
                    "contentType": "image/bmp",
                    "contentInBase64": "Qk06AAAAAAAAADYAAAAoAAAAAQAAAAEAAAABABgAAAAAAAQAAAAAAAAAAAAAAAAAAAAAAAAAzFUzAA==",  # cspell:disable-line
                    "contentId": "my-inline-image",
                }
            ],
        }

        poller = email_client.begin_send(message)
        response = poller.result()
        assert response["status"] == "Succeeded"

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
            "recipients": {
                "to": [
                    {
                        "email": self.recipient_address,
                        "displayName": "Customer Name"
                    }
                ]
            },
            "sender": self.sender_address
        }

        response = email_client.send(message)
        assert response['messageId'] is not None

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
                    {
                        "email": self.recipient_address,
                        "displayName": "Customer Name"
                    },
                    {
                        "email": self.recipient_address,
                        "displayName": "Customer Name 2"
                    }
                ]
            },
            "sender": self.sender_address
        }

        response = email_client.send(message)
        assert response['messageId'] is not None

    @email_decorator
    @recorded_by_proxy
    def test_send_email_attachment(self):
        email_client = EmailClient.from_connection_string(self.communication_connection_string)

        message = {
            "content": {
                "subject": "This is the subject",
                "plainText": "This is the body",
            },
            "recipients": {
                "to": [
                    {
                        "email": self.recipient_address,
                        "displayName": "Customer Name"
                    }
                ]
            },
            "sender": self.sender_address,
            "attachments": [
                {
                    "name": "readme.txt",
                    "attachmentType": "txt",
                    "contentBytesBase64": "ZW1haWwgdGVzdCBhdHRhY2htZW50" #cspell:disable-line
                }
            ]
        }

        response = email_client.send(message)
        assert response['messageId'] is not None

    @email_decorator
    @recorded_by_proxy
    def test_check_message_status(self):
        email_client = EmailClient.from_connection_string(self.communication_connection_string)

        message = {
            "content": {
                "subject": "This is the subject",
                "plainText": "This is the body",
            },
            "recipients": {
                "to": [
                    {
                        "email": self.recipient_address,
                        "displayName": "Customer Name"
                    }
                ]
            },
            "sender": self.sender_address
        }

        response = email_client.send(message)
        message_id = response['messageId']
        if message_id is not None:
            message_status_response = email_client.get_send_status(message_id)
            assert message_status_response['status'] is not None
        else:
            assert False

    @email_decorator
    @recorded_by_proxy
    def test_send_email_empty_to_recipients(self):
        email_client = EmailClient.from_connection_string(self.communication_connection_string)

        message = {
            "content": {
                "subject": "This is the subject",
                "plainText": "This is the body",
            },
            "recipients": {
                "cc": [
                    {
                        "email": self.recipient_address,
                        "displayName": "Customer Name"
                    }
                ],
                "bcc": [
                    {
                        "email": self.recipient_address,
                        "displayName": "Customer Name"
                    }
                ],
            },
            "sender": self.sender_address
        }

        response = email_client.send(message)
        assert response['messageId'] is not None

import pytest

from azure.communication.email.aio import EmailClient
from devtools_testutils import AzureRecordedTestCase
from devtools_testutils.aio import recorded_by_proxy_async
from async_preparers import email_decorator_async

class TestEmailClient(AzureRecordedTestCase):
    @email_decorator_async
    @recorded_by_proxy_async
    async def test_send_email_single_recipient(self):
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

        async with email_client:
            response = await email_client.send(message)
            assert response['message_id'] is not None

    @email_decorator_async
    @recorded_by_proxy_async
    async def test_send_email_multiple_recipients(self):
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

        async with email_client:
            response = await email_client.send(message)
            assert response['message_id'] is not None

    @email_decorator_async
    @recorded_by_proxy_async
    async def test_send_email_attachment(self):
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

        async with email_client:
            response = await email_client.send(message)
            assert response['message_id'] is not None

    @email_decorator_async
    @recorded_by_proxy_async
    async def test_check_message_status(self):
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

        async with email_client:
            response = await email_client.send(message)
            message_id = response['message_id']
            if message_id is not None:
                message_status_response = await email_client.get_send_status(message_id)
                assert message_status_response['status'] is not None
            else:
                assert False

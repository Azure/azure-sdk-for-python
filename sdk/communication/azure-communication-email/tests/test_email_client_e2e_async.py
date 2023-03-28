# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
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
                        "address": self.recipient_address,
                        "displayName": "Customer Name"
                    }
                ]
            },
            "senderAddress": self.sender_address
        }

        async with email_client:
            poller = await email_client.begin_send(message)
            response = await poller.result()
            assert response['status'] == "Succeeded"

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
                        "address": self.recipient_address,
                        "displayName": "Customer Name"
                    },
                    {
                        "address": self.recipient_address,
                        "displayName": "Customer Name 2"
                    }
                ]
            },
            "senderAddress": self.sender_address
        }

        async with email_client:
            poller = await email_client.begin_send(message)
            response = await poller.result()
            assert response['status'] == "Succeeded"


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
                        "address": self.recipient_address,
                        "displayName": "Customer Name"
                    }
                ]
            },
            "senderAddress": self.sender_address,
            "attachments": [
                {
                    "name": "readme.txt",
                    "contentType": "text/plain",
                    "contentInBase64": "ZW1haWwgdGVzdCBhdHRhY2htZW50" #cspell:disable-line
                }
            ]
        }

        async with email_client:
            poller = await email_client.begin_send(message)
            response = await poller.result()
            assert response['status'] == "Succeeded"

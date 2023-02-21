# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: send_email_to_multiple_recipient_sample_async.py
DESCRIPTION:
    This sample demonstrates sending an email to multiple recipients. The Email client is 
    authenticated using a connection string.
USAGE:
    python send_email_to_single_recipient_sample.py
    Set the environment variable with your own value before running the sample:
    1) COMMUNICATION_CONNECTION_STRING_EMAIL - the connection string in your ACS resource
    2) SENDER_ADDRESS - the address found in the linked domain that will send the email
    3) RECIPIENT_ADDRESS - the address that will receive the email
    4) SECOND_RECIPIENT_ADDRESS - the second address that will receive the email
"""

import os
import sys
import asyncio
from azure.core.exceptions import HttpResponseError
from azure.communication.email.aio import EmailClient

sys.path.append("..")

class EmailMultipleRecipientSampleAsync(object):

    connection_string = os.getenv("COMMUNICATION_CONNECTION_STRING_EMAIL")
    sender_address = os.getenv("SENDER_ADDRESS")
    recipient_address = os.getenv("RECIPIENT_ADDRESS")
    second_recipient_address = os.getenv("SECOND_RECIPIENT_ADDRESS")

    async def send_email_to_multiple_recipients_async(self):
        # creating the email client
        email_client = EmailClient.from_connection_string(self.connection_string)

        # creating the email message
        message = {
            "content": {
                "subject": "This is the subject",
                "plainText": "This is the body",
                "html": "html><h1>This is the body</h1></html>"
            },
            "recipients": {
                "to": [
                    {"address": self.recipient_address, "displayName": "Customer Name"},
                    {"address": self.second_recipient_address, "displayName": "Customer Name 2"}
                ],
                "cc": [
                    {"address": self.recipient_address, "displayName": "Customer Name"},
                    {"address": self.second_recipient_address, "displayName": "Customer Name 2"}
                ],
                "bcc": [
                    {"address": self.recipient_address, "displayName": "Customer Name"},
                    {"address": self.second_recipient_address, "displayName": "Customer Name 2"}
                ]
            },
            "senderAddress": self.sender_address
        }

        async with email_client:
            try:
                # sending the email message
                poller = await email_client.begin_send(message)
                response = await poller.result()
                print("Operation ID: " + response['id'])
            except HttpResponseError as ex:
                print(ex)
                pass

if __name__ == '__main__':
    sample = EmailMultipleRecipientSampleAsync()
    asyncio.run(sample.send_email_to_multiple_recipients_async())

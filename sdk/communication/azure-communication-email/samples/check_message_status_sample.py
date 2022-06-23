# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: check_message_status.py
DESCRIPTION:
    This sample demonstrates checking the status of a sent email. The Email client is 
    authenticated using a connection string.
USAGE:
    python check_message_status.py
    Set the environment variable with your own value before running the sample:
    1) COMMUNICATION_CONNECTION_STRING - the connection string in your ACS resource
    2) SENDER_ADDRESS - the address found in the linked domain that will send the email
    3) RECIPIENT_ADDRESS - the address that will recieve the email
"""

import os
import sys
from azure.communication.email import (
    EmailClient,
    EmailContent,
    EmailRecipients,
    EmailAddress,
    EmailMessage
)

sys.path.append("..")

class EmailCheckMessageStatusSample(object):

    connection_string = os.getenv("COMMUNICATION_CONNECTION_STRING")
    sender_address = os.getenv("SENDER_ADDRESS")
    recipient_address = os.getenv("RECIPIENT_ADDRESS")
    
    def check_message_status(self):
        # creating the email client
        email_client = EmailClient(self.connection_string)

        # creating the email message
        content = EmailContent(
            subject="This is the subject",
            plain_text="This is the body",
            html= "<html><h1>This is the body</h1></html>",
        )

        recipients = EmailRecipients(
            to=[EmailAddress(email=self.recipient_address, display_name="Customer Name")]
        )

        message = EmailMessage(
            sender=self.sender_address,
            content=content,
            recipients=recipients
        )

        # sending the email message
        response = email_client.send(message)

        # using the message id to get the status of the email
        message_id = response.message_id
        message_status = email_client.get_send_status(message_id)

        print("Message Status: " + message_status.status)

if __name__ == '__main__':
    sample = EmailCheckMessageStatusSample()
    sample.check_message_status()

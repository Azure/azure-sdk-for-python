# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: send_text_notification_messages_with_token_credentials.py

DESCRIPTION:
    This sample demonstrates sending an Whatsapp message from business phone number to a single user. The NotificationMessageClient is 
    authenticated using Bearer TokenCredentials with azureidentity.
    More information here: https://learn.microsoft.com/python/api/overview/azure/identity-readme?view=azure-python
USAGE:
    python send_text_notification_messages_with_token_credentials.py

    Set the environment variable with your own value before running the sample:
    1) COMMUNICATION_SAMPLES_CONNECTION_STRING - the connection string in your ACS resource
    2) RECIPIENT_PHONE_NUMBER - a phone number with Whatsapp capabilities. Use list for recipient phone number.
    3) WHATSAPP_CHANNEL_ID - Channel created in Azure portal for Advanced Messaging.
    4) Follow defining environment variables for DefaultAzureCredentials as give here:
        https://learn.microsoft.com/python/api/overview/azure/identity-readme?view=azure-python#environment-variables
        https://learn.microsoft.com/entra/identity-platform/howto-create-service-principal-portal
        Variable name	      Value
        AZURE_CLIENT_ID     ID of a Microsoft Entra application
        AZURE_TENANT_ID     ID of the application's Microsoft Entra tenant
        AZURE_CLIENT_SECRET one of the application's client secrets
"""

import os
import sys

sys.path.append("..")


class SendWhatsAppMessageSample(object):

    endpoint_string = os.getenv("COMMUNICATION_SAMPLES_ENDPOINT_STRING")
    phone_number = os.getenv("RECIPIENT_PHONE_NUMBER")
    channel_id = os.getenv("WHATSAPP_CHANNEL_ID")

    def send_text_send_message(self):

        from azure.communication.messages import NotificationMessagesClient
        from azure.communication.messages.models import TextNotificationContent
        from azure.identity import DefaultAzureCredential

        messaging_client = NotificationMessagesClient(
            endpoint=self.endpoint_string, credential=DefaultAzureCredential()
        )

        text_options = TextNotificationContent(
            channel_registration_id=self.channel_id,
            to=[self.phone_number],
            content="Hello World via Notification Messaging SDK using Token credentials.",
        )

        # calling send() with whatsapp message details
        message_responses = messaging_client.send(text_options)
        response = message_responses.receipts[0]
        print("Message with message id {} was successful sent to {}".format(response.message_id, response.to))


if __name__ == "__main__":
    sample = SendWhatsAppMessageSample()
    sample.send_text_send_message()

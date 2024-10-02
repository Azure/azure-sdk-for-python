# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: send_template_notification_messages.py

DESCRIPTION:
    This sample demonstrates sending an Whatsapp template message from business phone number to a single user. 
    Template to be used in the sample needs to be created in WhatsApp Business account first.
    Follow the instructions in the Meta Business Help Center at https://www.facebook.com/business/help/2055875911147364?id=2129163877102343.
    The NotificationMessageClient is authenticated using a connection string.
USAGE:
    python send_template_notification_messages.py

    Set the environment variable with your own value before running the sample:
    1) COMMUNICATION_SAMPLES_CONNECTION_STRING - the connection string in your ACS resource
    2) RECIPIENT_PHONE_NUMBER - a phone number with Whatsapp capabilities. Use list for recipient phone number.
    3) WHATSAPP_CHANNEL_ID - Channel created in Azure portal for Advanced Messaging.
"""

import os
import sys

sys.path.append("..")


class SendWhatsAppTemplateMessageSample(object):

    connection_string = os.getenv("COMMUNICATION_SAMPLES_CONNECTION_STRING")
    phone_number = os.getenv("RECIPIENT_PHONE_NUMBER")
    channel_id = os.getenv("WHATSAPP_CHANNEL_ID")

    def send_template_send_message(self):

        from azure.communication.messages import NotificationMessagesClient
        from azure.communication.messages.models import TemplateNotificationContent, MessageTemplate

        messaging_client = NotificationMessagesClient.from_connection_string(self.connection_string)

        # Setting template options
        input_template: MessageTemplate = MessageTemplate(
            name="gathering_invitation", language="ca"  # Name of the WhatsApp Template
        )  # Language of the WhatsApp Template
        template_options = TemplateNotificationContent(
            channel_registration_id=self.channel_id, to=[self.phone_number], template=input_template
        )

        # calling send() with whatsapp message details
        message_responses = messaging_client.send(template_options)
        response = message_responses.receipts[0]
        print("Message with message id {} was successful sent to {}".format(response.message_id, response.to))


if __name__ == "__main__":
    sample = SendWhatsAppTemplateMessageSample()
    sample.send_template_send_message()

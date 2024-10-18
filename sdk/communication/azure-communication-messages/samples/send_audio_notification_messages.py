# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: send_audio_notification_messages.py

DESCRIPTION:
    This sample demonstrates sending an Whatsapp audio message from business phone number to a single user. The NotificationMessageClient is 
    authenticated using a connection string.
USAGE:
    python send_audio_notification_messages.py

    Set the environment variable with your own value before running the sample:
    1) COMMUNICATION_SAMPLES_CONNECTION_STRING - the connection string in your ACS resource
    2) RECIPIENT_PHONE_NUMBER - a phone number with Whatsapp capabilities. Use list for recipient phone number.
    3) WHATSAPP_CHANNEL_ID - Channel created in Azure portal for Advanced Messaging.
"""

import os
import sys

sys.path.append("..")


class SendWhatsAppMessageSample(object):

    connection_string: str = os.getenv("COMMUNICATION_SAMPLES_CONNECTION_STRING")  # type: ignore
    phone_number: str = os.getenv("RECIPIENT_PHONE_NUMBER")  # type: ignore
    channel_id: str = os.getenv("WHATSAPP_CHANNEL_ID")  # type: ignore

    def send_audio_message(self):

        from azure.communication.messages import NotificationMessagesClient
        from azure.communication.messages.models import AudioNotificationContent

        messaging_client = NotificationMessagesClient.from_connection_string(self.connection_string)

        audio_options = AudioNotificationContent(
            channel_registration_id=self.channel_id,
            to=[self.phone_number],
            media_uri="https://filesamples.com/samples/audio/mp3/sample3.mp3",
        )

        # calling send() with whatsapp message details
        message_responses = messaging_client.send(audio_options)
        response = message_responses.receipts[0]
        print("Message with message id {} was successful sent to {}".format(response.message_id, response.to))


if __name__ == "__main__":
    sample = SendWhatsAppMessageSample()
    sample.send_audio_message()

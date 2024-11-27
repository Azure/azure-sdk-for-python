# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: send_whatsapplist_notification_messages.py

DESCRIPTION:
    This sample demonstrates sending an Whatsapp message from business phone number to a single user. The NotificationMessageClient is 
    authenticated using a connection string.
USAGE:
    python send_whatsapplist_notification_messages.py

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

    def send_whatsapplist_message(self):

        from azure.communication.messages import NotificationMessagesClient
        from azure.communication.messages.models import (
            ActionSetContent,
            ActionSet,
            ActionSetItem,
            InteractiveMessage,
            TextMessageContent,
            WhatsAppListActionBindings,
            InteractiveNotificationContent,
        )

        messaging_client = NotificationMessagesClient.from_connection_string(self.connection_string)

        action_item_list1 = [
            ActionSetItem(id="priority_express", title="Priority Mail Express", description="Next Day to 2 Days"),
            ActionSetItem(id="priority_mail", title="Priority Mail", description="1–3 Days"),
        ]
        action_item_list2 = [
            ActionSetItem(id="usps_ground_advantage", title="USPS Ground Advantage", description="2-5 Days"),
            ActionSetItem(id="media_mail", title="Media Mail", description="2-8 Days"),
        ]
        action_set = [
            ActionSet(title="I want it ASAP!", items_property=action_item_list1),
            ActionSet(title="I can wait a bit", items_property=action_item_list2),
        ]

        action_set_content = ActionSetContent(title="Shipping Options", action_set=action_set)

        interactionMessage = InteractiveMessage(
            body=TextMessageContent(text="Test Body"),
            footer=TextMessageContent(text="Test Footer"),
            header=TextMessageContent(text="Test Header"),
            action_bindings=WhatsAppListActionBindings(action=action_set_content),
        )
        interactiveMessageContent = InteractiveNotificationContent(
            channel_registration_id=self.channel_id,
            to=[self.phone_number],
            interactive_message=interactionMessage,
        )

        # calling send() with whatsapp message details
        message_responses = messaging_client.send(interactiveMessageContent)
        response = message_responses.receipts[0]
        print("Message with message id {} was successful sent to {}".format(response.message_id, response.to))


if __name__ == "__main__":
    sample = SendWhatsAppMessageSample()
    sample.send_whatsapplist_message()

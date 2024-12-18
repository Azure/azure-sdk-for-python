# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: get_templates_list.py

DESCRIPTION:
    This sample demonstrates fetching WhatsApp templates created in your WhatsApp Business account. The NotificationMessageClient is 
    authenticated using a connection string.
USAGE:
    python get_templates_list.py

    Set the environment variable with your own value before running the sample:
    1) COMMUNICATION_SAMPLES_CONNECTION_STRING - the connection string in your ACS resource
    2) WHATSAPP_CHANNEL_ID - Channel created in Azure portal for Advanced Messaging.
"""

import os
import sys

sys.path.append("..")


class GetTemplatesSample(object):

    connection_string = os.getenv("COMMUNICATION_SAMPLES_CONNECTION_STRING")
    channel_id = os.getenv("WHATSAPP_CHANNEL_ID")

    def get_templates_list(self):

        from azure.communication.messages import MessageTemplateClient
        from azure.communication.messages.models import TextNotificationContent

        message_template_client = MessageTemplateClient.from_connection_string(self.connection_string)

        # calling send() with whatsapp message details
        template_list = message_template_client.list_templates(self.channel_id)

        count_templates = len(list(template_list))
        print("Successfully retrieved {} templates from channel_id {}.".format(count_templates, self.channel_id))


if __name__ == "__main__":
    sample = GetTemplatesSample()
    sample.get_templates_list()

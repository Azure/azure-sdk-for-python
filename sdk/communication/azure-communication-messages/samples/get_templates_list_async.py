# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: get_templates_list_async.py

DESCRIPTION:
    This sample demonstrates fetching WhatsApp templates created in your WhatsApp Business account. The NotificationMessageClient is 
    authenticated using a connection string.
USAGE:
    python get_templates_list_async.py

    Set the environment variable with your own value before running the sample:
    1) COMMUNICATION_SAMPLES_CONNECTION_STRING - the connection string in your ACS resource
    2) WHATSAPP_CHANNEL_ID - Channel created in Azure portal for Advanced Messaging.
"""

import asyncio
import os
import sys

sys.path.append("..")


class GetTemplatesSampleAsync(object):

    connection_string = os.getenv("COMMUNICATION_SAMPLES_CONNECTION_STRING")
    channel_id = os.getenv("WHATSAPP_CHANNEL_ID")

    async def get_templates_list_async(self):

        from azure.communication.messages.aio import MessageTemplateClient

        message_template_client = MessageTemplateClient.from_connection_string(self.connection_string)

        # calling send() with whatsapp message details
        async with message_template_client:
            template_list = message_template_client.list_templates(self.channel_id)
            async_list_data = [x async for x in template_list]
            count_templates = len(list(async_list_data))
            print("Successfully retrieved {} templates from channel_id {}.".format(count_templates, self.channel_id))


async def main():
    sample = GetTemplatesSampleAsync()
    await sample.get_templates_list_async()


if __name__ == "__main__":
    asyncio.run(main())

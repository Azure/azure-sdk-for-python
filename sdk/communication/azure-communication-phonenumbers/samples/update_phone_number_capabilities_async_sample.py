# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: update_phone_number_capabilities_async_sample.py
DESCRIPTION:
    This sample demonstrates how to update the capabilities of a phone number using your connection string.
USAGE:
    python update_phone_number_capabilities_sample.py
    Set the environment variables with your own values before running the sample:
    1) AZURE_COMMUNICATION_SERVICE_CONNECTION_STRING - The connection string including your endpoint and 
        access key of your Azure Communication Service
    2) AZURE_COMMUNICATION_SERVICE_PHONE_NUMBER_TO_UPDATE - The phone number you want to update
"""

import asyncio
import os
from azure.communication.phonenumbers.aio import PhoneNumbersClient
from azure.communication.phonenumbers import PhoneNumberCapabilityType

connection_str = os.getenv('AZURE_COMMUNICATION_SERVICE_CONNECTION_STRING')
phone_number_to_update = os.getenv(
    "AZURE_COMMUNICATION_SERVICE_PHONE_NUMBER_TO_UPDATE" # e.g. "+15551234567"
) 
phone_numbers_client = PhoneNumbersClient.from_connection_string(connection_str)

async def update_phone_number_capabilities():
    async with phone_numbers_client:
        poller = await phone_numbers_client.begin_update_phone_number_capabilities(
            phone_number_to_update,
            PhoneNumberCapabilityType.OUTBOUND,
            PhoneNumberCapabilityType.INBOUND_OUTBOUND,
            polling = True
        )
        await poller.result()
    print('Status of the operation: ' + poller.status())

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(update_phone_number_capabilities())

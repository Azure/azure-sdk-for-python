# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: search_available_phone_numbers_async_sample.py
DESCRIPTION:
    This sample demonstrates how to search for available numbers you can buy with the respective API.
USAGE:
    python search_available_phone_numbers_sample.py
    Set the environment variables with your own values before running the sample:
    1) AZURE_COMMUNICATION_SERVICE_CONNECTION_STRING - The connection string including your endpoint and 
        access key of your Azure Communication Service
"""

import asyncio
import os
from azure.communication.phonenumbers.aio import PhoneNumbersClient
from azure.communication.phonenumbers import (
    PhoneNumberType,
    PhoneNumberAssignmentType,
    PhoneNumberCapabilities,
    PhoneNumberCapabilityType
)

connection_str = os.getenv('AZURE_COMMUNICATION_SERVICE_CONNECTION_STRING')
phone_numbers_client = PhoneNumbersClient.from_connection_string(connection_str)

async def search_available_phone_numbers():
    async with phone_numbers_client:
        capabilities = PhoneNumberCapabilities(
            calling = PhoneNumberCapabilityType.INBOUND,
            sms = PhoneNumberCapabilityType.INBOUND_OUTBOUND
        )
        poller = await phone_numbers_client.begin_search_available_phone_numbers(
            "US",
            PhoneNumberType.TOLL_FREE,
            PhoneNumberAssignmentType.APPLICATION,
            capabilities,
            polling = True
        )
        search_result = await poller.result()
        print ('Search id: ' + search_result.search_id)
        phone_number_list = search_result.phone_numbers
        print('Reserved phone numbers:')
        for phone_number in phone_number_list:
            print(phone_number)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(search_available_phone_numbers())

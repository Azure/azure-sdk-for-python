# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE:get_purchased_phone_number_async_sample.py
DESCRIPTION:
    This sample demonstrates how to get the information from an acquired phone number using your connection string
USAGE:
    python get_purchased_phone_number_sample.py
    Set the environment variables with your own values before running the sample:
    1) COMMUNICATION_SAMPLES_CONNECTION_STRING - The connection string including your endpoint and 
        access key of your Azure Communication Service
    2) AZURE_PHONE_NUMBER - The phone number you want to get its information
"""

import asyncio
import os
from azure.communication.phonenumbers.aio import (
    PhoneNumbersClient
)

connection_str = os.getenv('COMMUNICATION_SAMPLES_CONNECTION_STRING')
phone_number = os.getenv("AZURE_PHONE_NUMBER") # e.g. "+18001234567"
phone_numbers_client = PhoneNumbersClient.from_connection_string(connection_str)

async def get_purchased_phone_number_information():
    async with phone_numbers_client:
        purchased_phone_number_information = await phone_numbers_client.get_purchased_phone_number(phone_number)
    print('Phone number: ' + purchased_phone_number_information.phone_number)
    print('Country code: ' + purchased_phone_number_information.country_code)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(get_purchased_phone_number_information())

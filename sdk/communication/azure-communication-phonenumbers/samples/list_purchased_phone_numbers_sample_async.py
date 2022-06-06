# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: list_purchased_phone_numbers_async_sample.py
DESCRIPTION:
    This sample demonstrates how to get all of you acquired phone numbers using your connection string
USAGE:
    python list_purchased_phone_numbers_sample.py
    Set the environment variables with your own values before running the sample:
    1) COMMUNICATION_SAMPLES_CONNECTION_STRING - The connection string including your endpoint and 
        access key of your Azure Communication Service
"""

import asyncio
import os
from azure.communication.phonenumbers.aio import (
    PhoneNumbersClient
)

connection_str = os.getenv('COMMUNICATION_SAMPLES_CONNECTION_STRING')
phone_numbers_client = PhoneNumbersClient.from_connection_string(connection_str)

async def list_purchased_phone_numbers():
    async with phone_numbers_client:
        purchased_phone_numbers = phone_numbers_client.list_purchased_phone_numbers()
        print("Purchased Phone Numbers:")
        async for item in purchased_phone_numbers:
            print(item.phone_number)


if __name__ == '__main__':
    asyncio.run(list_purchased_phone_numbers())

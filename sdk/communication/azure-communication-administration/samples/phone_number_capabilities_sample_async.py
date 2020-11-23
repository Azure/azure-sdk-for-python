# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: phone_number_capabilities_sample_async.py
DESCRIPTION:
    This sample demonstrates how to get number capabilities via a connection string, capabilities update id and phone number for capabilities.
USAGE:
    python phone_number_capabilities_sample_async.py
    Set the environment variables with your own values before running the sample:
    1) AZURE_COMMUNICATION_SERVICE_CONNECTION_STRING - The endpoint of your Azure Communication Service
    2) AZURE_COMMUNICATION_SERVICE_PHONENUMBERS_CAPABILITIES_ID - The capabilities id you want to get
    3) AZURE_COMMUNICATION_SERVICE_PHONENUMBERS_PHONENUMBER_FOR_CAPABILITIES - The phone number you want to update capabilities to
"""

import asyncio
import os
from azure.communication.administration.aio import PhoneNumberAdministrationClient
from azure.communication.administration import NumberUpdateCapabilities


connection_str = os.getenv('AZURE_COMMUNICATION_SERVICE_CONNECTION_STRING')
capabilities_id = os.getenv('AZURE_COMMUNICATION_SERVICE_PHONENUMBERS_CAPABILITIES_ID', "capabilities-id")
phonenumber_for_capabilities = os.getenv('AZURE_COMMUNICATION_SERVICE_PHONENUMBERS_PHONENUMBER_FOR_CAPABILITIES',
                                                      "phone-number-for-capabilities")


async def list_all_phone_numbers():
    # [START list_all_phone_numbers]
    phone_number_administration_client = PhoneNumberAdministrationClient.from_connection_string(connection_str)
    async with phone_number_administration_client:
        list_all_phone_numbers_response = phone_number_administration_client.list_all_phone_numbers()
        print('list_all_phone_numbers_response:')
        async for phone_number in list_all_phone_numbers_response:
            print(phone_number)
    # [END list_all_phone_numbers]


async def get_capabilities_update():
    # [START get_capabilities_update]
    phone_number_administration_client = PhoneNumberAdministrationClient.from_connection_string(connection_str)
    async with phone_number_administration_client:
        capabilities_response = await phone_number_administration_client.get_capabilities_update(
            capabilities_update_id=capabilities_id
        )
        print('capabilities_response:')
        print(capabilities_response)
    # [END get_capabilities_update]


async def update_capabilities():
    # [START update_capabilities]
    phone_number_administration_client = PhoneNumberAdministrationClient.from_connection_string(connection_str)
    update = NumberUpdateCapabilities(add=iter(["InboundCalling"]))

    phone_number_capabilities_update = {
        phonenumber_for_capabilities: update
    }

    async with phone_number_administration_client:
        capabilities_response = await phone_number_administration_client.update_capabilities(
            phone_number_capabilities_update=phone_number_capabilities_update
        )
        print('capabilities_response:')
        print(capabilities_response)
    # [END update_capabilities]


async def main():
    await list_all_phone_numbers()
    await get_capabilities_update()
    await update_capabilities()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())

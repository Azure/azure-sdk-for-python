# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: phone_number_configuration_sample_async.py
DESCRIPTION:
    This sample demonstrates how to configure phone numbers and get phone number configuration via a connection string and phone number to configure
USAGE:
    python phone_number_configuration_sample_async.py
    Set the environment variables with your own values before running the sample:
    1) AZURE_COMMUNICATION_SERVICE_CONNECTION_STRING - The endpoint of your Azure Communication Service
    2) AZURE_COMMUNICATION_SERVICE_PHONENUMBERS_PHONENUMBER_TO_CONFIGURE - The phone number you want to configure
"""

import os
import asyncio
from azure.communication.administration.aio import PhoneNumberAdministrationClient
from azure.communication.administration import PstnConfiguration

connection_str = os.getenv('AZURE_COMMUNICATION_SERVICE_CONNECTION_STRING')
phonenumber_to_configure = os.getenv('AZURE_COMMUNICATION_SERVICE_PHONENUMBERS_PHONENUMBER_TO_CONFIGURE',
                                                  "phonenumber_to_configure")


async def get_number_configuration():
    # [START get_number_configuration]
    phone_number_administration_client = PhoneNumberAdministrationClient.from_connection_string(connection_str)
    async with phone_number_administration_client:
        phone_number_configuration_response = await phone_number_administration_client.get_number_configuration(
            phone_number=phonenumber_to_configure
        )
        print('phone_number_configuration_response:')
        print(phone_number_configuration_response)
    # [END get_number_configuration]


async def configure_number():
    # [START configure_number]
    phone_number_administration_client = PhoneNumberAdministrationClient.from_connection_string(connection_str)
    pstn_config = PstnConfiguration(
        callback_url="https://callbackurl",
        application_id="ApplicationId"
    )
    async with phone_number_administration_client:
        await phone_number_administration_client.configure_number(
            pstn_configuration=pstn_config,
            phone_number=phonenumber_to_configure
        )
    # [END configure_number]


async def main():
    await get_number_configuration()
    await configure_number()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())

# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: phone_number_capabilities_sample.py
DESCRIPTION:
    These samples demonstrate number capabilities samples.

    ///getting number capabilities via a connection string, capabilities update id and phone number for capabilities
USAGE:
    python phone_number_capabilities_sample.py
"""
import asyncio
import os
from azure.communication.administration.aio import PhoneNumberAdministrationClient
from azure.communication.administration import NumberUpdateCapabilities


class CommunicationNumberCapabilitiesSamplesAsync(object):

    def __init__(self):
        self.connection_str = os.getenv('AZURE_COMMUNICATION_SERVICE_CONNECTION_STRING')
        self.capabilities_id = os.getenv('AZURE_COMMUNICATION_SERVICE_TNM_CAPABILITIES_ID', "capabilities-id")
        self.phonenumber_for_capabilities = os.getenv('AZURE_COMMUNICATION_SERVICE_TNM_PHONENUMBER_FOR_CAPABILITIES',
                                                      "phone-number-for-capabilities")

    async def list_all_phone_numbers(self):
        self._phone_number_administration_client = PhoneNumberAdministrationClient.from_connection_string(
            self.connection_str)
        async with self._phone_number_administration_client:
            list_all_phone_numbers_response = self._phone_number_administration_client.list_all_phone_numbers()
            print('list_all_phone_numbers_response:')
            async for phone_number in list_all_phone_numbers_response:
                print(phone_number)

    async def get_capabilities_update(self):
        self._phone_number_administration_client = PhoneNumberAdministrationClient.from_connection_string(
            self.connection_str)
        async with self._phone_number_administration_client:
            capabilities_response = await self._phone_number_administration_client.get_capabilities_update(
                capabilities_update_id=self.capabilities_id
            )
            print('capabilities_response:')
            print(capabilities_response)

    async def update_capabilities(self):
        self._phone_number_administration_client = PhoneNumberAdministrationClient.from_connection_string(
            self.connection_str)
        update = NumberUpdateCapabilities(add=iter(["InboundCalling"]))

        phone_number_capabilities_update = {
            self.phonenumber_for_capabilities: update
        }

        async with self._phone_number_administration_client:
            capabilities_response = await self._phone_number_administration_client.update_capabilities(
                phone_number_capabilities_update=phone_number_capabilities_update
            )
            print('capabilities_response:')
            print(capabilities_response)


async def main():
    sample = CommunicationNumberCapabilitiesSamplesAsync()
    await sample.list_all_phone_numbers()
    await sample.get_capabilities_update()
    await sample.update_capabilities()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())

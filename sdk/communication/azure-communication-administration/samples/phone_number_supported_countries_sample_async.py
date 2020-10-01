# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: phone_number_supported_countries_sample_async.py
DESCRIPTION:
    These samples demonstrate supported countries samples.

    ///getting supported countries via a connection string
USAGE:
    python phone_number_supported_countries_sample_async.py
"""
import os
import asyncio
from azure.communication.administration.aio import PhoneNumberAdministrationClient

class CommunicationSupportedCountriesSamplesAsync(object):

    def __init__(self):
        self.connection_str = os.getenv('AZURE_COMMUNICATION_SERVICE_CONNECTION_STRING')

    async def list_all_supported_countries(self):
        self._phone_number_administration_client = PhoneNumberAdministrationClient.from_connection_string(
            self.connection_str)
        async with self._phone_number_administration_client:
            supported_countries = self._phone_number_administration_client.list_all_supported_countries()
            print('supported_countries:')
            async for supported_country in supported_countries:
                print(supported_country)


async def main():
    sample = CommunicationSupportedCountriesSamplesAsync()
    await sample.list_all_supported_countries()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())

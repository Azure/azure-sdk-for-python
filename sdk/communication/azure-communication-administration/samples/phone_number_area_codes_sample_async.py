# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: phone_number_area_codes_sample.py
DESCRIPTION:
    These samples demonstrate area codes samples.

    ///getting all area codes via a connection string, country code and phone plan id
USAGE:
    python phone_number_area_codes_sample.py
"""
import os
import asyncio
from azure.communication.administration.aio import PhoneNumberAdministrationClient

class CommunicationAreaCodesSamplesAsync(object):

    def __init__(self):
        self.connection_str = os.getenv('AZURE_COMMUNICATION_SERVICE_CONNECTION_STRING')
        self.country_code = os.getenv('AZURE_COMMUNICATION_SERVICE_TNM_COUNTRY_CODE', "US")
        self.phone_plan_id_area_codes = os.getenv('AZURE_COMMUNICATION_SERVICE_TNM_PHONE_PLAN_ID_AREA_CODES', "phone-plan-id")

    async def get_all_area_codes(self):
        self._phone_number_administration_client = PhoneNumberAdministrationClient.from_connection_string(
            self.connection_str)
        async with self._phone_number_administration_client:
            all_area_codes = await self._phone_number_administration_client.get_all_area_codes(
                location_type="NotRequired",
                country_code=self.country_code,
                phone_plan_id=self.phone_plan_id_area_codes
            )
        print('all_area_codes:')
        print(all_area_codes)

async def main():
    sample = CommunicationAreaCodesSamplesAsync()
    await sample.get_all_area_codes()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())

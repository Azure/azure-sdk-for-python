# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: phone_number_area_codes_sample_async.py
DESCRIPTION:
    This sample demonstrates how to get all area codes via a connection string, country code and phone plan id.
USAGE:
    python phone_number_area_codes_sample_async.py
    Set the environment variables with your own values before running the sample:
    1) AZURE_COMMUNICATION_SERVICE_CONNECTION_STRING - The endpoint of your Azure Communication Service
    2) AZURE_COMMUNICATION_SERVICE_PHONENUMBERS_COUNTRY_CODE - The country code you want to get area codes from
    3) AZURE_COMMUNICATION_SERVICE_PHONENUMBERS_PHONE_PLAN_ID_AREA_CODES - The phone plan id you want to get area codes from
"""

import os
import asyncio
from azure.communication.administration.aio import PhoneNumberAdministrationClient

connection_str = os.getenv('AZURE_COMMUNICATION_SERVICE_CONNECTION_STRING')
country_code = os.getenv('AZURE_COMMUNICATION_SERVICE_PHONENUMBERS_COUNTRY_CODE', "US")
phone_plan_id_area_codes = os.getenv('AZURE_COMMUNICATION_SERVICE_PHONENUMBERS_PHONE_PLAN_ID_AREA_CODES', "phone-plan-id")


async def get_all_area_codes():
    # [START get_all_area_codes]
    phone_number_administration_client = PhoneNumberAdministrationClient.from_connection_string(
        connection_str)
    async with phone_number_administration_client:
        all_area_codes = await phone_number_administration_client.get_all_area_codes(
            location_type="NotRequired",
            country_code=country_code,
            phone_plan_id=phone_plan_id_area_codes
        )
    # [END get_all_area_codes]
    print('all_area_codes:')
    print(all_area_codes)


async def main():
    await get_all_area_codes()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())

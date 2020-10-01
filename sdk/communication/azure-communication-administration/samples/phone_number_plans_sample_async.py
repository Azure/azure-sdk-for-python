# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: phone_number_plans_sample_async.py
DESCRIPTION:
    These samples demonstrate phone plan samples.

    ///listing phone plans via a connection string, country code, phone plan id and phone plan group id
USAGE:
    python phone_number_plans_sample_async.py
"""
import os
import asyncio
from azure.communication.administration.aio import PhoneNumberAdministrationClient

class CommunicationPhoneNumberPlansSamplesAsync(object):

    def __init__(self):
        self.connection_str = os.getenv('AZURE_COMMUNICATION_SERVICE_CONNECTION_STRING')
        self.country_code = os.getenv('AZURE_COMMUNICATION_SERVICE_TNM_COUNTRY_CODE', "US")
        self.phone_plan_group_id = os.getenv('AZURE_COMMUNICATION_SERVICE_TNM_PHONE_PLAN_GROUP_ID', "phone-plan-group-id")
        self.phone_plan_id = os.getenv('AZURE_COMMUNICATION_SERVICE_TNM_PHONE_PLAN_ID', "phone-plan-id")

    async def list_phone_plan_groups(self):
        self._phone_number_administration_client = PhoneNumberAdministrationClient.from_connection_string(
            self.connection_str)
        async with self._phone_number_administration_client:
            phone_plan_groups_response = self._phone_number_administration_client.list_phone_plan_groups(
                country_code=self.country_code
            )
            print('list_phone_plan_groups:')
            async for phone_plan_group in phone_plan_groups_response:
                print(phone_plan_group)

    async def list_phone_plans(self):
        self._phone_number_administration_client = PhoneNumberAdministrationClient.from_connection_string(
            self.connection_str)
        async with self._phone_number_administration_client:
            phone_plans_response = self._phone_number_administration_client.list_phone_plans(
                country_code=self.country_code,
                phone_plan_group_id=self.phone_plan_group_id
            )
            print('list_phone_plans:')
            async for phone_plan in phone_plans_response:
                print(phone_plan)

    async def get_phone_plan_location_options(self):
        self._phone_number_administration_client = PhoneNumberAdministrationClient.from_connection_string(
            self.connection_str)
        async with self._phone_number_administration_client:
            location_options_response = await self._phone_number_administration_client.get_phone_plan_location_options(
                country_code=self.country_code,
                phone_plan_group_id=self.phone_plan_group_id,
                phone_plan_id=self.phone_plan_id
            )
            print('get_phone_plan_location_options:')
            print(location_options_response)


async def main():
    sample = CommunicationPhoneNumberPlansSamplesAsync()
    await sample.list_phone_plan_groups()
    await sample.list_phone_plans()
    await sample.get_phone_plan_location_options()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())

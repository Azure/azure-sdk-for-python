# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: phone_number_plans_sample_async.py
DESCRIPTION:
    This sample demonstrates how to list phone plans via a connection string, country code, phone plan id and phone plan group id
USAGE:
    python phone_number_plans_sample_async.py
    Set the environment variables with your own values before running the sample:
    1) AZURE_COMMUNICATION_SERVICE_CONNECTION_STRING - The endpoint of your Azure Communication Service
    2) AZURE_COMMUNICATION_SERVICE_PHONENUMBERS_COUNTRY_CODE - The country code
    3) AZURE_COMMUNICATION_SERVICE_PHONENUMBERS_PHONE_PLAN_GROUP_ID - The phone plan group id you want to use to list phone plans
    4) AZURE_COMMUNICATION_SERVICE_PHONENUMBERS_PHONE_PLAN_ID - The phone plan id you want to use to get location options
"""


import os
import asyncio
from azure.communication.administration.aio import PhoneNumberAdministrationClient

connection_str = os.getenv('AZURE_COMMUNICATION_SERVICE_CONNECTION_STRING')
country_code = os.getenv('AZURE_COMMUNICATION_SERVICE_PHONENUMBERS_COUNTRY_CODE', "US")
phone_plan_group_id = os.getenv('AZURE_COMMUNICATION_SERVICE_PHONENUMBERS_PHONE_PLAN_GROUP_ID', "phone-plan-group-id")
phone_plan_id = os.getenv('AZURE_COMMUNICATION_SERVICE_PHONENUMBERS_PHONE_PLAN_ID', "phone-plan-id")


async def list_phone_plan_groups():
    # [START list_phone_plan_groups]
    phone_number_administration_client = PhoneNumberAdministrationClient.from_connection_string(connection_str)
    async with phone_number_administration_client:
        phone_plan_groups_response = phone_number_administration_client.list_phone_plan_groups(
            country_code=country_code
        )
        print('list_phone_plan_groups:')
        async for phone_plan_group in phone_plan_groups_response:
            print(phone_plan_group)
    # [END list_phone_plan_groups]


async def list_phone_plans():
    # [START list_phone_plans]
    phone_number_administration_client = PhoneNumberAdministrationClient.from_connection_string(connection_str)
    async with phone_number_administration_client:
        phone_plans_response = phone_number_administration_client.list_phone_plans(
            country_code=country_code,
            phone_plan_group_id=phone_plan_group_id
        )
        print('list_phone_plans:')
        async for phone_plan in phone_plans_response:
            print(phone_plan)
    # [END list_phone_plans]


async def get_phone_plan_location_options():
    # [START get_phone_plan_location_options]
    phone_number_administration_client = PhoneNumberAdministrationClient.from_connection_string(connection_str)
    async with phone_number_administration_client:
        location_options_response = await phone_number_administration_client.get_phone_plan_location_options(
            country_code=country_code,
            phone_plan_group_id=phone_plan_group_id,
            phone_plan_id=phone_plan_id
        )
        print('get_phone_plan_location_options:')
        print(location_options_response)
    # [START get_phone_plan_location_options]


async def main():
    await list_phone_plan_groups()
    await list_phone_plans()
    await get_phone_plan_location_options()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())

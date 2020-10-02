# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: phone_number_orders_sample_async.py
DESCRIPTION:
    This sample demonstrates how to list, acquire and cancel phone number orders via a connection string, search id, phone plan id and and area code
USAGE:
    python phone_number_orders_sample_async.py
    Set the environment variables with your own values before running the sample:
    1) AZURE_COMMUNICATION_SERVICE_CONNECTION_STRING - The endpoint of your Azure Communication Service
    2) AZURE_COMMUNICATION_SERVICE_PHONENUMBERS_RELEASE_ID - The release id you want to get info from
    3) AZURE_COMMUNICATION_SERVICE_PHONENUMBERS_SEARCH_ID - The search id you want to get info from
    4) AZURE_COMMUNICATION_SERVICE_PHONENUMBERS_AREA_CODE_FOR_SEARCH - The phone number you want to create search
    5) AZURE_COMMUNICATION_SERVICE_PHONENUMBERS_PHONE_PLAN_ID - The phone plan id
    6) AZURE_COMMUNICATION_SERVICE_PHONENUMBERS_SEARCH_ID_TO_PURCHASE - The search id you want to purchase
    7) AZURE_COMMUNICATION_SERVICE_PHONENUMBERS_SEARCH_ID_TO_CANCEL - The search id you want to cancel
"""

import os
import asyncio
from azure.communication.administration.aio import PhoneNumberAdministrationClient
from azure.communication.administration import CreateSearchOptions

connection_str = os.getenv('AZURE_COMMUNICATION_SERVICE_CONNECTION_STRING')
release_id = os.getenv('AZURE_COMMUNICATION_SERVICE_PHONENUMBERS_RELEASE_ID', "release-id")
search_id = os.getenv('AZURE_COMMUNICATION_SERVICE_PHONENUMBERS_SEARCH_ID', "search-id")
area_code_for_search = os.getenv('AZURE_COMMUNICATION_SERVICE_PHONENUMBERS_AREA_CODE_FOR_SEARCH', "area-code")
phone_plan_id = os.getenv('AZURE_COMMUNICATION_SERVICE_PHONENUMBERS_PHONE_PLAN_ID', "phone-plan-id")
search_id_to_purchase = os.getenv('AZURE_COMMUNICATION_SERVICE_PHONENUMBERS_SEARCH_ID_TO_PURCHASE', "search-id")
search_id_to_cancel = os.getenv('AZURE_COMMUNICATION_SERVICE_PHONENUMBERS_SEARCH_ID_TO_CANCEL', "search-id")


async def get_release_by_id():
    # [START get_release_by_id]
    phone_number_administration_client = PhoneNumberAdministrationClient.from_connection_string(connection_str)
    async with phone_number_administration_client:
        phone_number_release_response = await phone_number_administration_client.get_release_by_id(
            release_id=release_id
        )
        print('phone_number_release_response:')
        print(phone_number_release_response)
    # [END get_release_by_id]


async def list_all_releases():
    # [START list_all_releases]
    phone_number_administration_client = PhoneNumberAdministrationClient.from_connection_string(connection_str)
    async with phone_number_administration_client:
        releases_response = phone_number_administration_client.list_all_releases()
        print('releases_response:')
        async for release in releases_response:
            print(release)
    # [END list_all_releases]


async def get_search_by_id():
    # [START get_search_by_id]
    phone_number_administration_client = PhoneNumberAdministrationClient.from_connection_string(connection_str)
    async with phone_number_administration_client:
        phone_number_search_response = await phone_number_administration_client.get_search_by_id(
            search_id=search_id
        )
        print('phone_number_search_response:')
        print(phone_number_search_response)
    await phone_number_administration_client.close()
    # [END get_search_by_id]


async def create_search():
    # [START create_search]
    phone_number_administration_client = PhoneNumberAdministrationClient.from_connection_string(connection_str)
    searchOptions = CreateSearchOptions(
        area_code=area_code_for_search,
        description="testsearch20200014",
        display_name="testsearch20200014",
        phone_plan_ids=[phone_plan_id],
        quantity=1
    )
    async with phone_number_administration_client:
        search_response = await phone_number_administration_client.create_search(
            body=searchOptions
        )
        print('search_response:')
        print(search_response)
    # [END create_search]


async def cancel_search():
    # [START cancel_search]
    phone_number_administration_client = PhoneNumberAdministrationClient.from_connection_string(connection_str)
    async with phone_number_administration_client:
        await phone_number_administration_client.cancel_search(
            search_id=search_id_to_cancel
        )
    # [END cancel_search]


async def purchase_search():
    # [START purchase_search]
    phone_number_administration_client = PhoneNumberAdministrationClient.from_connection_string(connection_str)
    async with phone_number_administration_client:
        await phone_number_administration_client.purchase_search(
            search_id=search_id_to_purchase
        )
    # [END purchase_search]


async def main():
    await get_release_by_id()
    await list_all_releases()
    await get_search_by_id()
    await create_search()
    await cancel_search()
    # await purchase_search() #currently throws error if purchase an already purchased number

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())

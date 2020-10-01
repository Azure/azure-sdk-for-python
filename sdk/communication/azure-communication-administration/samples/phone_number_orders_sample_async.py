# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: phone_number_orders_sample_async.py
DESCRIPTION:
    These samples demonstrate phone number orders samples.

    ///listing, acquiring and cancelling phone number orders via a connection string, search id, phone plan id and and area code
USAGE:
    python phone_number_orders_sample_async.py
"""
import os
import asyncio
from azure.communication.administration.aio import PhoneNumberAdministrationClient
from azure.communication.administration import CreateSearchOptions

class CommunicationPhoneNumberOrdersSamplesAsync(object):

    def __init__(self):
        self.connection_str = os.getenv('AZURE_COMMUNICATION_SERVICE_CONNECTION_STRING')
        self.release_id = os.getenv('AZURE_COMMUNICATION_SERVICE_TNM_RELEASE_ID', "release-id")
        self.search_id = os.getenv('AZURE_COMMUNICATION_SERVICE_TNM_SEARCH_ID', "search-id")
        self.area_code_for_search = os.getenv('AZURE_COMMUNICATION_SERVICE_TNM_AREA_CODE_FOR_SEARCH', "area-code")
        self.phone_plan_id = os.getenv('AZURE_COMMUNICATION_SERVICE_TNM_PHONE_PLAN_ID', "phone-plan-id")
        self.search_id_to_purchase = os.getenv('AZURE_COMMUNICATION_SERVICE_TNM_SEARCH_ID_TO_PURCHASE', "search-id")
        self.search_id_to_cancel = os.getenv('AZURE_COMMUNICATION_SERVICE_TNM_SEARCH_ID_TO_CANCEL', "search-id")

    async def get_release_by_id(self):
        self._phone_number_administration_client = PhoneNumberAdministrationClient.from_connection_string(
            self.connection_str)
        async with self._phone_number_administration_client:
            phone_number_release_response = await self._phone_number_administration_client.get_release_by_id(
                release_id=self.release_id
            )
            print('phone_number_release_response:')
            print(phone_number_release_response)

    async def list_all_releases(self):
        self._phone_number_administration_client = PhoneNumberAdministrationClient.from_connection_string(
            self.connection_str)
        async with self._phone_number_administration_client:
            releases_response = self._phone_number_administration_client.list_all_releases()
            print('releases_response:')
            async for release in releases_response:
                print(release)

    async def get_search_by_id(self):
        self._phone_number_administration_client = PhoneNumberAdministrationClient.from_connection_string(
            self.connection_str)
        async with self._phone_number_administration_client:
            phone_number_search_response = await self._phone_number_administration_client.get_search_by_id(
                search_id=self.search_id
            )
            print('phone_number_search_response:')
            print(phone_number_search_response)

    async def create_search(self):
        self._phone_number_administration_client = PhoneNumberAdministrationClient.from_connection_string(
            self.connection_str)
        searchOptions = CreateSearchOptions(
            area_code=self.area_code_for_search,
            description="testsearch20200014",
            display_name="testsearch20200014",
            phone_plan_ids=[self.phone_plan_id],
            quantity=1
        )
        async with self._phone_number_administration_client:
            search_response = await self._phone_number_administration_client.create_search(
                body=searchOptions
            )
            print('search_response:')
            print(search_response)

    async def cancel_search(self):
        self._phone_number_administration_client = PhoneNumberAdministrationClient.from_connection_string(
            self.connection_str)
        async with self._phone_number_administration_client:
            await self._phone_number_administration_client.cancel_search(
                search_id=self.search_id_to_cancel
            )

    async def purchase_search(self):
        self._phone_number_administration_client = PhoneNumberAdministrationClient.from_connection_string(
            self.connection_str)
        async with self._phone_number_administration_client:
            await self._phone_number_administration_client.purchase_search(
                search_id=self.search_id_to_purchase
            )


async def main():
    sample = CommunicationPhoneNumberOrdersSamplesAsync()
    await sample.get_release_by_id()
    await sample.list_all_releases()
    await sample.get_search_by_id()
    await sample.create_search()
    await sample.cancel_search()
    await sample.purchase_search() #currently throws error if purchase an already purchased number

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())

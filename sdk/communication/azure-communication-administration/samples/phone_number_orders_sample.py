# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: phone_number_orders_sample.py
DESCRIPTION:
    These samples demonstrate phone number orders samples.

    ///listing, acquiring and cancelling phone number orders via a connection string, search id, phone plan id and and area code
USAGE:
    python phone_number_orders_sample.py
"""
import os
from azure.communication.administration import (
    PhoneNumberAdministrationClient,
    CreateSearchOptions
)

class CommunicationPhoneNumberOrdersSamples(object):

    def __init__(self):
        self.connection_str = os.getenv('AZURE_COMMUNICATION_SERVICE_CONNECTION_STRING')
        self._phone_number_administration_client = PhoneNumberAdministrationClient.from_connection_string(
            self.connection_str)
        self.release_id = os.getenv('AZURE_COMMUNICATION_SERVICE_TNM_RELEASE_ID', "release-id")
        self.search_id = os.getenv('AZURE_COMMUNICATION_SERVICE_TNM_SEARCH_ID', "search-id")
        self.area_code_for_search = os.getenv('AZURE_COMMUNICATION_SERVICE_TNM_AREA_CODE_FOR_SEARCH', "area-code")
        self.phone_plan_id = os.getenv('AZURE_COMMUNICATION_SERVICE_TNM_PHONE_PLAN_ID', "phone-plan-id")
        self.search_id_to_purchase = os.getenv('AZURE_COMMUNICATION_SERVICE_TNM_SEARCH_ID_TO_PURCHASE', "search-id")
        self.search_id_to_cancel = os.getenv('AZURE_COMMUNICATION_SERVICE_TNM_SEARCH_ID_TO_CANCEL', "search-id")

    def get_release_by_id(self):
        phone_number_release_response = self._phone_number_administration_client.get_release_by_id(
            release_id=self.release_id
        )
        print('phone_number_release_response:')
        print(phone_number_release_response)

    def list_all_releases(self):
        releases_response = self._phone_number_administration_client.list_all_releases()
        print('releases_response:')
        for release in releases_response:
            print(release)

    def get_search_by_id(self):
        phone_number_search_response = self._phone_number_administration_client.get_search_by_id(
            search_id=self.search_id
        )
        print('phone_number_search_response:')
        print(phone_number_search_response)

    def create_search(self):
        searchOptions = CreateSearchOptions(
            area_code=self.area_code_for_search,
            description="testsearch20200014",
            display_name="testsearch20200014",
            phone_plan_ids=[self.phone_plan_id],
            quantity=1
        )
        search_response = self._phone_number_administration_client.create_search(
            body=searchOptions
        )
        print('search_response:')
        print(search_response)

    def cancel_search(self):
        self._phone_number_administration_client.cancel_search(
            search_id=self.search_id_to_cancel
        )

    def purchase_search(self):
        self._phone_number_administration_client.purchase_search(
            search_id=self.search_id_to_purchase
        )

if __name__ == '__main__':
    sample = CommunicationPhoneNumberOrdersSamples()
    sample.get_release_by_id()
    sample.list_all_releases()
    sample.get_search_by_id()
    sample.create_search()
    sample.cancel_search()
    # sample.purchase_search() #currently throws error if purchase an already purchased number

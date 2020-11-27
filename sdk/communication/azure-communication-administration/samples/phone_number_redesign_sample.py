# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: phone_number_redesign_sample.py
DESCRIPTION:
    This sample demonstrates how seach, purchase, update, release and list phone numbers
USAGE:
    python phone_number_redesign_sample.py
    Set the environment variables with your own values before running the sample:
    1) AZURE_COMMUNICATION_SERVICE_CONNECTION_STRING - The endpoint of your Azure Communication Service
"""


import os
from azure.communication.administration import (
    PhoneNumberAdministrationClient,
    SearchCapabilities,
    SearchResult,
    Capabilities,
    AcquiredPhoneNumberUpdate
)

connection_str = os.getenv('AZURE_COMMUNICATION_SERVICE_CONNECTION_STRING')
phone_number_administration_client = PhoneNumberAdministrationClient.from_connection_string(connection_str)


def begin_search_phone_numbers():
    # [START begin_reserve_phone_numbers]
    country_code = "US"
    search_capabilities = SearchCapabilities(
        sms="outbound",
        calling="inbound+outbound"
    )

    search_phone_numbers_poller = phone_number_administration_client.begin_search_phone_numbers(
        country_code=country_code,
        number_type="geographic",
        assignment_type="application",
        capabilities=search_capabilities,
        area_code="425",
        quantity=2
    )

    # [END begin_reserve_phone_numbers]
    search_result=search_phone_numbers_poller.result()
    print('SearchId: ', search_result.id)
    print('Monthly Rate: ', search_result.monthly_rate.value)
    for phoneNumber in search_result.phone_numbers:
        print('Available Phone Number: ', phoneNumber)

def begin_purchase_phone_numbers():
    # [START begin_purchase_phone_numbers]
    search_id = "SEARCH_ID"

    purchase_phone_numbers_poller = phone_number_administration_client.begin_purchase_phone_numbers(
        search_id=search_id
    )

    # [END begin_purchase_phone_numbers]
    search_result=purchase_phone_numbers_poller.result()
    print('Purchase completed for the search: ', search_result.id)

def begin_update_phone_number():
    # [START begin_update_phone_number]
    phone_number = "PHONE_NUMBER"

    capabilities = Capabilities(
        sms="inbound+outbound" 
    )

    update_phone_number_poller = phone_number_administration_client.begin_update_phone_number(
        phone_number=phone_number,
        callback_url = "https://contoso.com/webhooks/phone",
        application_id = "1dcb5bde-f5f5-4195-a1c1-43f157688769",
        capabilities = capabilities
    )

    # [END begin_update_phone_number]
    update_result=update_phone_number_poller.result()

    print("Updated Application Id:" + update_result.application_id)
    print("Updated Callback Url:" + update_result.callback_url)
    print("Updated SMS:" + update_result.capabilities.sms)

def begin_release_phone_number():
    # [START begin_release_phone_number]
    phone_number = "PHONE_NUMBER"

    release_phone_number_poller = phone_number_administration_client.begin_release_phone_number(
        phone_number=phone_number
    )

    # [END begin_release_phone_number]
    release_phone_number_poller.result()
    print('Release succeeded for phone number: ', phone_number)

def list_acquired_phone_numbers():
    # [START list_acquired_phone_numbers]
    acquired_phone_numbers = phone_number_administration_client.list_acquired_phone_numbers()

    # [END list_acquired_phone_numbers]
    print('Displaying all acquired phone numbers')
    for acquired_phone_number in acquired_phone_numbers:
      print(acquired_phone_number.phone_number)

if __name__ == '__main__':
    begin_search_phone_numbers()
    begin_purchase_phone_numbers()
    begin_update_phone_number()
    begin_release_phone_number()
    list_acquired_phone_numbers()

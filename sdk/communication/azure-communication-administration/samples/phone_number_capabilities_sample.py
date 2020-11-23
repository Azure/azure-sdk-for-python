# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: phone_number_capabilities_sample.py
DESCRIPTION:
    This sample demonstrates how to get number capabilities via a connection string, capabilities update id and phone number for capabilities.
USAGE:
    python phone_number_capabilities_sample.py
    Set the environment variables with your own values before running the sample:
    1) AZURE_COMMUNICATION_SERVICE_CONNECTION_STRING - The endpoint of your Azure Communication Service
    2) AZURE_COMMUNICATION_SERVICE_PHONENUMBERS_CAPABILITIES_ID - The capabilities id you want to get
    3) AZURE_COMMUNICATION_SERVICE_PHONENUMBERS_PHONENUMBER_FOR_CAPABILITIES - The phone number you want to update capabilities to
"""

import os
from azure.communication.administration import (
    PhoneNumberAdministrationClient,
    NumberUpdateCapabilities
)

connection_str = os.getenv('AZURE_COMMUNICATION_SERVICE_CONNECTION_STRING')
phone_number_administration_client = PhoneNumberAdministrationClient.from_connection_string(connection_str)
capabilities_id = os.getenv('AZURE_COMMUNICATION_SERVICE_PHONENUMBERS_CAPABILITIES_ID', "capabilities-id")
phonenumber_for_capabilities = os.getenv('AZURE_COMMUNICATION_SERVICE_PHONENUMBERS_PHONENUMBER_FOR_CAPABILITIES', "+17771234567")


def list_all_phone_numbers():
    # [START list_all_phone_numbers]
    list_all_phone_numbers_response = phone_number_administration_client.list_all_phone_numbers()
    # [END list_all_phone_numbers]
    print('list_all_phone_numbers_response:')
    for phone_number in list_all_phone_numbers_response:
        print(phone_number)


def get_capabilities_update():
    # [START get_capabilities_update]
    capabilities_response = phone_number_administration_client.get_capabilities_update(
        capabilities_update_id=capabilities_id
    )
    # [END get_capabilities_update]
    print('capabilities_response:')
    print(capabilities_response)


def update_capabilities():
    # [START update_capabilities]
    update = NumberUpdateCapabilities(add=iter(["InboundCalling"]))

    phone_number_capabilities_update = {
        phonenumber_for_capabilities: update
    }

    capabilities_response = phone_number_administration_client.update_capabilities(
        phone_number_capabilities_update=phone_number_capabilities_update
    )
    # [END update_capabilities]
    print('capabilities_response:')
    print(capabilities_response)


if __name__ == '__main__':
    list_all_phone_numbers()
    get_capabilities_update()
    update_capabilities()

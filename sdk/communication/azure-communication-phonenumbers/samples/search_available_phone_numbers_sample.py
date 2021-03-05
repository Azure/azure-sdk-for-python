# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: search_available_phone_numbers_sample.py
DESCRIPTION:
    This sample demonstrates how to search for available numbers you can buy with the respective API.
USAGE:
    python search_available_phone_numbers_sample.py
    Set the environment variables with your own values before running the sample:
    1) AZURE_COMMUNICATION_SERVICE_CONNECTION_STRING - The connection string including your endpoint and 
        access key of your Azure Communication Service
"""

import os
from azure.communication.phonenumbers import (
    PhoneNumbersClient,
    PhoneNumberType,
    PhoneNumberAssignmentType,
    PhoneNumberCapabilities,
    PhoneNumberCapabilityType
)

connection_str = os.getenv('AZURE_COMMUNICATION_SERVICE_CONNECTION_STRING')
area_code = os.getenv('AZURE_COMMUNICATION_SERVICE_AREA_CODE')
phone_numbers_client = PhoneNumbersClient.from_connection_string(connection_str)

def search_available_phone_numbers():
    capabilities = PhoneNumberCapabilities(
        calling = PhoneNumberCapabilityType.INBOUND,
        sms = PhoneNumberCapabilityType.INBOUND_OUTBOUND
    )
    poller = phone_numbers_client.begin_search_available_phone_numbers(
        "US",
        PhoneNumberType.TOLL_FREE,
        PhoneNumberAssignmentType.APPLICATION,
        capabilities,
        polling = True
    )
    print('Acquired phone numbers: ' + poller.result())


if __name__ == '__main__':
    search_available_phone_numbers()

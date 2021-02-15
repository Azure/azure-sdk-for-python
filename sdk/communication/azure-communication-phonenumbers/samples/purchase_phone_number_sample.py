# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: phone_number_area_codes_sample.py
DESCRIPTION:
    This sample demonstrates how to get all area codes via a connection string, country code and phone plan id.
USAGE:
    python list_acquired_phone_numbers_sample.py
    Set the environment variables with your own values before running the sample:
    1) AZURE_COMMUNICATION_SERVICE_CONNECTION_STRING - The endpoint of your Azure Communication Service
    2) AZURE_COMMUNICATION_SERVICE_SEARCH_ID_TO_PURCHASE - The search id for the phone number you reserved and want to purchase
"""

import os
from azure.communication.phonenumbers import (
    PhoneNumbersClient
)

connection_str = os.getenv('AZURE_COMMUNICATION_SERVICE_CONNECTION_STRING')
phone_number = os.getenv("AZURE_COMMUNICATION_SERVICE_PHONE_NUMBER_INFORMATION")
phone_numbers_client = PhoneNumbersClient.from_connection_string(connection_str)

def get_phone_number_information():
    phone_number_information = phone_numbers_client.get_phone_number(phone_number)
    print('Phone number information:')
    print(phone_number_information)


if __name__ == '__main__':
    get_phone_number_information()
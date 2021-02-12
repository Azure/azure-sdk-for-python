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
"""

import os
from azure.communication.phonenumbers import (
    PhoneNumbersClient
)

connection_str = os.getenv('AZURE_COMMUNICATION_SERVICE_CONNECTION_STRING')
phone_numbers_client = PhoneNumbersClient.from_connection_string(connection_str)

def list_acquired_phone_numbers():
    acquired_phone_numbers = phone_numbers_client.list_acquired_phone_numbers()
    print('Acquired phone numbers:')
    print(acquired_phone_numbers)


if __name__ == '__main__':
    list_acquired_phone_numbers()
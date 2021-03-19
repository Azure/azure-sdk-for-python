# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: list_purchased_phone_numbers_sample.py
DESCRIPTION:
    This sample demonstrates how to get all of you acquired phone numbers using your connection string
USAGE:
    python list_purchased_phone_numbers_sample.py
    Set the environment variables with your own values before running the sample:
    1) AZURE_COMMUNICATION_SERVICE_CONNECTION_STRING - The connection string including your endpoint and 
        access key of your Azure Communication Service"""

import os
from azure.communication.phonenumbers import (
    PhoneNumbersClient
)

connection_str = os.getenv('AZURE_COMMUNICATION_SERVICE_CONNECTION_STRING')
phone_numbers_client = PhoneNumbersClient.from_connection_string(connection_str)

def list_purchased_phone_numbers():
    purchased_phone_numbers = phone_numbers_client.list_purchased_phone_numbers()
    print('Purchased phone numbers:')
    for acquired_phone_number in purchased_phone_numbers:
        print(acquired_phone_number.phone_number)


if __name__ == '__main__':
    list_purchased_phone_numbers()

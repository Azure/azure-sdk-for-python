# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: release_phone_number_sample.py
DESCRIPTION:
    This sample demonstrates how to release a previously acquired phone number using your connection string.
USAGE:
    python release_phone_number_sample.py
    Set the environment variables with your own values before running the sample:
    1) AZURE_COMMUNICATION_SERVICE_CONNECTION_STRING - The connection string including your endpoint and 
        access key of your Azure Communication Service
    2) AZURE_COMMUNICATION_SERVICE_PHONE_NUMBER_TO_RELEASE - The phone number you want to release
"""

import os
from azure.communication.phonenumbers import (
    PhoneNumbersClient
)

connection_str = os.getenv('AZURE_COMMUNICATION_SERVICE_CONNECTION_STRING')
phone_number_to_release = os.getenv(
    "AZURE_COMMUNICATION_SERVICE_PHONE_NUMBER_TO_RELEASE" # e.g. "+18001234567"
) 
phone_numbers_client = PhoneNumbersClient.from_connection_string(connection_str)

def release_phone_number():
    poller = phone_numbers_client.begin_release_phone_number(phone_number_to_release)
    poller.result()
    print('Status of the operation: ' + poller.status())

if __name__ == '__main__':
    release_phone_number()

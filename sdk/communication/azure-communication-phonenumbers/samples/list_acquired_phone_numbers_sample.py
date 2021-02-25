# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
<<<<<<< HEAD
<<<<<<< HEAD
FILE: list_acquired_phone_numbers_sample.py
DESCRIPTION:
    This sample demonstrates how to get all off you acquired phone numbers using your connection string
=======
FILE: phone_number_area_codes_sample.py
DESCRIPTION:
    This sample demonstrates how to get all area codes via a connection string, country code and phone plan id.
>>>>>>> 798b57943... Regenerated code
=======
FILE: list_acquired_phone_numbers_sample.py
DESCRIPTION:
    This sample demonstrates how to get all off you acquired phone numbers using your connection string
>>>>>>> cb958a482... Added fixed samples
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
<<<<<<< HEAD
<<<<<<< HEAD
    for acquired_phone_number in acquired_phone_numbers:
        print(acquired_phone_number.phone_number)
=======
    print(acquired_phone_numbers)
>>>>>>> 798b57943... Regenerated code
=======
    for acquired_phone_number in acquired_phone_numbers:
<<<<<<< HEAD
        print(acquired_phone_number)
>>>>>>> a11fa64fb... Corrected samples
=======
        print(acquired_phone_number.phone_number)
>>>>>>> f5c946df0... Regenerated code and addressed comments


if __name__ == '__main__':
    list_acquired_phone_numbers()
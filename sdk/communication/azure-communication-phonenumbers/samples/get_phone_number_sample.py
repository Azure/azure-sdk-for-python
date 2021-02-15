# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
<<<<<<< HEAD
FILE:get_phone_number_sample.py
DESCRIPTION:
    This sample demonstrates how to get the information from an acquired phone number using your connection string
USAGE:
    python get_phone_number_sample.py
=======
FILE: phone_number_area_codes_sample.py
DESCRIPTION:
    This sample demonstrates how to get all area codes via a connection string, country code and phone plan id.
USAGE:
    python list_acquired_phone_numbers_sample.py
>>>>>>> 798b57943... Regenerated code
    Set the environment variables with your own values before running the sample:
    1) AZURE_COMMUNICATION_SERVICE_CONNECTION_STRING - The endpoint of your Azure Communication Service
    2) AZURE_COMMUNICATION_SERVICE_PHONE_NUMBER_INFORMATION - The phone number you want to get its information
"""

import os
from azure.communication.phonenumbers import (
    PhoneNumbersClient
)

connection_str = os.getenv('AZURE_COMMUNICATION_SERVICE_CONNECTION_STRING')
<<<<<<< HEAD
<<<<<<< HEAD
phone_number = os.getenv("AZURE_COMMUNICATION_SERVICE_PHONE_NUMBER") # e.g. "+18001234567"
=======
phone_number = os.getenv("AZURE_COMMUNICATION_SERVICE_PHONE_NUMBER")
>>>>>>> 798b57943... Regenerated code
=======
phone_number = os.getenv("AZURE_COMMUNICATION_SERVICE_PHONE_NUMBER_INFORMATION")
>>>>>>> 968de8d7e... Added README and samples
phone_numbers_client = PhoneNumbersClient.from_connection_string(connection_str)

def get_phone_number_information():
    phone_number_information = phone_numbers_client.get_phone_number(phone_number)
<<<<<<< HEAD
    print('Phone number information: ' + phone_number_information)
=======
    print('Phone number information:')
    print(phone_number_information)

>>>>>>> 798b57943... Regenerated code

if __name__ == '__main__':
    get_phone_number_information()
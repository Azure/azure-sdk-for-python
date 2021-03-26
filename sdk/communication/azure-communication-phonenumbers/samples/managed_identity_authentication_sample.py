# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: managed_identity_authentication_sample.py
DESCRIPTION:
    This sample demonstrates how to authenticate the PhoneNumbersClient using managed identity
USAGE:
    python managed_identity_authentication_sample.py
    Set the environment variables with your own values before running the sample:
    1) AZURE_COMMUNICATION_SERVICE_ENDPOINT - The endpoint of your Azure Communication Service
    2) AZURE_CLIENT_ID - The id of your registered Azure Active Directory application
    3) AZURE_CLIENT_SECRET - A client secret created for your registered AAD aplication
    4) AZURE_TENANT_ID - The tenant in which this application can be found
"""

import os
from azure.communication.phonenumbers import PhoneNumbersClient
from azure.identity import DefaultAzureCredential

endpoint = os.getenv('AZURE_COMMUNICATION_SERVICE_ENDPOINT')
phone_numbers_client = PhoneNumbersClient(endpoint, DefaultAzureCredential())

def list_purchased_phone_numbers_using_managed_identity():
    purchased_phone_numbers = phone_numbers_client.list_purchased_phone_numbers()
    print('Purchased phone numbers:')
    for acquired_phone_number in purchased_phone_numbers:
        print(acquired_phone_number.phone_number)


if __name__ == '__main__':
    list_purchased_phone_numbers_using_managed_identity()

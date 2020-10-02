# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: phone_number_supported_countries_sample.py
DESCRIPTION:
    This sample demonstrates how to get supported countries via a connection string
USAGE:
    python phone_number_supported_countries_sample.py
    Set the environment variables with your own values before running the sample:
    1) AZURE_COMMUNICATION_SERVICE_CONNECTION_STRING - The endpoint of your Azure Communication Service
"""


import os
from azure.communication.administration import (
    PhoneNumberAdministrationClient
)

connection_str = os.getenv('AZURE_COMMUNICATION_SERVICE_CONNECTION_STRING')
phone_number_administration_client = PhoneNumberAdministrationClient.from_connection_string(connection_str)


def list_all_supported_countries():
    # [START list_all_supported_countries]
    supported_countries = phone_number_administration_client.list_all_supported_countries()
    # [END list_all_supported_countries]
    print('supported_countries:')
    for supported_country in supported_countries:
        print(supported_country)


if __name__ == '__main__':
    list_all_supported_countries()

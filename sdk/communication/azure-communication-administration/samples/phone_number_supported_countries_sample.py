# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: phone_number_supported_countries_sample.py
DESCRIPTION:
    These samples demonstrate supported countries samples.

    ///getting supported countries via a connection string
USAGE:
    python phone_number_supported_countries_sample.py
"""
import os
from azure.communication.administration import (
    PhoneNumberAdministrationClient
)

class CommunicationSupportedCountriesSamples(object):

    def __init__(self):
        self.connection_str = os.getenv('AZURE_COMMUNICATION_SERVICE_CONNECTION_STRING')
        self._phone_number_administration_client = PhoneNumberAdministrationClient.from_connection_string(
            self.connection_str)

    def list_all_supported_countries(self):
        supported_countries = self._phone_number_administration_client.list_all_supported_countries()
        print('supported_countries:')
        for supported_country in supported_countries:
            print(supported_country)

if __name__ == '__main__':
    sample = CommunicationSupportedCountriesSamples()
    sample.list_all_supported_countries()

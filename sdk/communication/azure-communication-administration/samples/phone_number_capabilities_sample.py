# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: phone_number_capabilities_sample.py
DESCRIPTION:
    These samples demonstrate number capabilities samples.

    ///getting number capabilities via a connection string, capabilities update id and phone number for capabilities
USAGE:
    python phone_number_capabilities_sample.py
"""
import os
from azure.communication.administration import (
    PhoneNumberAdministrationClient,
    NumberUpdateCapabilities
)

class CommunicationNumberCapabilitiesSamples(object):

    def __init__(self):
        self.connection_str = os.getenv('AZURE_COMMUNICATION_SERVICE_CONNECTION_STRING')
        self._phone_number_administration_client = PhoneNumberAdministrationClient.from_connection_string(
            self.connection_str)
        self.capabilities_id = os.getenv('AZURE_COMMUNICATION_SERVICE_TNM_CAPABILITIES_ID', "capabilities-id")
        self.phonenumber_for_capabilities = os.getenv('AZURE_COMMUNICATION_SERVICE_TNM_PHONENUMBER_FOR_CAPABILITIES', "+17771234567")

    def list_all_phone_numbers(self):
        list_all_phone_numbers_response = self._phone_number_administration_client.list_all_phone_numbers()
        print('list_all_phone_numbers_response:')
        for phone_number in list_all_phone_numbers_response:
            print(phone_number)

    def get_capabilities_update(self):
        capabilities_response = self._phone_number_administration_client.get_capabilities_update(
            capabilities_update_id=self.capabilities_id
        )
        print('capabilities_response:')
        print(capabilities_response)

    def update_capabilities(self):
        update = NumberUpdateCapabilities(add=iter(["InboundCalling"]))

        phone_number_capabilities_update = {
            self.phonenumber_for_capabilities: update
        }

        capabilities_response = self._phone_number_administration_client.update_capabilities(
            phone_number_capabilities_update=phone_number_capabilities_update
        )
        print('capabilities_response:')
        print(capabilities_response)

if __name__ == '__main__':
    sample = CommunicationNumberCapabilitiesSamples()
    sample.list_all_phone_numbers()
    sample.get_capabilities_update()
    sample.update_capabilities()

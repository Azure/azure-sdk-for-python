# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: phone_number_configuration_sample_async.py
DESCRIPTION:
    These samples demonstrate phone number configuration samples.

    ///listing phone plans via a connection string and phone number to configure
USAGE:
    python phone_number_configuration_sample_async.py
"""
import os
import asyncio
from azure.communication.administration.aio import PhoneNumberAdministrationClient
from azure.communication.administration import PstnConfiguration

class CommunicationPhoneNumberConfigurationSamplesAsync(object):

    def __init__(self):
        self.connection_str = os.getenv('AZURE_COMMUNICATION_SERVICE_CONNECTION_STRING')
        self.phonenumber_to_configure = os.getenv('AZURE_COMMUNICATION_SERVICE_TNM_PHONENUMBER_TO_CONFIGURE',
                                                  "phonenumber_to_configure")

    async def get_number_configuration(self):
        self._phone_number_administration_client = PhoneNumberAdministrationClient.from_connection_string(
            self.connection_str)
        async with self._phone_number_administration_client:
            phone_number_configuration_response = await self._phone_number_administration_client.get_number_configuration(
                phone_number=self.phonenumber_to_configure
            )
            print('phone_number_configuration_response:')
            print(phone_number_configuration_response)

    async def configure_number(self):
        self._phone_number_administration_client = PhoneNumberAdministrationClient.from_connection_string(
            self.connection_str)
        pstn_config = PstnConfiguration(
            callback_url="https://callbackurl",
            application_id="ApplicationId",
            azure_pstn_target_id="AzurePstnTargetId"
        )
        async with self._phone_number_administration_client:
            await self._phone_number_administration_client.configure_number(
                pstn_configuration=pstn_config,
                phone_number=self.phonenumber_to_configure
            )


async def main():
    sample = CommunicationPhoneNumberConfigurationSamplesAsync()
    await sample.get_number_configuration()
    await sample.configure_number()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())

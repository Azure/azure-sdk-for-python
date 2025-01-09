# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sms_token_credential_auth_sample_async.py
DESCRIPTION:
    This sample demonstrates creating an SMS client using a token credential and then sending
    a message.
USAGE:
    python sms_token_credential_auth_sample_async.py
    Set the environment variable with your own value before running the sample:
    1) COMMUNICATION_SAMPLES_CONNECTION_STRING - the connection string in your ACS resource
    2) AZURE_PHONE_NUMBER - a phone number with SMS capabilities in your ACS resource
"""

import os
import sys
import asyncio
from azure.communication.sms.aio import SmsClient
from azure.communication.sms._shared.utils import parse_connection_str
from azure.identity.aio import DefaultAzureCredential

sys.path.append("..")


class SmsTokenCredentialAuthSampleAsync(object):

    connection_string = os.getenv("COMMUNICATION_LIVETEST_STATIC_CONNECTION_STRING")
    phone_number = os.getenv("SMS_PHONE_NUMBER")
    client_id = os.getenv("AZURE_CLIENT_ID")
    client_secret = os.getenv("AZURE_CLIENT_SECRET")
    tenant_id = os.getenv("AZURE_TENANT_ID")

    async def sms_token_credential_auth_async(self):
        if not self.connection_string or not self.phone_number:
            raise ValueError(
                '''Environment variables COMMUNICATION_LIVETEST_STATIC_CONNECTION_STRING and SMS_PHONE_NUMBER must be 
                set''')
        # To use Azure Active Directory Authentication (DefaultAzureCredential) make sure to have
        # AZURE_TENANT_ID, AZURE_CLIENT_ID and AZURE_CLIENT_SECRET as env variables.
        if self.client_id is not None and self.client_secret is not None and self.tenant_id is not None:
            endpoint, _ = parse_connection_str(self.connection_string)
            sms_client = SmsClient(endpoint, DefaultAzureCredential())
        else:
            sms_client = SmsClient.from_connection_string(self.connection_string)

        async with sms_client:
            # calling send() with sms values
            sms_responses = await sms_client.send(
                from_=self.phone_number, to=self.phone_number, message="Hello World via SMS"
            )
            sms_response = sms_responses[0]

            if sms_response.successful:
                print(
                    "Message with message id {} was successful sent to {}".format(
                        sms_response.message_id, sms_response.to
                    )
                )
            else:
                print(
                    "Message failed to send to {} with the status code {} and error: {}".format(
                        sms_response.to, sms_response.http_status_code, sms_response.error_message
                    )
                )


if __name__ == "__main__":
    sample = SmsTokenCredentialAuthSampleAsync()
    asyncio.run(sample.sms_token_credential_auth_async())

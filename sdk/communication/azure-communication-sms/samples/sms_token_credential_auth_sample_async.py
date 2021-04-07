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
    1) AZURE_COMMUNICATION_SERVICE_ENDPOINT - the endpoint in your ACS account
"""

import os
import sys
import asyncio
from azure.communication.sms.aio import SmsClient
from azure.identity import DefaultAzureCredential

sys.path.append("..")

class SmsTokenCredentialAuthSampleAsync(object):

    endpoint = os.getenv('AZURE_COMMUNICATION_SERVICE_ENDPOINT')
    
    async def sms_token_credential_auth_async(self):
        # To use Azure Active Directory Authentication (DefaultAzureCredential) make sure to have
        # AZURE_TENANT_ID, AZURE_CLIENT_ID and AZURE_CLIENT_SECRET as env variables.
        sms_client = SmsClient(self.endpoint, DefaultAzureCredential())

        async with sms_client:
            try:
                # calling send() with sms values
                sms_responses = await sms_client.send(
                    from_="<leased-phone-number>",
                    to=["<to-phone-number>"],
                    message="Hello World via SMS")
                sms_response = sms_responses[0]
                
                if (sms_response.successful):
                    print("Message with message id {} was successful sent to {}"
                    .format(sms_response.message_id, sms_response.to))
                else:
                    print("Message failed to send to {} with the status code {} and error: {}"
                    .format(sms_response.to, sms_response.http_status_code, sms_response.error_message))
            except Exception:
                print(Exception)
                pass

if __name__ == '__main__':
    sample = SmsTokenCredentialAuthSampleAsync()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(sample.sms_token_credential_auth_async())

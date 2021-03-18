# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: send_sms_to_multiple_recipients_sample_async.py
DESCRIPTION:
    This sample demonstrates sending an SMS message to multiple recipients. The SMS client is 
    authenticated using a connection string.
USAGE:
    python send_sms_to_multiple_recipients_sample_async.py
    Set the environment variable with your own value before running the sample:
    1) AZURE_COMMUNICATION_SERVICE_CONNECTION_STRING - the connection string in your ACS account
"""

import os
import sys
import asyncio
from azure.communication.sms.aio import SmsClient

sys.path.append("..")

class SmsMultipleRecipientsSampleAsync(object):

    connection_string = os.getenv("AZURE_COMMUNICATION_SERVICE_CONNECTION_STRING")
        
    async def send_sms_to_multiple_recipients_async(self):
        sms_client = SmsClient.from_connection_string(self.connection_string)

        async with sms_client:
            try:
                # calling send() with sms values 
                sms_responses = await sms_client.send(
                    from_="<leased-phone-number>",
                    to=["<to-phone-number-1>", "<to-phone-number-2>", "<to-phone-number-3>"],
                    message="Hello World via SMS",
                    enable_delivery_report=True, # optional property
                    tag="custom-tag") # optional property
        
                for sms_response in sms_responses:
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
    sample = SmsMultipleRecipientsSampleAsync()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(sample.send_sms_to_multiple_recipients_async())

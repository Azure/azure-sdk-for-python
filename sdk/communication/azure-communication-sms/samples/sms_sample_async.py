# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sms_sample_async.py
DESCRIPTION:
    These samples demonstrate sending mutiple sms messages and resending 
    any failed messages.
    
    ///authenticating a client via a connection string
USAGE:
    python sms_sample_async.py
"""

import sys
import asyncio
from azure.communication.sms.aio import SmsClient

sys.path.append("..")

class SmsSamples(object):

    async def send_sms_async(self):
        connection_string = "COMMUNICATION_SERVICES_CONNECTION_STRING"
        sms_client = SmsClient.from_connection_string(connection_string)

        async with sms_client:
            try:
                # calling send() with sms values 
                sms_responses = await sms_client.send(
                    from_="<leased-phone-number>",
                    to=["<to-phone-number-1>", "<to-phone-number-2>", "<to-phone-number-3>"],
                    message="Hello World via SMS",
                    enable_delivery_report=True, # optional property
                    tag="custom-tag") # optional property
            except Exception:
                print(Exception)
                pass

            failed_recipients = []
            for sms_response in sms_responses:
                if (sms_response.successful):
                    print("Message with message id {} was successful sent to {}"
                    .format(sms_response.message_id, sms_response.to))
                else:
                    print("Message failed to send to {} with the status code {} and error: {}"
                    .format(sms_response.to, sms_response.http_status_code, sms_response.error_message))
                    if (sms_response.http_status_code != 400):
                        failed_recipients.append(sms_response.to)
            
            try:
                # calling send() with failed recipients
                sms_responses = await sms_client.send(
                    from_="<leased-phone-number>",
                    to=failed_recipients,
                    message="Hello World via SMS",
                    enable_delivery_report=True, # optional property
                    tag="custom-tag") # optional property
            except Exception:
                print(Exception)
                pass

if __name__ == '__main__':
    sample = SmsSamples()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(sample.send_sms_async())

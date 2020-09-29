# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import sys
import asyncio
from azure.communication.sms import (
    SendSmsOptions, PhoneNumber
)
from azure.communication.sms.aio import SmsClient
sys.path.append("..")

"""
FILE: sms_sample_async.py
DESCRIPTION:
    These samples demonstrate sending an sms asynchronously.
    
    ///authenticating a client via a connection string
USAGE:
    python sms_sample_async.py
"""

class SmsSamples(object):

    async def send_sms_async(self):
        connection_string = "COMMUNICATION_SERVICES_CONNECTION_STRING"
        sms_client = SmsClient.from_connection_string(connection_string)

        async with sms_client:
            try:
                # calling send() with constructed request object
                smsresponse = await sms_client.send(
                    from_phone_number=PhoneNumber("<leased-phone-number>"),
                    to_phone_numbers=[PhoneNumber("<to-phone-number>")],
                    message="Hello World via SMS",
                    send_sms_options=SendSmsOptions(enable_delivery_report=True)) # optional property
            except Exception:
                print(Exception)
                pass

            print(smsresponse)

if __name__ == '__main__':
    sample = SmsSamples()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(sample.send_sms_async())

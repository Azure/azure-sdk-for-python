# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sms_sample.py
DESCRIPTION:
    These samples demonstrate sending an sms.
    
    ///authenticating a client via a connection string
USAGE:
    python sms_sample.py
"""

import sys
from azure.communication.sms import (
    SendSmsOptions, PhoneNumber, SmsClient
)

sys.path.append("..")

class SmsSamples(object):

    def send_sms(self):
        connection_string = "COMMUNICATION_SERVICES_CONNECTION_STRING"

        sms_client = SmsClient.from_connection_string(connection_string)

        # calling send() with sms values
        smsresponse = sms_client.send(
            from_phone_number=PhoneNumber("<leased-phone-number>"),
            to_phone_numbers=[PhoneNumber("<to-phone-number>")],
            message="Hello World via SMS",
            send_sms_options=SendSmsOptions(enable_delivery_report=True)) # optional property

        print(smsresponse)

if __name__ == '__main__':
    sample = SmsSamples()
    sample.send_sms()

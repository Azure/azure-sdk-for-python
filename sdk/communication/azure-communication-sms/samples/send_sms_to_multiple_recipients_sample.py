# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: send_sms_to_multiple_recipients_sample.py
DESCRIPTION:
    This sample demonstrates sending an SMS message to multiple recipients. The SMS client is 
    authenticated using a connection string.
USAGE:
    python send_sms_to_multiple_recipients_sample.py
    Set the environment variable with your own value before running the sample:
    1) COMMUNICATION_SAMPLES_CONNECTION_STRING - the connection string in your ACS resource
    2) AZURE_PHONE_NUMBER - a phone number with SMS capabilities in your ACS resource
"""

import os
import sys
from azure.communication.sms import SmsClient

sys.path.append("..")

class SmsMultipleRecipientsSample(object):

    connection_string = os.getenv("COMMUNICATION_SAMPLES_CONNECTION_STRING")
    phone_number = os.getenv("AZURE_PHONE_NUMBER")
        
    def send_sms_to_multiple_recipients(self):
        sms_client = SmsClient.from_connection_string(self.connection_string)

        # calling send() with sms values
        sms_responses = sms_client.send(
            from_=self.phone_number,
            to=[self.phone_number, self.phone_number],
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

if __name__ == '__main__':
    sample = SmsMultipleRecipientsSample()
    sample.send_sms_to_multiple_recipients()

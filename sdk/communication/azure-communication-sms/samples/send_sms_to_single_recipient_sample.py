# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: send_sms_to_single_recipient_sample.py
DESCRIPTION:
    This sample demonstrates sending an SMS message to a single recipient. The SMS client is 
    authenticated using a connection string.
USAGE:
    python send_sms_to_single_recipient_sample.py
    Set the environment variable with your own value before running the sample:
    1) AZURE_COMMUNICATION_SERVICE_CONNECTION_STRING - the connection string in your ACS account
"""

import os
import sys
from azure.communication.sms import SmsClient

sys.path.append("..")

class SmsSingleRecipientSample(object):

    connection_string = os.getenv("AZURE_COMMUNICATION_SERVICE_CONNECTION_STRING")
    
    def send_sms_to_single_recipient(self):
        sms_client = SmsClient.from_connection_string(self.connection_string)

        # calling send() with sms values
        sms_responses = sms_client.send(
            from_="<leased-phone-number>",
            to="<to-phone-number>",
            message="Hello World via SMS",
            enable_delivery_report=True, # optional property
            tag="custom-tag") # optional property
        sms_response = sms_responses[0]
        
        if (sms_response.successful):
            print("Message with message id {} was successful sent to {}"
            .format(sms_response.message_id, sms_response.to))
        else:
            print("Message failed to send to {} with the status code {} and error: {}"
            .format(sms_response.to, sms_response.http_status_code, sms_response.error_message))

if __name__ == '__main__':
    sample = SmsSingleRecipientSample()
    sample.send_sms_to_single_recipient()

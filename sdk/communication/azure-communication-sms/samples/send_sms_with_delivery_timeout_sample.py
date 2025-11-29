#!/usr/bin/env python

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: send_sms_with_delivery_timeout_sample.py

DESCRIPTION:
    This sample demonstrates how to send an SMS message with a custom delivery report timeout.
    The delivery report timeout specifies how long to wait for a delivery report before 
    considering it expired.

USAGE:
    python send_sms_with_delivery_timeout_sample.py

    Set the environment variables with your own values before running the sample:
    1) COMMUNICATION_SERVICES_CONNECTION_STRING - the connection string in your Communication Services resource
    2) SENDER_PHONE_NUMBER - a phone number associated with your Communication Services resource
    3) RECIPIENT_PHONE_NUMBER - the phone number you want to send SMS to
"""

import os
from azure.communication.sms import SmsClient

def main():
    # Get configuration from environment variables
    connection_string = os.environ["COMMUNICATION_SERVICES_CONNECTION_STRING"]
    sender_phone_number = os.environ["SENDER_PHONE_NUMBER"]
    recipient_phone_number = os.environ["RECIPIENT_PHONE_NUMBER"]

    # Create SmsClient from connection string
    sms_client = SmsClient.from_connection_string(connection_string)

    # [START send_sms_with_delivery_timeout]
    try:
        # Send SMS with custom delivery report timeout
        # Setting timeout to 60 seconds (minimum allowed value)
        sms_responses = sms_client.send(
            from_=sender_phone_number,
            to=recipient_phone_number,
            message="Hello! This SMS has a 60-second delivery report timeout.",
            enable_delivery_report=True,
            delivery_report_timeout_in_seconds=60,  # Wait 60 seconds for delivery report
            tag="delivery-timeout-sample"
        )

        for sms_response in sms_responses:
            if sms_response.successful:
                print(f"✅ SMS sent successfully!")
                print(f"   Message ID: {sms_response.message_id}")
                print(f"   To: {sms_response.to}")
                print(f"   HTTP Status: {sms_response.http_status_code}")
                print(f"   Delivery report timeout: 60 seconds")
                print(f"   Note: If delivery report is not received within 60 seconds,")
                print(f"         a timeout error will be generated in the delivery report.")
            else:
                print(f"❌ Failed to send SMS to {sms_response.to}")
                print(f"   Error: {sms_response.error_message}")
                print(f"   HTTP Status: {sms_response.http_status_code}")
                
    except Exception as e:
        print(f"❌ Error sending SMS: {e}")
    # [END send_sms_with_delivery_timeout]

    print("\nℹ️  Delivery Report Timeout Information:")
    print("   - Minimum timeout: 60 seconds")
    print("   - Maximum timeout: 43200 seconds (12 hours)")
    print("   - If not specified, default system timeout is used")
    print("   - Timeout controls when to generate a timeout error if no delivery report is received")

if __name__ == "__main__":
    main()

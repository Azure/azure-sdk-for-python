#!/usr/bin/env python

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: send_sms_with_messaging_connect_sample.py

DESCRIPTION:
    This sample demonstrates how to send an SMS message using the Messaging Connect feature.
    Messaging Connect allows you to use partner networks for SMS delivery by providing
    an API key and partner name.

USAGE:
    python send_sms_with_messaging_connect_sample.py

    Set the environment variables with your own values before running the sample:
    1) COMMUNICATION_SERVICES_CONNECTION_STRING - the connection string in your Communication Services resource
    2) SENDER_PHONE_NUMBER - a phone number associated with your Communication Services resource
    3) RECIPIENT_PHONE_NUMBER - the phone number you want to send SMS to
    4) MESSAGING_CONNECT_API_KEY - your API key for the Messaging Connect partner
    5) MESSAGING_CONNECT_PARTNER_NAME - the name of your Messaging Connect partner
"""

import os
from azure.communication.sms import SmsClient

def main():
    # Get configuration from environment variables
    connection_string = os.environ["COMMUNICATION_SERVICES_CONNECTION_STRING"]
    sender_phone_number = os.environ["SENDER_PHONE_NUMBER"]
    recipient_phone_number = os.environ["RECIPIENT_PHONE_NUMBER"]
    messaging_connect_api_key = os.environ["MESSAGING_CONNECT_API_KEY"]
    messaging_connect_partner_name = os.environ["MESSAGING_CONNECT_PARTNER_NAME"]

    # Create SmsClient from connection string
    sms_client = SmsClient.from_connection_string(connection_string)

    # [START send_sms_with_messaging_connect]
    try:
        # Send SMS using Messaging Connect partner
        sms_responses = sms_client.send(
            from_=sender_phone_number,
            to=recipient_phone_number,
            message="Hello! This SMS is sent via Messaging Connect partner network.",
            enable_delivery_report=True,
            messaging_connect_api_key=messaging_connect_api_key,
            messaging_connect_partner_name=messaging_connect_partner_name,
            tag="messaging-connect-sample"
        )

        for sms_response in sms_responses:
            if sms_response.successful:
                print(f"✅ SMS sent successfully via Messaging Connect!")
                print(f"   Message ID: {sms_response.message_id}")
                print(f"   To: {sms_response.to}")
                print(f"   HTTP Status: {sms_response.http_status_code}")
                print(f"   Partner: {messaging_connect_partner_name}")
                print(f"   API Key: {messaging_connect_api_key[:8]}...")  # Show only first 8 chars for security
            else:
                print(f"❌ Failed to send SMS to {sms_response.to}")
                print(f"   Error: {sms_response.error_message}")
                print(f"   HTTP Status: {sms_response.http_status_code}")
                
    except Exception as e:
        print(f"❌ Error sending SMS: {e}")
    # [END send_sms_with_messaging_connect]

    print("\nℹ️  Messaging Connect Information:")
    print("   - Both API key and partner name must be provided together")
    print("   - The API key is associated with your account in the partner portal")
    print("   - Partner name specifies which Messaging Connect partner to use")
    print("   - This feature enables SMS delivery through partner networks")

if __name__ == "__main__":
    main()

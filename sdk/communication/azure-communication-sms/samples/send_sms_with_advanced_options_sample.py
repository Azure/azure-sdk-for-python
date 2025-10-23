#!/usr/bin/env python

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: send_sms_with_advanced_options_sample.py

DESCRIPTION:
    This sample demonstrates how to send an SMS message using all the advanced options:
    delivery report timeout and Messaging Connect features combined.

USAGE:
    python send_sms_with_advanced_options_sample.py

    Set the environment variables with your own values before running the sample:
    1) COMMUNICATION_SERVICES_CONNECTION_STRING - the connection string in your Communication Services resource
    2) SENDER_PHONE_NUMBER - a phone number associated with your Communication Services resource
    3) RECIPIENT_PHONE_NUMBER - the phone number you want to send SMS to
    4) MESSAGING_CONNECT_API_KEY - your API key for the Messaging Connect partner (optional)
    5) MESSAGING_CONNECT_PARTNER_NAME - the name of your Messaging Connect partner (optional)
"""

import os
from azure.communication.sms import SmsClient

def main():
    # Get configuration from environment variables
    connection_string = os.environ["COMMUNICATION_SERVICES_CONNECTION_STRING"]
    sender_phone_number = os.environ["SENDER_PHONE_NUMBER"]
    recipient_phone_number = os.environ["RECIPIENT_PHONE_NUMBER"]
    
    # Optional Messaging Connect parameters
    messaging_connect_api_key = os.environ.get("MESSAGING_CONNECT_API_KEY")
    messaging_connect_partner_name = os.environ.get("MESSAGING_CONNECT_PARTNER_NAME")

    # Create SmsClient from connection string
    sms_client = SmsClient.from_connection_string(connection_string)

    # [START send_sms_with_advanced_options]
    try:
        # Prepare SMS options
        sms_options = {
            "from_": sender_phone_number,
            "to": recipient_phone_number,
            "message": "Hello! This SMS uses advanced delivery and partner options.",
            "enable_delivery_report": True,
            "delivery_report_timeout_in_seconds": 300,  # 5-minute timeout
            "tag": "advanced-options-sample"
        }

        # Add Messaging Connect options if available
        if messaging_connect_api_key and messaging_connect_partner_name:
            sms_options["messaging_connect_api_key"] = messaging_connect_api_key
            sms_options["messaging_connect_partner_name"] = messaging_connect_partner_name
            print("📡 Sending SMS with Messaging Connect partner network")
        else:
            print("📱 Sending SMS with standard delivery")

        # Send SMS with all available options
        sms_responses = sms_client.send(**sms_options)

        for sms_response in sms_responses:
            if sms_response.successful:
                print(f"✅ SMS sent successfully with advanced options!")
                print(f"   Message ID: {sms_response.message_id}")
                print(f"   To: {sms_response.to}")
                print(f"   HTTP Status: {sms_response.http_status_code}")
                print(f"   Delivery timeout: 300 seconds (5 minutes)")
                
                if messaging_connect_api_key and messaging_connect_partner_name:
                    print(f"   Partner: {messaging_connect_partner_name}")
                    print(f"   Using Messaging Connect: Yes")
                else:
                    print(f"   Using Messaging Connect: No")
            else:
                print(f"❌ Failed to send SMS to {sms_response.to}")
                print(f"   Error: {sms_response.error_message}")
                print(f"   HTTP Status: {sms_response.http_status_code}")
                
    except ValueError as e:
        print(f"❌ Validation Error: {e}")
        print("   Make sure both API key and partner name are provided together for Messaging Connect")
    except Exception as e:
        print(f"❌ Error sending SMS: {e}")
    # [END send_sms_with_advanced_options]

    print("\nℹ️  Advanced SMS Options Summary:")
    print("   - Delivery Report Timeout: Controls when to generate timeout error")
    print("   - Range: 60 to 43200 seconds (1 minute to 12 hours)")
    print("   - Messaging Connect: Enables partner network delivery")
    print("   - Both API key and partner name required for Messaging Connect")
    print("   - These options can be used independently or together")

if __name__ == "__main__":
    main()

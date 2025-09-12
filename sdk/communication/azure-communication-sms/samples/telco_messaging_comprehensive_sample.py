#!/usr/bin/env python

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: telco_messaging_comprehensive_sample.py

DESCRIPTION:
    This sample demonstrates how to use the TelcoMessagingClient to send SMS messages,
    retrieve delivery reports, and manage opt-out lists.

USAGE:
    python telco_messaging_comprehensive_sample.py

    Set the environment variable with your own value before running the sample:
    1) COMMUNICATION_SERVICES_CONNECTION_STRING - the connection string in your Communication Services resource
    2) SENDER_PHONE_NUMBER - a phone number associated with your Communication Services resource
    3) RECIPIENT_PHONE_NUMBER - the phone number you want to send the message to
"""

import os
from azure.communication.sms import TelcoMessagingClient

def main():
    # [START create_telco_messaging_client]
    # Get connection string from environment variable
    connection_string = os.environ["COMMUNICATION_SERVICES_CONNECTION_STRING"]
    
    # Create TelcoMessagingClient
    telco_client = TelcoMessagingClient.from_connection_string(connection_string)
    
    # Access sub-clients
    sms_client = telco_client.sms
    delivery_reports_client = telco_client.delivery_reports
    opt_outs_client = telco_client.opt_outs
    # [END create_telco_messaging_client]
    
    # Get phone numbers from environment
    sender_phone_number = os.environ["SENDER_PHONE_NUMBER"]
    recipient_phone_number = os.environ["RECIPIENT_PHONE_NUMBER"]
    
    # [START send_sms_with_delivery_reports]
    # Send SMS message with delivery reports enabled
    sms_responses = sms_client.send(
        from_=sender_phone_number,
        to=recipient_phone_number,
        message="Hello from Azure Communication Services SMS SDK!",
        enable_delivery_report=True,
        tag="sample-message"
    )
    
    # Process SMS responses
    for sms_response in sms_responses:
        if sms_response.successful:
            print(f"Message sent successfully to {sms_response.to}")
            print(f"Message ID: {sms_response.message_id}")
            
            # Retrieve delivery report for the message
            try:
                delivery_report = delivery_reports_client.get_status(sms_response.message_id)
                if delivery_report:
                    print(f"Delivery status: {getattr(delivery_report, 'delivery_status', 'Unknown')}")
                    print(f"Delivery timestamp: {getattr(delivery_report, 'delivery_timestamp', 'Unknown')}")
            except Exception as e:
                print(f"Could not retrieve delivery report: {e}")
        else:
            print(f"Message failed to send to {sms_response.to}")
            print(f"Error code: {sms_response.http_status_code}")
            print(f"Error message: {sms_response.error_message}")
    # [END send_sms_with_delivery_reports]
    
    # [START manage_opt_outs]
    try:
        # Check current opt-out status
        print("Checking opt-out status...")
        check_results = opt_outs_client.check_opt_out(from_=sender_phone_number, to=recipient_phone_number)
        for result in check_results:
            print(f"Current opt-out status for {result.to}: {'Opted out' if result.is_opted_out else 'Not opted out'}")
        
        # Add phone number to opt-out list
        print("Adding phone number to opt-out list...")
        add_results = opt_outs_client.add_opt_out(from_=sender_phone_number, to=recipient_phone_number)
        for result in add_results:
            if result.http_status_code == 200 and not result.error_message:
                print(f"Successfully added {result.to} to opt-out list")
            else:
                print(f"Failed to add {result.to}: {result.error_message or 'HTTP ' + str(result.http_status_code)}")
        
        # Check opt-out status again
        print("Checking opt-out status after adding...")
        check_results = opt_outs_client.check_opt_out(from_=sender_phone_number, to=recipient_phone_number)
        for result in check_results:
            print(f"Updated opt-out status for {result.to}: {'Opted out' if result.is_opted_out else 'Not opted out'}")
        
        # Remove phone number from opt-out list (cleanup)
        print("Removing phone number from opt-out list...")
        remove_results = opt_outs_client.remove_opt_out(from_=sender_phone_number, to=recipient_phone_number)
        for result in remove_results:
            if result.http_status_code == 200 and not result.error_message:
                print(f"Successfully removed {result.to} from opt-out list")
            else:
                print(f"Failed to remove {result.to}: {result.error_message or 'HTTP ' + str(result.http_status_code)}")
        
    except Exception as e:
        print(f"Error managing opt-outs: {e}")
    # [END manage_opt_outs]

if __name__ == "__main__":
    main()

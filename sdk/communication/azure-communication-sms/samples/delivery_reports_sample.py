#!/usr/bin/env python

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: delivery_reports_sample.py

DESCRIPTION:
    This sample demonstrates how to use the SmsClient to retrieve 
    delivery reports for SMS messages.

USAGE:
    python delivery_reports_sample.py

    Set the environment variable with your own value before running the sample:
    1) COMMUNICATION_SERVICES_CONNECTION_STRING - the connection string in your Communication Services resource
    2) SMS_MESSAGE_ID - the ID of an SMS message for which you want to retrieve delivery report
"""

import os
from azure.communication.sms import SmsClient

def main():
    # [START create_sms_client]
    # Get connection string from environment variable
    connection_string = os.environ["COMMUNICATION_SERVICES_CONNECTION_STRING"]
    
    # Create SmsClient from connection string
    sms_client = SmsClient.from_connection_string(connection_string)
    # [END create_sms_client]
    
    # Get message ID from environment
    message_id = os.environ.get("SMS_MESSAGE_ID", "sample-message-id")
    
    # [START get_delivery_status]
    try:
        # Retrieve delivery report for the message using SmsClient
        delivery_report = sms_client.get_delivery_report(message_id)
        
        if delivery_report:
            print(f"Delivery report retrieved successfully for message ID: {message_id}")
            
            # Access delivery report properties
            print(f"Message ID: {delivery_report.message_id}")
            print(f"From: {delivery_report.from_property}")
            print(f"To: {delivery_report.to}")
            print(f"Delivery status: {delivery_report.delivery_status}")
            
            if delivery_report.delivery_status_details:
                print(f"Delivery status details: {delivery_report.delivery_status_details}")
                
            if delivery_report.received_timestamp:
                print(f"Received timestamp: {delivery_report.received_timestamp}")
                
            if delivery_report.tag:
                print(f"Tag: {delivery_report.tag}")
                
            if delivery_report.delivery_attempts:
                print(f"Number of delivery attempts: {len(delivery_report.delivery_attempts)}")
                for i, attempt in enumerate(delivery_report.delivery_attempts):
                    print(f"  Attempt {i+1}: {attempt}")
                
        else:
            print(f"No delivery report found for message ID: {message_id}")
            
    except Exception as e:
        print(f"Error retrieving delivery report: {e}")
        print(f"This could happen if the message ID doesn't exist or the message is too old")
    # [END get_delivery_status]

if __name__ == "__main__":
    main()

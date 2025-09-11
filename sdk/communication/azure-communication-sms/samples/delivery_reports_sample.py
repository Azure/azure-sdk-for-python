#!/usr/bin/env python

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: delivery_reports_sample.py

DESCRIPTION:
    This sample demonstrates how to use the DeliveryReportsClient to retrieve 
    delivery reports for SMS messages.

USAGE:
    python delivery_reports_sample.py

    Set the environment variable with your own value before running the sample:
    1) COMMUNICATION_SERVICES_CONNECTION_STRING - the connection string in your Communication Services resource
    2) SMS_MESSAGE_ID - the ID of an SMS message for which you want to retrieve delivery report
"""

import os
from azure.communication.sms import DeliveryReportsClient

def main():
    # [START create_delivery_reports_client]
    # Get connection string from environment variable
    connection_string = os.environ["COMMUNICATION_SERVICES_CONNECTION_STRING"]
    
    # Create DeliveryReportsClient from connection string
    delivery_reports_client = DeliveryReportsClient.from_connection_string(connection_string)
    # [END create_delivery_reports_client]
    
    # Get message ID from environment
    message_id = os.environ.get("SMS_MESSAGE_ID", "sample-message-id")
    
    # [START get_delivery_status]
    try:
        # Retrieve delivery report for the message
        delivery_report = delivery_reports_client.get_status(message_id)
        
        if delivery_report:
            print(f"Delivery report retrieved successfully for message ID: {message_id}")
            
            # Access delivery report properties (these may vary based on the actual model)
            delivery_status = getattr(delivery_report, 'delivery_status', 'Unknown')
            delivery_timestamp = getattr(delivery_report, 'delivery_timestamp', 'Unknown')
            error_code = getattr(delivery_report, 'error_code', None)
            
            print(f"Delivery status: {delivery_status}")
            print(f"Delivery timestamp: {delivery_timestamp}")
            
            if error_code:
                print(f"Error code: {error_code}")
                
        else:
            print(f"No delivery report found for message ID: {message_id}")
            
    except Exception as e:
        print(f"Error retrieving delivery report: {e}")
        print(f"This could happen if the message ID doesn't exist or the message is too old")
    # [END get_delivery_status]

if __name__ == "__main__":
    main()

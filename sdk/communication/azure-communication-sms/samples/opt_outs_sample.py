#!/usr/bin/env python

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: opt_outs_sample.py

DESCRIPTION:
    This sample demonstrates how to use the OptOutsClient to manage SMS opt-out lists.

USAGE:
    python opt_outs_sample.py

    Set the environment variable with your own value before running the sample:
    1) COMMUNICATION_SERVICES_CONNECTION_STRING - the connection string in your Communication Services resource
    2) SENDER_PHONE_NUMBER - a phone number associated with your Communication Services resource
    3) RECIPIENT_PHONE_NUMBER - the phone number you want to manage in the opt-out list
"""

import os
from azure.communication.sms import OptOutsClient

def main():
    # [START create_opt_outs_client]
    # Get connection string from environment variable
    connection_string = os.environ["COMMUNICATION_SERVICES_CONNECTION_STRING"]
    
    # Create OptOutsClient from connection string
    opt_outs_client = OptOutsClient.from_connection_string(connection_string)
    # [END create_opt_outs_client]
    
    # Get phone numbers from environment
    sender_phone_number = os.environ["SENDER_PHONE_NUMBER"]
    recipient_phone_number = os.environ["RECIPIENT_PHONE_NUMBER"]
    
    # [START manage_opt_out_list]
    # Create opt-out request
    opt_out_request = {
        "from": sender_phone_number,
        "recipients": [{"to": recipient_phone_number}]
    }
    
    try:
        print(f"Managing opt-out list for {recipient_phone_number} from {sender_phone_number}")
        
        # Check current opt-out status
        print("1. Checking current opt-out status...")
        check_response = opt_outs_client.check_opt_out(opt_out_request)
        print(f"Current opt-out status: {check_response}")
        
        # [START add_opt_out]
        # Add phone number to opt-out list
        print("2. Adding phone number to opt-out list...")
        add_response = opt_outs_client.add_opt_out(opt_out_request)
        print(f"Add opt-out response: {add_response}")
        # [END add_opt_out]
        
        # Check opt-out status after adding
        print("3. Checking opt-out status after adding...")
        check_response_after_add = opt_outs_client.check_opt_out(opt_out_request)
        print(f"Status after adding: {check_response_after_add}")
        
        # [START remove_opt_out]
        # Remove phone number from opt-out list
        print("4. Removing phone number from opt-out list...")
        remove_response = opt_outs_client.remove_opt_out(opt_out_request)
        print(f"Remove opt-out response: {remove_response}")
        # [END remove_opt_out]
        
        # [START check_opt_out]
        # Check final opt-out status
        print("5. Checking final opt-out status...")
        final_check_response = opt_outs_client.check_opt_out(opt_out_request)
        print(f"Final opt-out status: {final_check_response}")
        # [END check_opt_out]
        
    except Exception as e:
        print(f"Error managing opt-outs: {e}")
        print("This could happen if the phone numbers are invalid or there's a service issue")
    # [END manage_opt_out_list]

if __name__ == "__main__":
    main()

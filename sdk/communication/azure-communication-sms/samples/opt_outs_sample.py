#!/usr/bin/env python

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: opt_outs_sample.py

DESCRIPTION:
    This sample demonstrates how to manage SMS opt-out lists using both the
    hierarchical client pattern (recommended) and direct client access (alternative).

USAGE:
    python opt_outs_sample.py

    Set the environment variable with your own value before running the sample:
    1) COMMUNICATION_SERVICES_CONNECTION_STRING - the connection string in your Communication Services resource
    2) SENDER_PHONE_NUMBER - a phone number associated with your Communication Services resource
    3) RECIPIENT_PHONE_NUMBER - the phone number you want to manage in the opt-out list
"""

import os
from azure.communication.sms import SmsClient, OptOutsClient

def main():
    # Get configuration from environment
    connection_string = os.environ["COMMUNICATION_SERVICES_CONNECTION_STRING"]
    sender_phone_number = os.environ["SENDER_PHONE_NUMBER"]
    recipient_phone_number = os.environ["RECIPIENT_PHONE_NUMBER"]
    
    # [START create_opt_outs_client_hierarchical]
    # Approach 1: Hierarchical pattern (recommended)
    # Create SmsClient first, then get OptOutsClient from it
    sms_client = SmsClient.from_connection_string(connection_string)
    opt_outs_client_hierarchical = sms_client.get_opt_outs_client()
    # [END create_opt_outs_client_hierarchical]
    
    # [START create_opt_outs_client_direct]
    # Approach 2: Direct client access (alternative)
    # Create OptOutsClient directly from connection string
    opt_outs_client_direct = OptOutsClient.from_connection_string(connection_string)
    # [END create_opt_outs_client_direct]
    
    print("=== Demonstrating Hierarchical Pattern (Recommended) ===")
    manage_opt_outs_example(opt_outs_client_hierarchical, sender_phone_number, recipient_phone_number, "hierarchical")
    
    print("\n=== Demonstrating Direct Access (Alternative) ===") 
    manage_opt_outs_example(opt_outs_client_direct, sender_phone_number, recipient_phone_number, "direct")

def manage_opt_outs_example(opt_outs_client, sender_phone_number, recipient_phone_number, approach_name):
    # [START manage_opt_out_list]
    try:
        print(f"Managing opt-out list using {approach_name} approach")
        print(f"Target: {recipient_phone_number} from {sender_phone_number}")
        
        # Check current opt-out status
        print("1. Checking current opt-out status...")
        check_results = opt_outs_client.check_opt_out(from_=sender_phone_number, to=recipient_phone_number)
        for result in check_results:
            print(f"Current opt-out status for {result.to}: {'Opted out' if result.is_opted_out else 'Not opted out'}")
        
        # [START add_opt_out]
        # Add phone number to opt-out list
        print("2. Adding phone number to opt-out list...")
        add_results = opt_outs_client.add_opt_out(from_=sender_phone_number, to=recipient_phone_number)
        for result in add_results:
            if result.http_status_code == 200 and not result.error_message:
                print(f"✅ Successfully added {result.to} to opt-out list")
            else:
                print(f"❌ Failed to add {result.to}: {result.error_message or 'HTTP ' + str(result.http_status_code)}")
        # [END add_opt_out]
        
        # Check opt-out status after adding
        print("3. Checking opt-out status after adding...")
        check_results_after_add = opt_outs_client.check_opt_out(from_=sender_phone_number, to=recipient_phone_number)
        for result in check_results_after_add:
            print(f"Status after adding for {result.to}: {'Opted out' if result.is_opted_out else 'Not opted out'}")
        
        # [START remove_opt_out]
        # Remove phone number from opt-out list
        print("4. Removing phone number from opt-out list...")
        remove_results = opt_outs_client.remove_opt_out(from_=sender_phone_number, to=recipient_phone_number)
        for result in remove_results:
            if result.http_status_code == 200 and not result.error_message:
                print(f"✅ Successfully removed {result.to} from opt-out list")
            else:
                print(f"❌ Failed to remove {result.to}: {result.error_message or 'HTTP ' + str(result.http_status_code)}")
        # [END remove_opt_out]
        
        # [START check_opt_out]
        # Check final opt-out status
        print("5. Checking final opt-out status...")
        final_check_results = opt_outs_client.check_opt_out(from_=sender_phone_number, to=recipient_phone_number)
        for result in final_check_results:
            print(f"Final opt-out status for {result.to}: {'Opted out' if result.is_opted_out else 'Not opted out'}")
        # [END check_opt_out]
        
    except Exception as e:
        print(f"❌ Error managing opt-outs: {e}")
        print("This could happen if the phone numbers are invalid or there's a service issue")
    # [END manage_opt_out_list]


if __name__ == "__main__":
    main()
    
    print("\nℹ️  Client Access Pattern Information:")
    print("   📋 HIERARCHICAL PATTERN (Recommended):")
    print("      - Use: sms_client.get_opt_outs_client()")  
    print("      - Follows Azure SDK Design Guidelines")
    print("      - Better consistency with other Azure services")
    print("   📋 DIRECT ACCESS (Alternative):")
    print("      - Use: OptOutsClient.from_connection_string()")
    print("      - Useful when you only need opt-out functionality")
    print("      - Both patterns support the same authentication methods")

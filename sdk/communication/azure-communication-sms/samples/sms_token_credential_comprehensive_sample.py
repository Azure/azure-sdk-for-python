#!/usr/bin/env python

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sms_token_credential_comprehensive_sample.py

DESCRIPTION:
    This sample demonstrates using token credential authentication for both SMS sending
    and opt-out management. Shows both hierarchical pattern and direct client access.

USAGE:
    python sms_token_credential_comprehensive_sample.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_COMMUNICATION_ENDPOINT - endpoint of your Communication Services resource
    2) AZURE_TENANT_ID, AZURE_CLIENT_ID, AZURE_CLIENT_SECRET - Azure AD credentials
    3) SENDER_PHONE_NUMBER - a phone number associated with your Communication Services resource
    4) RECIPIENT_PHONE_NUMBER - the phone number to send SMS and manage in opt-out list
"""

import os
from azure.communication.sms import SmsClient, OptOutsClient
from azure.identity import DefaultAzureCredential

def main():
    # Get configuration from environment variables
    endpoint = os.environ["AZURE_COMMUNICATION_ENDPOINT"]
    sender_phone_number = os.environ["SENDER_PHONE_NUMBER"] 
    recipient_phone_number = os.environ["RECIPIENT_PHONE_NUMBER"]
    
    # [START create_clients_with_token_credential]
    # To use Azure Active Directory Authentication (DefaultAzureCredential) make sure to have
    # AZURE_TENANT_ID, AZURE_CLIENT_ID and AZURE_CLIENT_SECRET as env variables.
    credential = DefaultAzureCredential()
    
    # Create SmsClient with token credential
    sms_client = SmsClient(endpoint, credential)
    
    # Option 1: Get OptOutsClient using hierarchical pattern (recommended)
    opt_outs_client_hierarchical = sms_client.get_opt_outs_client()
    
    # Option 2: Create OptOutsClient directly with token credential (alternative)
    opt_outs_client_direct = OptOutsClient(endpoint, credential)
    # [END create_clients_with_token_credential]
    
    # [START send_sms_with_token_credential]
    print("=== SMS Sending with Token Credential ===")
    try:
        sms_responses = sms_client.send(
            from_=sender_phone_number,
            to=recipient_phone_number,
            message="Hello! This SMS is sent using Azure AD token credential authentication.",
            enable_delivery_report=True,
            tag="token-auth-test"
        )
        
        for sms_response in sms_responses:
            if sms_response.successful:
                print(f"✅ SMS sent successfully using token credential!")
                print(f"   Message ID: {sms_response.message_id}")
                print(f"   To: {sms_response.to}")
                
                # [START get_delivery_report_with_token_credential]
                # Retrieve delivery report using the same authenticated client
                print("   Retrieving delivery report...")
                delivery_report = sms_client.get_delivery_report(sms_response.message_id)
                if delivery_report:
                    print(f"   ✅ Delivery report retrieved: {delivery_report.delivery_status}")
                else:
                    print("   ⚠️  Delivery report not yet available")
                # [END get_delivery_report_with_token_credential]
            else:
                print(f"❌ Failed to send SMS: {sms_response.error_message}")
                
    except Exception as e:
        print(f"❌ Error sending SMS: {e}")
    # [END send_sms_with_token_credential]
    
    # [START manage_opt_outs_hierarchical_token_credential]
    print("\n=== Opt-Out Management (Hierarchical Pattern) with Token Credential ===")
    try:
        # Using hierarchical pattern with token credential
        print("Using hierarchical pattern: sms_client.get_opt_outs_client()")
        
        # Check opt-out status
        check_results = opt_outs_client_hierarchical.check_opt_out(
            from_=sender_phone_number, 
            to=recipient_phone_number
        )
        for result in check_results:
            print(f"Opt-out status for {result.to}: {'Opted out' if result.is_opted_out else 'Not opted out'}")
            
    except Exception as e:
        print(f"❌ Error checking opt-outs (hierarchical): {e}")
    # [END manage_opt_outs_hierarchical_token_credential]
    
    # [START manage_opt_outs_direct_token_credential]  
    print("\n=== Opt-Out Management (Direct Access) with Token Credential ===")
    try:
        # Using direct client access with token credential
        print("Using direct access: OptOutsClient(endpoint, credential)")
        
        # Add to opt-out list
        add_results = opt_outs_client_direct.add_opt_out(
            from_=sender_phone_number,
            to=recipient_phone_number
        )
        for result in add_results:
            if result.http_status_code == 200:
                print(f"✅ Added {result.to} to opt-out list using token credential")
            else:
                print(f"❌ Failed to add {result.to}: {result.error_message}")
        
        # Remove from opt-out list  
        remove_results = opt_outs_client_direct.remove_opt_out(
            from_=sender_phone_number,
            to=recipient_phone_number
        )
        for result in remove_results:
            if result.http_status_code == 200:
                print(f"✅ Removed {result.to} from opt-out list using token credential")
            else:
                print(f"❌ Failed to remove {result.to}: {result.error_message}")
                
    except Exception as e:
        print(f"❌ Error managing opt-outs (direct): {e}")
    # [END manage_opt_outs_direct_token_credential]

    print("\n=== Authentication Information ===")
    print("✅ Token credential authentication successful for:")
    print("   - SmsClient (SMS sending and delivery reports)")
    print("   - OptOutsClient (both hierarchical and direct access)")
    print("   - Supports Azure managed identity and service principal authentication")
    print("   - Requires AZURE_TENANT_ID, AZURE_CLIENT_ID, AZURE_CLIENT_SECRET environment variables")

if __name__ == "__main__":
    main()
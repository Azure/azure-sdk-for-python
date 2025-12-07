#!/usr/bin/env python

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sms_api_versioning_sample.py

DESCRIPTION:
    This sample demonstrates how to use the SmsClient with the default API version (2026-01-23).
    The latest API version provides access to all current features and is backward compatible.

USAGE:
    python sms_api_versioning_sample.py

    Set the environment variable with your own value before running the sample:
    1) COMMUNICATION_SERVICES_CONNECTION_STRING - the connection string in your Communication Services resource
    2) SENDER_PHONE_NUMBER - the phone number you want to send the SMS from
    3) RECIPIENT_PHONE_NUMBER - the phone number you want to send the SMS to
"""

import os
from azure.communication.sms import SmsClient

def main():
    connection_string = os.environ["COMMUNICATION_SERVICES_CONNECTION_STRING"]
    sender_phone_number = os.environ["SENDER_PHONE_NUMBER"]
    recipient_phone_number = os.environ["RECIPIENT_PHONE_NUMBER"]
    
    # [START use_default_api_version]
    # Using default API version (2026-01-23) - recommended approach
    # The default version provides access to all latest features
    sms_client = SmsClient.from_connection_string(connection_string)
    # [END use_default_api_version]
    
    # [START use_explicit_api_version]
    # You can also explicitly specify the API version if needed
    sms_client_explicit = SmsClient.from_connection_string(
        connection_string, 
        api_version="2026-01-23"
    )
    # [END use_explicit_api_version]
    
    # [START send_sms_with_latest_features]
    # Send SMS using the latest API version with all current features
    try:
        sms_responses = sms_client.send(
            from_=sender_phone_number,
            to=[recipient_phone_number],
            message="Hello! This SMS uses the latest API version with full feature support.",
            enable_delivery_report=True,
            delivery_report_timeout_in_seconds=3600,  # Delivery timeout feature
            tag="api-versioning-latest"
        )
        
        for sms_response in sms_responses:
            if sms_response.successful:
                print(f"✅ Message sent successfully with latest API!")
                print(f"   To: {sms_response.to}")
                print(f"   Message ID: {sms_response.message_id}")
                
                # Get delivery report using direct method (latest API feature)
                if sms_response.message_id:
                    try:
                        delivery_report = sms_client.get_delivery_report(sms_response.message_id)
                        if delivery_report:
                            print(f"   ✅ Delivery status: {delivery_report.delivery_status}")
                        else:
                            print(f"   ⏳ Delivery report not yet available")
                    except Exception as e:
                        print(f"   ⚠️  Delivery report retrieval: {e}")
                        
                # Demonstrate opt-outs client access (hierarchical pattern)
                opt_outs_client = sms_client.get_opt_outs_client()
                print(f"   ✅ OptOuts client accessible via hierarchical pattern")
                
            else:
                print(f"❌ Message failed to send to {sms_response.to}: {sms_response.error_message}")
                
    except Exception as ex:
        print(f"❌ Error sending SMS: {ex}")
    # [END send_sms_with_latest_features]
if __name__ == "__main__":
    main()
    
    print("\nℹ️  API Version Information:")
    print("   📋 DEFAULT VERSION: 2026-01-23")
    print("      - Provides access to all latest features")
    print("      - Includes delivery reports, opt-outs, MessagingConnect")
    print("      - Hierarchical client pattern support")
    print("      - Backward compatible with previous versions")
    print("   📋 RECOMMENDATION:")
    print("      - Use the default API version for new applications")
    print("      - Latest version is always backward compatible")
    print("      - No need to specify api_version parameter explicitly")
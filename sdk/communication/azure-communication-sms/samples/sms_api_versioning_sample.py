#!/usr/bin/env python

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sms_api_versioning_sample.py

DESCRIPTION:
    This sample demonstrates how to use different API versions with the SmsClient.

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
    # Using default API version (2026-01-23)
    sms_client_default = SmsClient.from_connection_string(connection_string)
    # [END use_default_api_version]
    
    # [START use_specific_api_version]
    # Using a specific API version
    sms_client_specific = SmsClient.from_connection_string(
        connection_string, 
        api_version="2026-01-23"
    )
    # [END use_specific_api_version]
    
    # [START use_legacy_api_version]
    # Using legacy API version for backward compatibility
    sms_client_legacy = SmsClient.from_connection_string(
        connection_string, 
        api_version="2021-03-07"
    )
    # [END use_legacy_api_version]
    
    # Send SMS using default API version (latest features available)
    try:
        sms_responses = sms_client_default.send(
            from_=sender_phone_number,
            to=[recipient_phone_number],
            message="Hello World from SMS SDK with latest API!",
            enable_delivery_report=True,
            delivery_report_timeout_in_seconds=300,  # 5 minutes timeout
            tag="api-versioning-sample"
        )
        
        for sms_response in sms_responses:
            if sms_response.successful:
                print(f"Message sent successfully to {sms_response.to}")
                print(f"Message ID: {sms_response.message_id}")
                
                # Get delivery report (available with latest API)
                if sms_response.message_id:
                    try:
                        delivery_report = sms_client_default.get_delivery_report(sms_response.message_id)
                        print(f"Delivery status: {delivery_report.delivery_status}")
                    except Exception as e:
                        print(f"Could not retrieve delivery report yet: {e}")
            else:
                print(f"Message failed to send to {sms_response.to}: {sms_response.error_message}")
                
    except Exception as ex:
        print(f"Error sending SMS: {ex}")
    
    # Send SMS using legacy API version (for backward compatibility)
    try:
        sms_responses_legacy = sms_client_legacy.send(
            from_=sender_phone_number,
            to=[recipient_phone_number],
            message="Hello World from SMS SDK with legacy API!",
            enable_delivery_report=True,
            tag="legacy-api-sample"
            # Note: delivery_report_timeout_in_seconds and messaging_connect features
            # may not be available in older API versions
        )
        
        for sms_response in sms_responses_legacy:
            if sms_response.successful:
                print(f"Legacy API - Message sent successfully to {sms_response.to}")
                print(f"Legacy API - Message ID: {sms_response.message_id}")
            else:
                print(f"Legacy API - Message failed to send to {sms_response.to}: {sms_response.error_message}")
                
    except Exception as ex:
        print(f"Error sending SMS with legacy API: {ex}")

if __name__ == "__main__":
    main()
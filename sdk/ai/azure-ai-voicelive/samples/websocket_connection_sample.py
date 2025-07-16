#!/usr/bin/env python

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: websocket_connection_sample.py
DESCRIPTION:
    This sample demonstrates how to use WebSocket connections with the Azure VoiceLive SDK.
USAGE:
    python websocket_connection_sample.py
    
    Set the environment variables with your own values before running the sample:
    1) AZURE_VOICELIVE_API_KEY - The API key for your VoiceLive resource.
    2) AZURE_VOICELIVE_ENDPOINT - The endpoint for your VoiceLive resource.
"""

import os
import time
from azure.ai.voicelive import VoiceLiveClient
from azure.core.credentials import AzureKeyCredential

def main():
    # Get credentials from environment variables
    api_key = os.environ.get("AZURE_VOICELIVE_API_KEY", "your-api-key")
    endpoint = os.environ.get("AZURE_VOICELIVE_ENDPOINT", "wss://api.voicelive.com/v1")
    
    print(f"Using endpoint: {endpoint}")
    
    # Create client
    client = VoiceLiveClient(
        credential=AzureKeyCredential(api_key),
        endpoint=endpoint
    )
    
    # Define model to use
    model = "voicelive-model-name"  # Replace with actual model name
    
    print("Connecting to WebSocket...")
    try:
        # Connect to the WebSocket API
        with client.connect(model=model) as connection:
            # Send a simple session update event
            connection.send({
                "type": "session.update",
                "session": {
                    "modalities": ["audio", "text"]
                }
            })
            
            print("Sent session update request. Waiting for response...")
            
            # Receive events for a few seconds
            timeout = time.time() + 10  # 10 second timeout
            for event in connection:
                print(f"Received event: {event}")
                
                # Exit after session is updated or timeout
                if event.get('type') == 'session.updated' or time.time() > timeout:
                    break
    
    except ImportError:
        print("You need to install the websockets and httpx packages to run this sample:")
        print("pip install azure-ai-voicelive[websockets]")
    except Exception as e:
        print(f"Error during WebSocket connection: {e}")

if __name__ == "__main__":
    main()
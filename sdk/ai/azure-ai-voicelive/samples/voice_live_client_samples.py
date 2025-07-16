# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------

"""
FILE: voice_live_client_samples.py
DESCRIPTION:
    These samples demonstrate the use of the VoiceLiveClient for WebSocket-based 
    communication with the Azure AI VoiceLive service.
USAGE:
    python voice_live_client_samples.py
    Set the environment variables with your own values before running the sample:
    1) AZURE_VOICELIVE_ENDPOINT - The endpoint for your Azure AI VoiceLive resource.
    2) AZURE_CLIENT_ID - The client ID of your active directory application.
    3) AZURE_TENANT_ID - The tenant ID of your active directory application.
    4) AZURE_CLIENT_SECRET - The secret of your active directory application.
"""

import os
import asyncio
from azure.identity import DefaultAzureCredential
from azure.identity.aio import DefaultAzureCredential as AsyncDefaultAzureCredential
from azure.ai.voicelive import VoiceLiveClient
from azure.ai.voicelive.aio import AsyncVoiceLiveClient


def sync_voice_live_client_sample():
    """
    Demonstrates the use of the synchronous VoiceLiveClient
    """
    # Get credential and create client
    credential = DefaultAzureCredential()
    endpoint = os.environ.get("AZURE_VOICELIVE_ENDPOINT", "wss://voicelive.azure.com")
    
    # Create the client
    client = VoiceLiveClient(credential=credential, endpoint=endpoint)
    
    # Connect to the service
    client.connect()
    print(f"Connected to {endpoint}")
    
    # Add your code to interact with the service here
    # ...
    
    # Disconnect when done
    client.disconnect()
    print("Disconnected from service")


async def async_voice_live_client_sample():
    """
    Demonstrates the use of the asynchronous AsyncVoiceLiveClient
    """
    # Get credential and create client
    credential = AsyncDefaultAzureCredential()
    endpoint = os.environ.get("AZURE_VOICELIVE_ENDPOINT", "wss://voicelive.azure.com")
    
    # Create the client
    client = AsyncVoiceLiveClient(credential=credential, endpoint=endpoint)
    
    # Connect to the service
    await client.connect()
    print(f"Connected to {endpoint}")
    
    # Add your code to interact with the service here
    # ...
    
    # Disconnect when done
    await client.disconnect()
    print("Disconnected from service")


async def main():
    print("\nSynchronous sample:")
    sync_voice_live_client_sample()
    
    print("\nAsynchronous sample:")
    await async_voice_live_client_sample()


if __name__ == "__main__":
    asyncio.run(main())
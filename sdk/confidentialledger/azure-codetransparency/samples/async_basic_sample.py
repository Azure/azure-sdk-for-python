#!/usr/bin/env python3

# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------

"""
This sample demonstrates how to use the Azure Code Transparency Service client library
with async/await patterns.

To run this sample, you need:
1. An Azure subscription
2. A Code Transparency Service instance
3. Set the environment variable AZURE_CODETRANSPARENCY_ENDPOINT to your instance URL

The DefaultAzureCredential will automatically handle authentication by trying different
credential types in order (environment variables, managed identity, Azure CLI, etc.).
"""

import asyncio
import os
from azure.identity.aio import DefaultAzureCredential
from azure.codetransparency.aio import CodeTransparencyClient


async def main():
    # Get the endpoint from environment variable
    endpoint = os.environ.get("AZURE_CODETRANSPARENCY_ENDPOINT")
    if not endpoint:
        print("Please set the AZURE_CODETRANSPARENCY_ENDPOINT environment variable")
        print("Example: https://your-instance.confidentialledger.azure.com/")
        return

    # Create a credential object for async usage
    # DefaultAzureCredential will automatically find the best authentication method
    credential = DefaultAzureCredential()

    # Create the async client
    print(f"Creating async Code Transparency client for endpoint: {endpoint}")
    
    async with CodeTransparencyClient(endpoint=endpoint, credential=credential) as client:
        print("Async Code Transparency client created successfully!")
        print("Client is ready to use for transparency operations.")
        
        # Example async usage would go here - actual API calls would be added
        # once the service operations are implemented
        print("You can now use the async client to interact with the Code Transparency Service.")

    # Close the credential when done
    await credential.close()


if __name__ == "__main__":
    asyncio.run(main())
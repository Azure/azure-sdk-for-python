#!/usr/bin/env python3

# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------

"""
This sample demonstrates how to use the Azure Code Transparency Service client library
to create a basic client and authenticate with Azure.

To run this sample, you need:
1. An Azure subscription
2. A Code Transparency Service instance
3. Set the environment variable AZURE_CODETRANSPARENCY_ENDPOINT to your instance URL

The DefaultAzureCredential will automatically handle authentication by trying different
credential types in order (environment variables, managed identity, Azure CLI, etc.).
"""

import os
from azure.identity import DefaultAzureCredential
from azure.codetransparency import CodeTransparencyClient


def main():
    # Get the endpoint from environment variable
    endpoint = os.environ.get("AZURE_CODETRANSPARENCY_ENDPOINT")
    if not endpoint:
        print("Please set the AZURE_CODETRANSPARENCY_ENDPOINT environment variable")
        print("Example: https://your-instance.confidentialledger.azure.com/")
        return

    # Create a credential object
    # DefaultAzureCredential will automatically find the best authentication method
    credential = DefaultAzureCredential()

    # Create the client
    print(f"Creating Code Transparency client for endpoint: {endpoint}")
    
    with CodeTransparencyClient(endpoint=endpoint, credential=credential) as client:
        print("Code Transparency client created successfully!")
        print("Client is ready to use for transparency operations.")
        
        # Example usage would go here - actual API calls would be added
        # once the service operations are implemented
        print("You can now use the client to interact with the Code Transparency Service.")


if __name__ == "__main__":
    main()
# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
"""
FILE: sample_authentication.py

DESCRIPTION:
    This sample demonstrates how to authenticate with the Code Transparency Service
    using different authentication methods.

USAGE:
    python sample_authentication.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_CODETRANSPARENCY_ENDPOINT - the endpoint of your Code Transparency service
    2) AZURE_CODETRANSPARENCY_API_KEY - the API key for your Code Transparency service
"""

import os


def authenticate_with_api_key():
    # [START authenticate_with_api_key]
    from azure.codetransparency import CodeTransparencyClient
    from azure.core.credentials import AzureKeyCredential

    endpoint = os.getenv("AZURE_CODETRANSPARENCY_ENDPOINT")
    api_key = os.getenv("AZURE_CODETRANSPARENCY_API_KEY")

    if endpoint is None or api_key is None:
        raise ValueError(
            "Please set AZURE_CODETRANSPARENCY_ENDPOINT and AZURE_CODETRANSPARENCY_API_KEY environment variables"
        )

    client = CodeTransparencyClient(
        endpoint=endpoint,
        credential=AzureKeyCredential(key=api_key)
    )

    # Test the client with a simple operation
    try:
        result = client.get_public_keys()
        print("Successfully authenticated with API key")
        # Process the result as needed
        print(f"Received response from get_public_keys")
    except Exception as e:
        print(f"Authentication failed: {e}")
    # [END authenticate_with_api_key]


def authenticate_with_azure_active_directory():
    # [START authenticate_with_azure_active_directory]
    from azure.codetransparency import CodeTransparencyClient
    from azure.identity import DefaultAzureCredential

    endpoint = os.getenv("AZURE_CODETRANSPARENCY_ENDPOINT")
    
    if endpoint is None:
        raise ValueError("Please set AZURE_CODETRANSPARENCY_ENDPOINT environment variable")

    # DefaultAzureCredential will use the appropriate Azure AD authentication method
    # based on your environment setup
    credential = DefaultAzureCredential()
    
    client = CodeTransparencyClient(
        endpoint=endpoint,
        credential=credential
    )

    # Test the client with a simple operation
    try:
        result = client.get_public_keys()
        print("Successfully authenticated with Azure Active Directory")
        # Process the result as needed
        print(f"Received response from get_public_keys")
    except Exception as e:
        print(f"Authentication failed: {e}")
    # [END authenticate_with_azure_active_directory]


if __name__ == "__main__":
    print("---Authenticating with API key---")
    authenticate_with_api_key()
    
    print("\n---Authenticating with Azure Active Directory---")
    try:
        authenticate_with_azure_active_directory()
    except Exception as e:
        print(f"Azure AD authentication example couldn't be run: {e}")

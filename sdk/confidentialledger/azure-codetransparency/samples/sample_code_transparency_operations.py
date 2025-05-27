# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
"""
FILE: sample_code_transparency_operations.py

DESCRIPTION:
    This sample demonstrates common operations with the Code Transparency Service,
    including creating entries, retrieving entries, and getting entry statements.

USAGE:
    python sample_code_transparency_operations.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_CODETRANSPARENCY_ENDPOINT - the endpoint of your Code Transparency service
    2) AZURE_CODETRANSPARENCY_API_KEY - the API key for your Code Transparency service
"""

import os
import time
import hashlib


def create_and_retrieve_entry():
    # [START create_and_retrieve_entry]
    from azure.codetransparency import CodeTransparencyClient
    from azure.core.credentials import AzureKeyCredential
    from azure.core.exceptions import HttpResponseError, ResourceNotFoundError

    endpoint = os.getenv("AZURE_CODETRANSPARENCY_ENDPOINT")
    api_key = os.getenv("AZURE_CODETRANSPARENCY_API_KEY")

    if endpoint is None or api_key is None:
        raise ValueError(
            "Please set AZURE_CODETRANSPARENCY_ENDPOINT and AZURE_CODETRANSPARENCY_API_KEY environment variables"
        )

    # Create a client
    client = CodeTransparencyClient(
        endpoint=endpoint,
        credential=AzureKeyCredential(key=api_key)
    )

    # Create sample binary data (in a real scenario, this might be a compiled binary or a package)
    sample_data = b"This is a sample code artifact for transparency ledger"
    
    # Calculate SHA-256 hash of the binary data (for verification later)
    data_hash = hashlib.sha256(sample_data).hexdigest()
    print(f"Created sample data with SHA-256 hash: {data_hash}")

    # Create a new entry in the Code Transparency Service
    try:
        print("Creating entry in Code Transparency Service...")
        response = client.create_entry(body=sample_data)
        
        # The response contains information about the created entry
        entry_info = b""
        for chunk in response:
            entry_info += chunk
        
        # In a real scenario, you would parse the entry_info to get the entry ID
        # For this example, we'll use a placeholder
        entry_id = "placeholder-entry-id"
        print(f"Entry created successfully")
        
    except HttpResponseError as e:
        print(f"Failed to create entry: {e}")
        return

    # Wait a moment for the entry to be processed
    print("Waiting for entry to be processed...")
    time.sleep(5)

    # Retrieve the entry by ID
    try:
        print(f"Retrieving entry with ID: {entry_id}...")
        response = client.get_entry(entry_id=entry_id)
        
        # Process the binary response
        entry_data = b""
        for chunk in response:
            entry_data += chunk
        
        # Verify the retrieved data matches what we submitted
        retrieved_hash = hashlib.sha256(entry_data).hexdigest()
        print(f"Retrieved entry with SHA-256 hash: {retrieved_hash}")
        
        if data_hash == retrieved_hash:
            print("Verification successful: Retrieved data matches original data")
        else:
            print("Verification failed: Retrieved data does not match original data")
            
    except (HttpResponseError, ResourceNotFoundError) as e:
        print(f"Failed to retrieve entry: {e}")
    # [END create_and_retrieve_entry]


def get_service_configuration():
    # [START get_service_configuration]
    from azure.codetransparency import CodeTransparencyClient
    from azure.core.credentials import AzureKeyCredential
    from azure.core.exceptions import HttpResponseError

    endpoint = os.getenv("AZURE_CODETRANSPARENCY_ENDPOINT")
    api_key = os.getenv("AZURE_CODETRANSPARENCY_API_KEY")

    if endpoint is None or api_key is None:
        raise ValueError(
            "Please set AZURE_CODETRANSPARENCY_ENDPOINT and AZURE_CODETRANSPARENCY_API_KEY environment variables"
        )

    # Create a client
    client = CodeTransparencyClient(
        endpoint=endpoint,
        credential=AzureKeyCredential(key=api_key)
    )

    # Get the transparency service configuration in CBOR format
    try:
        print("Getting transparency service configuration...")
        response = client.get_transparency_config_cbor()
        
        # Process the binary response
        config_data = b""
        for chunk in response:
            config_data += chunk
        
        print(f"Retrieved {len(config_data)} bytes of configuration data")
        
        # In a real scenario, you would parse and process the CBOR data
        # For this example, we'll just show the size of the data
        
    except HttpResponseError as e:
        print(f"Failed to get transparency configuration: {e}")
    # [END get_service_configuration]


def get_public_keys():
    # [START get_public_keys]
    from azure.codetransparency import CodeTransparencyClient
    from azure.core.credentials import AzureKeyCredential
    from azure.core.exceptions import HttpResponseError

    endpoint = os.getenv("AZURE_CODETRANSPARENCY_ENDPOINT")
    api_key = os.getenv("AZURE_CODETRANSPARENCY_API_KEY")

    if endpoint is None or api_key is None:
        raise ValueError(
            "Please set AZURE_CODETRANSPARENCY_ENDPOINT and AZURE_CODETRANSPARENCY_API_KEY environment variables"
        )

    # Create a client
    client = CodeTransparencyClient(
        endpoint=endpoint,
        credential=AzureKeyCredential(key=api_key)
    )

    # Get the public keys from the service
    try:
        print("Getting public keys...")
        response = client.get_public_keys()
        
        # The response can be either JSON or binary data
        # For this example, we'll handle both possibilities
        if hasattr(response, '__iter__') and not isinstance(response, (str, bytes, bytearray)):
            # It's an iterator of bytes
            key_data = b""
            for chunk in response:
                key_data += chunk
            print(f"Retrieved {len(key_data)} bytes of public key data")
        else:
            # It's JSON data
            print(f"Retrieved public keys: {response}")
        
    except HttpResponseError as e:
        print(f"Failed to get public keys: {e}")
    # [END get_public_keys]


if __name__ == "__main__":
    print("---Creating and retrieving an entry---")
    create_and_retrieve_entry()
    
    print("\n---Getting service configuration---")
    get_service_configuration()
    
    print("\n---Getting public keys---")
    get_public_keys()

# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: basic_sample.py

DESCRIPTION:
    This sample demonstrates basic usage of the Azure Code Transparency Service client library.

USAGE:
    python basic_sample.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_CLIENT_ID - the client ID of your Azure Active Directory application
    2) AZURE_CLIENT_SECRET - the client secret of your Azure Active Directory application
    3) AZURE_TENANT_ID - the tenant ID of your Azure Active Directory application
    4) CODE_TRANSPARENCY_ENDPOINT - the endpoint of your Code Transparency Service instance
"""

import os
from azure.identity import DefaultAzureCredential
from azure.codetransparency import CodeTransparencyClient


def main():
    """Main function demonstrating basic client usage."""
    
    # Get the Code Transparency Service endpoint from environment variable
    endpoint = os.environ.get("CODE_TRANSPARENCY_ENDPOINT")
    if not endpoint:
        raise ValueError("CODE_TRANSPARENCY_ENDPOINT environment variable must be set")

    # Create a credential object using DefaultAzureCredential
    credential = DefaultAzureCredential()

    # Create the Code Transparency Service client
    client = CodeTransparencyClient(endpoint=endpoint, credential=credential)

    print(f"Successfully created Code Transparency Service client for endpoint: {endpoint}")

    # Close the client when done
    client.close()
    print("Client closed successfully")


if __name__ == "__main__":
    main()
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_authentication.py

DESCRIPTION:
    This sample demonstrates how to authenticate the LogsIngestionClient.

    Note: This sample requires the azure-identity library.

USAGE:
    python sample_authentication.py
"""


def authenticate_public_cloud():
    # [START create_client_public_cloud]
    from azure.identity import DefaultAzureCredential
    from azure.monitor.ingestion import LogsIngestionClient

    credential = DefaultAzureCredential()
    endpoint = "https://example.ingest.monitor.azure.com"
    client = LogsIngestionClient(endpoint, credential)
    # [END create_client_public_cloud]


def authenticate_sovereign_cloud():
    # [START create_client_sovereign_cloud]
    from azure.identity import AzureAuthorityHosts, DefaultAzureCredential
    from azure.monitor.ingestion import LogsIngestionClient

    credential = DefaultAzureCredential(authority=AzureAuthorityHosts.AZURE_GOVERNMENT)
    endpoint = "https://example.ingest.monitor.azure.us"
    client = LogsIngestionClient(endpoint, credential, credential_scopes=["https://monitor.azure.us/.default"])
    # [END create_client_sovereign_cloud]


if __name__ == "__main__":
    authenticate_public_cloud()
    authenticate_sovereign_cloud()

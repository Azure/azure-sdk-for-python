# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Code snippets demonstrating how to create various credentials."""


def create_azure_developer_cli_credential():
    # [START azure_developer_cli_credential]
    from azure.identity import AzureDeveloperCliCredential

    credential = AzureDeveloperCliCredential()
    # [END azure_developer_cli_credential]


def create_azure_developer_cli_credential_async():
    # [START azure_developer_cli_credential_async]
    from azure.identity.aio import AzureDeveloperCliCredential

    credential = AzureDeveloperCliCredential()
    # [END azure_developer_cli_credential_async]


def create_workload_identity_credential():
    # [START workload_identity_credential]
    from azure.identity import WorkloadIdentityCredential

    credential = WorkloadIdentityCredential(
        tenant_id="<tenant_id>",
        client_id="<client_id>",
        file="<token_file_path>"
    )

    # Parameters can be omitted if the following environment variables are set:
    #   - AZURE_TENANT_ID
    #   - AZURE_CLIENT_ID
    #   - AZURE_FEDERATED_TOKEN_FILE
    credential = WorkloadIdentityCredential()
    # [END workload_identity_credential]


def create_workload_identity_credential_async():
    # [START workload_identity_credential_async]
    from azure.identity.aio import WorkloadIdentityCredential

    credential = WorkloadIdentityCredential(
        tenant_id="<tenant_id>",
        client_id="<client_id>",
        file="<token_file_path>"
    )

    # Parameters can be omitted if the following environment variables are set:
    #   - AZURE_TENANT_ID
    #   - AZURE_CLIENT_ID
    #   - AZURE_FEDERATED_TOKEN_FILE
    credential = WorkloadIdentityCredential()
    # [END workload_identity_credential_async]

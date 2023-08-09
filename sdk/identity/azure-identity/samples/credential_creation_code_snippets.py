# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Code snippets demonstrating how to create various credentials."""


def create_authorization_code_credential():
    # [START create_authorization_code_credential]
    from azure.identity import AuthorizationCodeCredential

    credential = AuthorizationCodeCredential(
        tenant_id="<tenant_id>",
        client_id="<client_id>",
        authorization_code="<auth_code>",
        redirect_uri="<redirect_uri>",
    )
    # [END create_authorization_code_credential]


async def create_authorization_code_credential_async():
    # [START create_authorization_code_credential_async]
    from azure.identity.aio import AuthorizationCodeCredential

    credential = AuthorizationCodeCredential(
        tenant_id="<tenant_id>",
        client_id="<client_id>",
        authorization_code="<auth_code>",
        redirect_uri="<redirect_uri>",
    )
    # [END create_authorization_code_credential_async]


def create_azure_cli_credential():
    # [START create_azure_cli_credential]
    from azure.identity import AzureCliCredential

    credential = AzureCliCredential()
    # [END create_azure_cli_credential]


async def create_azure_cli_credential_async():
    # [START create_azure_cli_credential_async]
    from azure.identity.aio import AzureCliCredential

    credential = AzureCliCredential()
    # [END create_azure_cli_credential_async]


def create_azure_developer_cli_credential():
    # [START azure_developer_cli_credential]
    from azure.identity import AzureDeveloperCliCredential

    credential = AzureDeveloperCliCredential()
    # [END azure_developer_cli_credential]


async def create_azure_developer_cli_credential_async():
    # [START azure_developer_cli_credential_async]
    from azure.identity.aio import AzureDeveloperCliCredential

    credential = AzureDeveloperCliCredential()
    # [END azure_developer_cli_credential_async]


def create_azure_power_shell_credential():
    # [START create_azure_power_shell_credential]
    from azure.identity import AzurePowerShellCredential

    credential = AzurePowerShellCredential()
    # [END create_azure_power_shell_credential]


async def create_azure_power_shell_credential_async():
    # [START create_azure_power_shell_credential_async]
    from azure.identity.aio import AzurePowerShellCredential

    credential = AzurePowerShellCredential()
    # [END create_azure_power_shell_credential_async]


def create_certificate_credential():
    # [START create_certificate_credential]
    from azure.identity import CertificateCredential

    credential = CertificateCredential(
        tenant_id="<tenant_id>",
        client_id="<client_id>",
        certificate_path="<path to PEM/PKCS12 certificate>",
        password="<certificate password if necessary>",
    )

    # Certificate/private key byte data can also be passed directly
    credential = CertificateCredential(
        tenant_id="<tenant_id>",
        client_id="<client_id>",
        certificate_data=b"<cert data>",
    )
    # [END create_certificate_credential]


async def create_certificate_credential_async():
    # [START create_certificate_credential_async]
    from azure.identity.aio import CertificateCredential

    credential = CertificateCredential(
        tenant_id="<tenant_id>",
        client_id="<client_id>",
        certificate_path="<path to PEM/PKCS12 certificate>",
        password="<certificate password if necessary>",
    )

    # Certificate/private key byte data can also be passed directly
    credential = CertificateCredential(
        tenant_id="<tenant_id>",
        client_id="<client_id>",
        certificate_data=b"<cert data>",
    )
    # [END create_certificate_credential_async]


def create_chained_token_credential():
    # [START create_chained_token_credential]
    from azure.identity import ChainedTokenCredential, EnvironmentCredential, AzureCliCredential

    credential_chain = (
        # Try EnvironmentCredential first
        EnvironmentCredential(),
        # Fallback to Azure CLI if EnvironmentCredential fails
        AzureCliCredential(),
    )
    credential = ChainedTokenCredential(*credential_chain)
    # [END create_chained_token_credential]


async def create_chained_token_credential_async():
    # [START create_chained_token_credential_async]
    from azure.identity.aio import ChainedTokenCredential, EnvironmentCredential, AzureCliCredential

    credential_chain = (
        # Try EnvironmentCredential first
        EnvironmentCredential(),
        # Fallback to Azure CLI if EnvironmentCredential fails
        AzureCliCredential(),
    )
    credential = ChainedTokenCredential(*credential_chain)
    # [END create_chained_token_credential_async]


def create_client_assertion_credential():
    # [START create_client_assertion_credential]
    from azure.identity import ClientAssertionCredential

    def get_assertion():
        return "<client-assertion>"

    credential = ClientAssertionCredential(
        tenant_id="<tenant_id>",
        client_id="<client_id>",
        func=get_assertion,
    )
    # [END create_client_assertion_credential]


async def create_client_assertion_credential_async():
    # [START create_client_assertion_credential_async]
    from azure.identity.aio import ClientAssertionCredential

    def get_assertion():
        return "<client-assertion>"

    credential = ClientAssertionCredential(
        tenant_id="<tenant_id>",
        client_id="<client_id>",
        func=get_assertion,
    )
    # [END create_client_assertion_credential_async]


def create_client_secret_credential():
    # [START create_client_secret_credential]
    from azure.identity import ClientSecretCredential

    credential = ClientSecretCredential(
        tenant_id="<tenant_id>",
        client_id="<client_id>",
        client_secret="<client_secret>",
    )
    # [END create_client_secret_credential]


async def create_client_secret_credential_async():
    # [START create_client_secret_credential_async]
    from azure.identity.aio import ClientSecretCredential

    credential = ClientSecretCredential(
        tenant_id="<tenant_id>",
        client_id="<client_id>",
        client_secret="<client_secret>",
    )
    # [END create_client_secret_credential_async]


def create_default_credential():
    # [START create_default_credential]
    from azure.identity import DefaultAzureCredential

    credential = DefaultAzureCredential()
    # [END create_default_credential]


async def create_default_credential_async():
    # [START create_default_credential_async]
    from azure.identity.aio import DefaultAzureCredential

    credential = DefaultAzureCredential()
    # [END create_default_credential_async]


def create_device_code_credential():
    # [START create_device_code_credential]
    from azure.identity import DeviceCodeCredential

    credential = DeviceCodeCredential()
    # [END create_device_code_credential]


def create_environment_credential():
    # [START create_environment_credential]
    from azure.identity import EnvironmentCredential

    credential = EnvironmentCredential()
    # [END create_environment_credential]


async def create_environment_credential_async():
    # [START create_environment_credential_async]
    from azure.identity.aio import EnvironmentCredential

    credential = EnvironmentCredential()
    # [END create_environment_credential_async]


def create_interactive_browser_credential():
    # [START create_interactive_browser_credential]
    from azure.identity import InteractiveBrowserCredential

    credential = InteractiveBrowserCredential(
        client_id="<client_id>",
    )
    # [END create_interactive_browser_credential]


def create_managed_identity_credential():
    # [START create_managed_identity_credential]
    from azure.identity import ManagedIdentityCredential

    credential = ManagedIdentityCredential()

    # Can also specify a client ID of a user-assigned managed identity
    credential = ManagedIdentityCredential(
        client_id="<client_id>",
    )
    # [END create_managed_identity_credential]


async def create_managed_identity_credential_async():
    # [START create_managed_identity_credential_async]
    from azure.identity.aio import ManagedIdentityCredential

    credential = ManagedIdentityCredential()

    # Can also specify a client ID of a user-assigned managed identity
    credential = ManagedIdentityCredential(
        client_id="<client_id>",
    )
    # [END create_managed_identity_credential_async]


def create_on_behalf_of_credential():
    # [START create_on_behalf_of_credential]
    from azure.identity import OnBehalfOfCredential

    credential = OnBehalfOfCredential(
        tenant_id="<tenant_id>",
        client_id="<client_id>",
        client_secret="<client_secret>",
        user_assertion="<access_token>",
    )
    # [END create_on_behalf_of_credential]


async def create_on_behalf_of_credential_async():
    # [START create_on_behalf_of_credential_async]
    from azure.identity.aio import OnBehalfOfCredential

    credential = OnBehalfOfCredential(
        tenant_id="<tenant_id>",
        client_id="<client_id>",
        client_secret="<client_secret>",
        user_assertion="<access_token>",
    )
    # [END create_on_behalf_of_credential_async]


def create_username_password_credential():
    # [START create_username_password_credential]
    from azure.identity import UsernamePasswordCredential

    credential = UsernamePasswordCredential(
        client_id="<client_id>",
        username="<username>",
        password="<password>",
    )
    # [END create_username_password_credential]


def create_workload_identity_credential():
    # [START workload_identity_credential]
    from azure.identity import WorkloadIdentityCredential

    credential = WorkloadIdentityCredential(
        tenant_id="<tenant_id>",
        client_id="<client_id>",
        token_file_path="<token_file_path>",
    )

    # Parameters can be omitted if the following environment variables are set:
    #   - AZURE_TENANT_ID
    #   - AZURE_CLIENT_ID
    #   - AZURE_FEDERATED_TOKEN_FILE
    credential = WorkloadIdentityCredential()
    # [END workload_identity_credential]


async def create_workload_identity_credential_async():
    # [START workload_identity_credential_async]
    from azure.identity.aio import WorkloadIdentityCredential

    credential = WorkloadIdentityCredential(
        tenant_id="<tenant_id>",
        client_id="<client_id>",
        token_file_path="<token_file_path>",
    )

    # Parameters can be omitted if the following environment variables are set:
    #   - AZURE_TENANT_ID
    #   - AZURE_CLIENT_ID
    #   - AZURE_FEDERATED_TOKEN_FILE
    credential = WorkloadIdentityCredential()
    # [END workload_identity_credential_async]

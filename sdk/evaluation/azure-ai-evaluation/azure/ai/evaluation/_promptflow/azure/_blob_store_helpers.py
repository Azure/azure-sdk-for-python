# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import os
from typing import cast, NamedTuple, Union, Final
from urllib.parse import quote

from azure.ai.evaluation._evaluate._utils import AzureMLWorkspace
from azure.ai.evaluation._exceptions import ErrorBlame, ErrorCategory, ErrorTarget, EvaluationException
from azure.ai.evaluation._http_utils import get_http_client
from azure.ai.evaluation.simulator._model_tools._identity_manager import TokenScope
from azure.core.credentials import AzureSasCredential
from azure.identity import (
    AzureCliCredential, 
    DefaultAzureCredential,
    ManagedIdentityCredential,
    ChainedTokenCredential
)


class BlobStoreInfo(NamedTuple):
    account_name: str
    endpoint: str
    container_name: str
    credentials: AzureSasCredential


def _get_workspace_from_trace_string(trace_destination: str) -> AzureMLWorkspace:
    """ Extracts the subscription ID, resource group name, and AI workspace name from the specified
        trace destination string. If the values are not found in the trace destination string, the
        values are extracted from the local configuration JSON, or environment variables."""
    
    from promptflow._cli._utils import get_workspace_triad_from_local
    from azure.ai.evaluation._evaluate._utils import extract_workspace_triad_from_trace_provider

    subscription_id, resource_group, workspace_name = extract_workspace_triad_from_trace_provider(trace_destination)

    if not(subscription_id and resource_group and workspace_name):
        local = get_workspace_triad_from_local()
        subscription_id = cast(str, subscription_id or local.subscription_id or os.getenv("AZUREML_ARM_WORKSPACE_NAME"))
        resource_group = cast(str, resource_group or local.resource_group_name or os.getenv("AZUREML_ARM_SUBSCRIPTION"))
        workspace_name = cast(str, workspace_name or local.workspace_name or os.getenv("AZUREML_ARM_RESOURCEGROUP"))
    
    return AzureMLWorkspace(subscription_id, resource_group, workspace_name)

def _get_workspace_credentials() -> Union[AzureCliCredential, ManagedIdentityCredential, ChainedTokenCredential]:
    """ Returns the Azure credentials for the Azure Machine Learning workspace. """
    
    from promptflow._utils.logger_utils import get_cli_sdk_logger
    # TODO ralphe: Do we need AzureMLOnBehalfOfCredential?
    #from azure.ai.ml.identity import AzureMLOnBehalfOfCredential

    logger = get_cli_sdk_logger()

    # if os.getenv("AZUREML_OBO_ENABLED"):
    #     logger.debug("User identity is configured, use OBO credential.")
    #     credential = AzureMLOnBehalfOfCredential()
    if os.environ.get("PF_USE_AZURE_CLI_CREDENTIAL", "false").lower() == "true":
        logger.debug("Use azure cli credential since specified in environment variable.")
        credential = AzureCliCredential()
    else:
        client_id_from_env = os.getenv("DEFAULT_IDENTITY_CLIENT_ID")
        if client_id_from_env:
            # use managed identity when client id is available from environment variable.
            # reference code:
            # https://learn.microsoft.com/en-us/azure/machine-learning/how-to-identity-based-service-authentication?tabs=cli#compute-cluster
            logger.debug("Use managed identity credential.")
            credential = ManagedIdentityCredential(client_id=client_id_from_env)
        elif os.environ.get("IS_IN_CI_PIPELINE", "false").lower() == "true":
            # use managed identity when executing in CI pipeline.
            logger.debug("Use azure cli credential since in CI pipeline.")
            credential = AzureCliCredential()
        else:
            # use default Azure credential to handle other cases.
            logger.debug("Use default credential.")
            credential = DefaultAzureCredential()

    return credential

def get_workspace_default_blob_store(trace_destination: str) -> BlobStoreInfo:
    """ Returns the default blob store for the specified Azure Machine Learning workspace
        by parsing the trace destination string. """

    API_VERSION_KEY: Final[str] = "api-version"
    API_VERSION: Final[str] = "2024-10-01"

    subscription_id, resource_group, workspace_name = _get_workspace_from_trace_string(trace_destination)
    subscription_id = quote(subscription_id, safe='')
    resource_group = quote(resource_group, safe='')
    workspace_name = quote(workspace_name, safe='')

    base_url = f"https://management.azure.com/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/Microsoft.MachineLearningServices/workspaces/{workspace_name}/datastores"

    credential = _get_workspace_credentials()
    # TODO ralphe: use the APITokenManager to cache this token
    access_token = credential.get_token(TokenScope.DEFAULT_AZURE_MANAGEMENT.value)
    headers = {
        "Authorization": f"Bearer {access_token.token}",
        "Content-Type": "application/json"
    }

    http_client = get_http_client()

    # 1. Get the default blob store
    stores_response = http_client.request(
        "GET",
        base_url,
        params={
            API_VERSION_KEY: API_VERSION,
            "isDefault": "true",
            "count": 1,
            "orderByAsc": "false"
        },
        headers=headers
    )
    stores_response.raise_for_status() # TODO ralphe: should we raise a different exception here?

    # TODO is this always the first one?
    first_store_props = stores_response.json()["value"][0]["properties"]
    account_name = first_store_props["accountName"]
    endpoint = first_store_props["endpoint"]
    container_name = first_store_props["containerName"]

    # 2. Get the SAS token to use for accessing the blob store
    secrets_response = http_client.request(
        "POST",
        base_url + "/workspaceblobstore/listSecrets",
        params={
            API_VERSION_KEY: API_VERSION
        },
        headers=headers
    )
    secrets_response.raise_for_status() # TODO ralphe: should we raise a different exception here?

    secrets_json = secrets_response.json()
    cred_type = secrets_json["secretsType"]

    if cred_type.lower() != "sas":
        # TODO ralphe: assume this is an AccountKeyConfiguration? or AccountKeyToken?
        raise EvaluationException(
            message=f"The '{account_name}' blob store does not use a SAS token.",
            internal_message=f"The credential type is '{cred_type}'",
            target=ErrorTarget.EVALUATE,
            category=ErrorCategory.INVALID_VALUE,
            blame=ErrorBlame.SYSTEM_ERROR
        )
    
    blob_store_credential = AzureSasCredential(secrets_json["sasToken"])

    return BlobStoreInfo(account_name, endpoint, container_name, blob_store_credential)

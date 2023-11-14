# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Azure OpenAI deployment related utils."""
import openai
from azure.core.credentials import AzureKeyCredential
from azure.ai.generative.index._utils.connections import (
    connection_to_credential,
    get_metadata_from_connection,
    get_target_from_connection,
)
from openai.api_resources.deployment import Deployment
from openai.util import convert_to_dict


def infer_deployment(aoai_connection, model_name):
    """Infer deployment name in an AOAI connection, given model name."""
    if model_name is None or model_name == "":
        raise ValueError("Parameter 'model_name' has no value. Deployment inferring cannot be performed.")
    connection_metadata = get_metadata_from_connection(aoai_connection)
    openai.api_type = connection_metadata.get("ApiType", connection_metadata.get("apiType", "azure"))
    openai.api_version = connection_metadata.get(
        "ApiVersion", connection_metadata.get("apiVersion", "2023-03-15-preview")
    )
    openai.api_base = get_target_from_connection(aoai_connection)
    credential = connection_to_credential(aoai_connection)
    openai.api_key = credential.key if isinstance(credential, AzureKeyCredential) else credential.get_token().token
    deployment_list = convert_to_dict(
        Deployment.list(api_key=openai.api_key, api_base=openai.api_base, api_type=openai.api_type)
    )
    for deployment in deployment_list["data"]:
        if deployment["model"] == model_name:
            return deployment["id"]
    raise Exception(
        f"Deployment for model={model_name} not found in AOAI workspace. Please retry with correct model name or create a deployment."
    )

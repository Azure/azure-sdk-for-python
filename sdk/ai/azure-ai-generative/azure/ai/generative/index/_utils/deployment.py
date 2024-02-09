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
from packaging import version


def infer_deployment(aoai_connection, model_name):
    """Infer deployment name in an AOAI connection, given model name."""
    if model_name is None or model_name == "":
        raise ValueError("Parameter 'model_name' has no value. Deployment inferring cannot be performed.")
    connection_metadata = get_metadata_from_connection(aoai_connection)
    openai.api_type = connection_metadata.get("ApiType", connection_metadata.get("apiType", "azure"))
    openai.api_version = connection_metadata.get(
        "ApiVersion", connection_metadata.get("apiVersion", "2023-03-15-preview")
    )
    api_base = get_target_from_connection(aoai_connection)
    if hasattr(openai, "api_base"):
        openai.api_base = api_base
    else:
        openai.base_url = api_base
    credential = connection_to_credential(aoai_connection)
    openai.api_key = credential.key if isinstance(credential, AzureKeyCredential) else credential.get_token().token

    if version.parse(openai.version.VERSION) >= version.parse("1.0.0"):
        from openai.resources import Deployment
    else:
        from openai.api_resources.deployment import Deployment

    deployment_list = convert_to_dict(
        Deployment.list(api_key=openai.api_key, api_base=api_base, api_type=openai.api_type)
    )
    for deployment in deployment_list["data"]:
        if deployment["model"] == model_name:
            return deployment["id"]
    raise Exception(
        f"Deployment for model={model_name} not found in AOAI workspace. Please retry with correct model name or create a deployment."
    )

def convert_to_dict(obj: object) -> dict:
    """
    Converts a OpenAIObject back to a regular dict.

    Nested OpenAIObjects are also converted back to regular dicts.

    :param obj: The OpenAIObject to convert.

    :returns: The OpenAIObject as a dict.
    """
    if isinstance(obj, list):
        return [convert_to_dict(i) for i in obj]
    # This works by virtue of the fact that OpenAIObjects _are_ dicts. The dict
    # comprehension returns a regular dict and recursively applies the
    # conversion to each value.
    elif isinstance(obj, dict):
        return {k: convert_to_dict(v) for k, v in obj.items()}
    else:
        return obj

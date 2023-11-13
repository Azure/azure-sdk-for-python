# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Azure OpenAI deployment related utils"""
from openai.api_resources.deployment import Deployment
import openai
from openai.util import convert_to_dict


def infer_deployment(aoai_connection, model_name):
    """Infer deployment name in an AOAI connection, given model name."""
    if "properties" not in aoai_connection:
        raise ValueError("Parameter 'aoai_connection' is not populated correctly. Deployment inferring cannot be performed.")
    if model_name is None or model_name == "":
        raise ValueError("Parameter 'model_name' has no value. Deployment inferring cannot be performed.")
    connection_metadata = aoai_connection.get('properties', {}).get('metadata', {})
    openai.api_type = connection_metadata.get("ApiType", connection_metadata.get("apiType", "azure"))
    openai.api_version = connection_metadata.get('ApiVersion', connection_metadata.get('apiVersion', '2023-03-15-preview'))
    openai.api_base = aoai_connection.get('properties', {}).get('target')
    openai.api_key = aoai_connection.get('properties', {}).get('credentials').get("key")
    deployment_list = convert_to_dict(Deployment.list(api_key=openai.api_key, api_base=openai.api_base, api_type=openai.api_type))
    for deployment in deployment_list["data"]:
        if deployment["model"] == model_name:
            return deployment["id"]
    raise Exception(f"Deployment for model={model_name} not found in AOAI workspace. Please retry with correct model name or create a deployment.")

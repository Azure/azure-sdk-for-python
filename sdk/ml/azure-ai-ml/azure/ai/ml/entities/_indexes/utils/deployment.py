# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Azure OpenAI deployment related utils."""

import openai
from azure.core.credentials import AzureKeyCredential
from azure.ai.ml.entities._indexes.utils.connections import (
    connection_to_credential,
    get_metadata_from_connection,
    get_target_from_connection,
)
from azure.ai.ml.entities._indexes.utils.logging import get_logger
from packaging import version

logger = get_logger("utils.deployment")


def _split_resource_id(resource_id, start):
    resource_id = resource_id.split("/")
    dets = {}
    for i in range(start, len(resource_id), 2):
        dets[resource_id[i]] = resource_id[i + 1]
    return dets


def _get_deployment_from_id(deployment_id):
    if deployment_id.find("/deployments/") == -1:
        raise ValueError("Cannot parse deployment name from deployment_id.")
    return deployment_id[deployment_id.find("/deployments/") + len("/deployments/") :]


def infer_deployment(aoai_connection, model_name):
    """Infer deployment names in an AOAI connection, given model name."""
    if model_name is None or model_name == "":
        raise ValueError("Parameter 'model_name' has no value. Deployment inferring cannot be performed.")
    connection_metadata = get_metadata_from_connection(aoai_connection)
    openai.api_type = connection_metadata.get("ApiType", connection_metadata.get("apiType", "azure"))
    openai.api_version = connection_metadata.get(
        "ApiVersion", connection_metadata.get("apiVersion", "2023-03-15-preview")
    )
    resource_id = connection_metadata.get("ResourceId", aoai_connection["id"])
    if resource_id is None:
        raise ValueError("Could not fetch resource_id from aoai_connection.")

    workspace_details = _split_resource_id(resource_id, start=1)
    try:
        subscription_id = workspace_details["subscriptions"]
    except Exception as e:
        raise ValueError("Could not parse subscriptions from workspace_details") from e
    try:
        resource_group = workspace_details["resourceGroups"]
    except Exception as e:
        raise ValueError("Could not parse resourceGroups from workspace_details") from e
    aoai_name = workspace_details.get("accounts", None)
    if aoai_name is None:
        try:
            target = aoai_connection["properties"]["target"]
        except Exception as e:
            raise ValueError("Could not parse target from aoai_connection") from e
        try:
            aoai_name = target[target.find("https://") + len("https://") : target.find(".openai.azure.com")]
        except Exception as e:
            raise ValueError('Could not parse aoai name from aoai_connection["properties"]["target"]') from e
        if aoai_name is None:
            raise ValueError("Could not fetch aoai_name from aoai_connection.")

    print(f"subscription_id is {subscription_id}, resource_group is {resource_group}, aoai_name is {aoai_name}")

    api_base = get_target_from_connection(aoai_connection)
    if hasattr(openai, "api_base"):
        openai.api_base = api_base
    else:
        openai.base_url = api_base

    credential = connection_to_credential(aoai_connection, data_plane=True)
    openai.api_key = credential.key if isinstance(credential, AzureKeyCredential) else credential.get_token().token

    if version.parse(openai.version.VERSION) >= version.parse("1.0.0"):
        try:
            from azure.mgmt.cognitiveservices import CognitiveServicesManagementClient
        except ImportError as e:
            raise ValueError(
                "Could not import azure-mgmt-cognitiveservices python package. "
                "Please install it with `pip install azure-mgmt-cognitiveservices`."
            ) from e
        try:
            from azure.identity import DefaultAzureCredential
        except ImportError as e:
            raise ValueError(
                "Could not import azure-identity python package. "
                "Please install it with `pip install azure-identity`."
            ) from e
        print(
            f"calling cognitive service with subscription_id is {subscription_id}, resource_group is {resource_group}, aoai_name is {aoai_name}"
        )
        client = CognitiveServicesManagementClient(
            credential=DefaultAzureCredential(process_timeout=60), subscription_id=subscription_id
        )
        deployment_list = convert_to_dict(
            client.deployments.list(resource_group_name=resource_group, account_name=aoai_name)
        )
        result = []
        for deployment in deployment_list:
            if deployment.name == model_name:
                result.append(_get_deployment_from_id(deployment.id))
    else:  # This doesn't seem to work, please ask customers to use openai v1
        logger.warning("infer_deployment() might fail with openai v0.x")
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
    from collections.abc import Iterable

    if isinstance(obj, list):
        return [convert_to_dict(i) for i in obj]
    # This works by virtue of the fact that OpenAIObjects _are_ dicts. The dict
    # comprehension returns a regular dict and recursively applies the
    # conversion to each value.
    elif isinstance(obj, dict):
        return {k: convert_to_dict(v) for k, v in obj.items()}
    elif isinstance(obj, Iterable):
        return [convert_to_dict(i) for i in obj]
    else:
        return obj

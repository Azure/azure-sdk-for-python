# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Language model classes."""

import copy
import json
import os
import requests
import logging
from typing import Optional

from azure.core.credentials import TokenCredential
from azure.ai.ml.entities._indexes.utils.connections import (
    connection_to_credential,
    get_connection_by_id_v2,
    get_connection_credential,
)

logger = logging.getLogger(__name__)


def init_open_ai_from_config(config: dict, credential: Optional[TokenCredential] = None) -> dict:
    """Initialize an OpenAI model from a configuration dictionary."""
    import openai

    logger.debug("OpenAI arguments: \n")
    logger.debug(
        "\n".join(f"{k}={v}" if k != "key" and k != "api_key" else f"{k}=[REDACTED]" for k, v in config.items())
    )

    try:
        if config.get("key") is not None:
            config["api_key"] = config.get("key")
        elif "connection_type" not in config:
            if config.get("api_key") is None:
                config["api_key"] = os.environ.get("OPENAI_API_KEY", None)
            if config["api_key"] is None and "azure" in config["api_type"]:
                from azure.identity import DefaultAzureCredential

                credential = DefaultAzureCredential(process_timeout=60) if credential is None else credential
                config["api_key"] = credential.get_token("https://cognitiveservices.azure.com/.default").token
                config["api_type"] = "azure_ad"
        else:
            if config["connection_type"] == "workspace_connection":
                connection_id = config.get("connection", {}).get("id", "")
                connection = get_connection_by_id_v2(connection_id, credential=credential)
                # Only change base, version, and type in AOAI case
                if hasattr(connection, "type"):
                    if connection.type == "azure_open_ai":
                        config["api_base"] = connection.target[:-1] if connection.target.endswith("/") else connection.target
                        config["api_version"] = (
                            connection.api_version
                            if hasattr(connection, "api_version") and connection.api_version is not None
                            else "2023-03-15-preview"
                        )
                        config["api_type"] = (
                            connection.api_type
                            if hasattr(connection, "api_type") and connection.api_type is not None
                            else "azure"
                        )
                elif (
                    isinstance(connection, dict)
                    and connection.get("properties", {}).get("category", None) == "AzureOpenAI"
                ):
                    config["api_base"] = connection.get("properties", {}).get("target")
                    connection_metadata = connection.get("properties", {}).get("metadata", {})
                    config["api_version"] = connection_metadata.get(
                        "apiVersion", connection_metadata.get("ApiVersion", "2023-03-15-preview")
                    )
                    config["api_type"] = connection_metadata.get(
                        "apiType", connection_metadata.get("ApiType", "azure")
                    ).lower()

                if config["api_type"] == "azure_ad" or config["api_type"] == "azuread":
                    from azure.identity import DefaultAzureCredential

                    credential = DefaultAzureCredential(process_timeout=60) if credential is None else credential
                else:
                    credential = connection_to_credential(connection, data_plane=True)
            else:
                credential = get_connection_credential(config, data_plane=True)

            if not hasattr(credential, "key"):
                # Add hack to check for "BAKER-OPENAI-API-KEY"
                if config.get("connection_type", "workspace_keyvault") == "workspace_keyvault":
                    new_args = copy.deepcopy(config)
                    new_args["connection"]["key"] = "BAKER-OPENAI-API-KEY"
                    credential = get_connection_credential(new_args)

            if hasattr(credential, "key"):
                config["api_key"] = credential.key
            else:
                config["api_type"] = "azure_ad"
                if callable(credential):
                    config["azure_ad_token_provider"] = credential
                else:
                    config["api_key"] = credential.get_token("https://cognitiveservices.azure.com/.default").token
    except Exception as e:
        if "OPENAI_API_KEY" in os.environ:
            logger.warning(f"Failed to get credential for ACS with {e}, falling back to env vars.")
            config["api_key"] = os.environ["OPENAI_API_KEY"]
            config["api_type"] = os.environ.get("OPENAI_API_TYPE", "azure")
            config["api_base"] = os.environ.get(
                "OPENAI_API_BASE", openai.api_base if hasattr(openai, "api_base") else openai.base_url
            )
            config["api_version"] = os.environ.get("OPENAI_API_VERSION", openai.api_version)
        else:
            raise e

    if isinstance(openai.api_type, str) and "azure" in openai.api_type:
        config["api_version"] = config.get("api_version", "2023-03-15-preview")

    return config


def init_serverless_from_config(config: dict, credential: Optional[TokenCredential] = None) -> dict:
    """Initialize an Serverless model from a configuration dictionary."""
    logger.debug("Serverless connection arguments: \n")
    logger.debug(
        "\n".join(f"{k}={v}" if k != "key" and k != "api_key" else f"{k}=[REDACTED]" for k, v in config.items())
    )

    if "connection" not in config and "endpoint" not in config:
        raise ValueError("Expected either a connection or an endpoint in the embedding config, found neither.")

    if "endpoint" in config:
        # The embedding config doesn't specify a connection, but does specify a serverless endpoint instead.
        endpoint_id = config.get("endpoint", {}).get("id", "")
        if credential is None:
            from azure.identity import DefaultAzureCredential
            credential = DefaultAzureCredential()

        auth_header = f'Bearer {credential.get_token("https://management.azure.com/.default").token}'
        endpoint = requests.get(
            f'https://management.azure.com{endpoint_id}?api-version=2024-01-01-preview',
            headers={'Authorization': auth_header}
        ).json()
        endpoint_keys = requests.post(
            f'https://management.azure.com{endpoint_id}/listKeys?api-version=2024-01-01-preview',
            headers={'Authorization': auth_header},
        ).json()

        api_base = endpoint.get("properties", {}).get("inferenceEndpoint", {}).get("uri").rstrip("/")

        config["api_type"] = "serverless"
        config["api_base"] = f"{api_base}/v1"
        config["api_key"] = endpoint_keys.get("primaryKey")

        try:
            # Best-effort model name retrieval
            info_response = requests.get(f"{api_base}/info", headers={"Authorization": f"Bearer {endpoint_keys.get('primaryKey')}"})
            info_response.raise_for_status()
            info_json = info_response.json()
            config["model"] = info_json.get("model_name") or info_json.get("served_model_name") or "generic_embed"
        except Exception:
            config["model"] = "generic_embed"

    elif config.get("connection_type", "").lower() == "workspace_connection":
        # The embedding config specifies a workspace connection to a serverless endpoint.
        connection_id = config.get("connection", {}).get("id", "")
        connection = get_connection_by_id_v2(connection_id, credential=credential)

        if hasattr(connection, "type") and connection.type == "serverless":
            api_base = connection.target.rstrip("/")
            config["api_base"] = f"{api_base}/v1"
            if hasattr(connection, "metadata"):
                config["api_type"] = "serverless"
                config["model"] = connection.metadata.get("model_name") or connection.metadata.get("served_model_name") or "generic_embed"
        elif (
            isinstance(connection, dict)
            and connection.get("properties", {}).get("category", None) == "Serverless"
        ):
            api_base = connection.get("properties", {}).get("target").rstrip("/")
            config["api_base"] = f"{api_base}/v1"
            connection_metadata = connection.get("properties", {}).get("metadata", {})
            config["api_type"] = "serverless"
            config["model"] = connection_metadata.get("model_name") or connection_metadata.get("served_model_name") or "generic_embed"
        else:
            raise ValueError(f"Malformed workspace connection response for connection {connection_id}")

        connection_credentials = connection_to_credential(connection)
        config["api_key"] = connection_credentials.key

    else:
        raise ValueError("Unknown connection type " + config.get("connection_type"))

    return config

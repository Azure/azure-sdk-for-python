# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Language model classes."""
import copy
import json
import os
from typing import Optional

from azure.core.credentials import TokenCredential
from azure.ai.resources._index._utils.connections import (
    connection_to_credential,
    get_connection_by_id_v2,
    get_connection_credential,
)
from azure.ai.resources._index._utils.logging import get_logger

logger = get_logger(__name__)


def parse_model_uri(uri: str, **kwargs) -> dict:
    """Parse a model URI into a dictionary of configuration parameters."""
    scheme, details = uri.split("://")

    def split_details(details):
        details = details.split("/")
        details_dict = {}
        for i in range(0, len(details), 2):
            details_dict[details[i]] = details[i + 1]
        return details_dict

    config = {**kwargs}
    if scheme == "azure_open_ai":
        config = {**split_details(details), **config}
        config["kind"] = "open_ai"
        if "endpoint" in config:
            if ".openai." in config["endpoint"] or ".api.cognitive." in config["endpoint"]:
                config["api_base"] = config["endpoint"].rstrip("/")
            else:
                config["api_base"] = f"https://{config['endpoint']}.openai.azure.com"
        config["api_type"] = "azure"
        config["api_version"] = kwargs.get("api_version") if kwargs.get("api_version") is not None else "2023-03-15-preview"
        # Azure OpenAI has a batch_size limit of 16
        if "batch_size" not in config:
            config["batch_size"] = "16"
    elif scheme == "open_ai":
        config["kind"] = "open_ai"
        config = {**split_details(details), **config}
        config["api_type"] = "open_ai"
    elif scheme == "hugging_face":
        config["kind"] = "hugging_face"
        config["model"] = details.split("model/")[1]
    elif scheme == "none":
        config["kind"] = "none"
    else:
        raise ValueError(f"Unknown model kind: {scheme}")

    return config


def init_open_ai_from_config(config: dict, credential: Optional[TokenCredential]) -> dict:
    """Initialize an OpenAI model from a configuration dictionary."""
    import openai

    logger.debug("OpenAI arguments: \n")
    logger.debug("\n".join(f"{k}={v}" if k != "key" and k != "api_key" else f"{k}=[REDACTED]" for k, v in config.items()))

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
                        config["api_base"] = getattr(connection, "target", None)
                        connection_metadata = getattr(connection, "metadata", {})
                        config["api_version"] = connection_metadata.get("apiVersion", connection_metadata.get("ApiVersion", "2023-07-01-preview"))
                        config["api_type"] = connection_metadata.get("apiType", connection_metadata.get("ApiType", "azure")).lower()
                elif isinstance(connection, dict) and connection.get("properties", {}).get("category", None) == "AzureOpenAI":
                    config["api_base"] = connection.get("properties", {}).get("target")
                    connection_metadata = connection.get("properties", {}).get("metadata", {})
                    config["api_version"] = connection_metadata.get("apiVersion", connection_metadata.get("ApiVersion", "2023-03-15-preview"))
                    config["api_type"] = connection_metadata.get("apiType", connection_metadata.get("ApiType", "azure")).lower()

                if config["api_type"] == "azure_ad" or config["api_type"] == "azuread":
                    from azure.identity import DefaultAzureCredential

                    credential = DefaultAzureCredential(process_timeout=60) if credential is None else credential
                else:
                    credential = connection_to_credential(connection)
            else:
                credential = get_connection_credential(config)

            if not hasattr(credential, "key"):
                # Add hack to check for "BAKER-OPENAI-API-KEY"
                if config.get("connection_type", "workspace_keyvault") == "workspace_keyvault":
                    new_args = copy.deepcopy(config)
                    new_args["connection"]["key"] = "BAKER-OPENAI-API-KEY"
                    credential = get_connection_credential(new_args)

            if hasattr(credential, "key"):
                config["api_key"] = credential.key
            else:
                config["api_key"] = credential.get_token("https://cognitiveservices.azure.com/.default").token
                config["api_type"] = "azure_ad"
    except Exception as e:
        if "OPENAI_API_KEY" in os.environ:
            logger.warning(f"Failed to get credential for ACS with {e}, falling back to openai 0.x env vars.")
            config["api_key"] = os.environ["OPENAI_API_KEY"]
            config["api_type"] = os.environ.get("OPENAI_API_TYPE", "azure")
            config["api_base"] = os.environ.get("OPENAI_API_BASE", openai.api_base if hasattr(openai, "api_base") else openai.base_url)
            config["api_version"] = os.environ.get("OPENAI_API_VERSION", openai.api_version)
        elif "AZURE_OPENAI_KEY" in os.environ:
            logger.warning(f"Failed to get credential for ACS with {e}, falling back to openai 1.x env vars.")
            config["api_key"] = os.environ["AZURE_OPENAI_KEY"]
            config["azure_endpoint"] = os.environ.get("AZURE_OPENAI_ENDPOINT")
            config["api_version"] = os.environ.get("OPENAI_API_VERSION", openai.api_version)
        else:
            raise e

    if "azure" in openai.api_type:
        config["api_version"] = config.get("api_version", "2023-03-15-preview")

    return config
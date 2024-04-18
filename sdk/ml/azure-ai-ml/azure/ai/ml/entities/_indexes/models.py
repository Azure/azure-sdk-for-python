# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Language model classes."""

import copy
import json
import os
from typing import Optional

from azure.core.credentials import TokenCredential
from azure.ai.ml.entities._indexes.utils.connections import (
    connection_to_credential,
    get_connection_by_id_v2,
    get_connection_credential,
)
from azure.ai.ml.entities._indexes.utils.logging import get_logger

logger = get_logger(__name__)


def parse_model_uri(uri: str, **kwargs) -> dict:
    """Parse a model URI into a dictionary of configuration parameters."""
    config = {**kwargs}

    # If model uri is None, it is *considered* as a serverless endpoint for now.
    # TODO: finalized a scheme for different embeddings - serverless, openai, huggingface, etc.
    if uri is None:
        config["kind"] = "serverless_endpoint"
        return config

    scheme, details = uri.split("://")

    def split_details(details):
        details = details.split("/")
        dets = {}
        for i in range(0, len(details), 2):
            dets[details[i]] = details[i + 1]
        return dets

    if "is_florence" in config:
        config["kind"] = "florence"
        config["api_base"] = uri

    elif scheme == "azure_open_ai":
        config = {**split_details(details), **config}
        config["kind"] = "open_ai"
        if "endpoint" in config:
            substrings = [".openai.", ".api.cognitive.", ".cognitiveservices."]
            if any(substring in config["endpoint"] for substring in substrings):
                config["api_base"] = config["endpoint"].rstrip("/")
            else:
                config["api_base"] = f"https://{config['endpoint']}.openai.azure.com"
        config["api_type"] = "azure"
        config["api_version"] = (
            kwargs.get("api_version") if kwargs.get("api_version") is not None else "2023-03-15-preview"
        )
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

    if config.get("key") is not None:
        config["api_key"] = config.get("key")
    elif "connection_type" not in config:
        raise ValueError("AAD authentication is not supported for serverless at this time.")
    elif config["connection_type"].lower() == "workspace_connection":
        connection_id = config.get("connection", {}).get("id", "")
        connection = get_connection_by_id_v2(connection_id, credential=credential)

        if hasattr(connection, "type") and connection.type == "serverless":
            api_base = connection.target.rstrip("/")
            config["api_base"] = f"{api_base}/v1"
            # TODO: Remove fallback logic, and throw if appropriate metadata isn't set.
            if hasattr(connection, "metadata"):
                config["api_type"] = connection.metadata.get("MODEL_PROVIDER_NAME", "cohere").lower()
                config["model"] = connection.metadata.get("SERVED_MODEL_NAME", "cohere-embed-english")
            else:
                # TODO: Remove fallback logic, and throw if appropriate metadata isn't set.
                config["api_type"] = "cohere"
                config["model"] = "cohere-embed-english"
        elif (
            isinstance(connection, dict)
            and connection.get("properties", {}).get("category", None) == "Serverless"
        ):
            api_base = connection.get("properties", {}).get("target").rstrip("/")
            config["api_base"] = f"{api_base}/v1"
            connection_metadata = connection.get("properties", {}).get("metadata", {})
            # TODO: Remove fallback logic, and throw if appropriate metadata isn't set.
            config["api_type"] = connection_metadata.get("MODEL_PROVIDER_NAME", "cohere").lower()
            config["model"] = connection_metadata.get("SERVED_MODEL_NAME", "cohere-embed-english")
        else:
            raise ValueError(f"Malformed workspace connection response for connection {connection_id}")

        connection_credentials = connection_to_credential(connection)
        config["api_key"] = connection_credentials.key
    else:
        raise ValueError("Unknown connection type " + config["connection_type"])

    return config


# TODO: Vendor langchain deps or move to langchain module.
def init_llm(model_config: dict, **kwargs):
    """Initialize a language model from a model configuration."""
    from langchain.chat_models.azure_openai import AzureChatOpenAI
    from langchain.chat_models.openai import ChatOpenAI
    from langchain.llms import AzureOpenAI

    llm = None
    logger.debug(f"model_config: {json.dumps(model_config, indent=2)}")
    model_kwargs = {
        "frequency_penalty": model_config.get("frequency_penalty", 0),
        "presence_penalty": model_config.get("presence_penalty", 0),
    }
    if model_config.get("stop") is not None:
        model_kwargs["stop"] = model_config.get("stop")
    if model_config.get("kind", "").lower() == "open_ai" and model_config.get("api_type", "").lower() == "azure":
        model_config = init_open_ai_from_config(model_config)
        if (
            model_config["model"].startswith("gpt-3.5-turbo")
            or model_config["model"].startswith("gpt-35-turbo")
            or model_config["model"].startswith("gpt-4")
        ):
            logger.info(f"Initializing AzureChatOpenAI with model {model_config['model']} with kwargs: {model_kwargs}")

            llm = AzureChatOpenAI(
                deployment_name=model_config["deployment"],
                model=model_config["model"],
                max_tokens=model_config.get("max_tokens"),
                model_kwargs=model_kwargs,
                openai_api_key=model_config.get("api_key"),
                openai_api_base=model_config.get("api_base"),
                openai_api_type=model_config.get("api_type"),
                openai_api_version=model_config.get("api_version"),
                max_retries=model_config.get("max_retries", 3),
                **kwargs,
            )  # type: ignore
            if model_config.get("temperature", None) is not None:
                llm.temperature = model_config.get("temperature")
        else:
            logger.info(f"Initializing AzureOpenAI with model {model_config['model']} with kwargs: {model_kwargs}")

            llm = AzureOpenAI(
                deployment_name=model_config["deployment"],
                model=model_config["model"],
                max_tokens=model_config.get("max_tokens"),
                model_kwargs=model_kwargs,
                openai_api_key=model_config.get("api_key"),
                max_retries=model_config.get("max_retries", 3),
                **kwargs,
            )  # type: ignore
            if model_config.get("temperature", None) is not None:
                llm.temperature = model_config.get("temperature")
    elif model_config.get("kind", "").lower() == "open_ai" and model_config.get("api_type", "").lower() == "open_ai":
        logger.info(f"Initializing OpenAI with model {model_config['model']} with kwargs: {model_kwargs}")
        model_config = init_open_ai_from_config(model_config)
        llm = ChatOpenAI(
            model=model_config["model"],
            max_tokens=model_config.get("max_tokens"),
            model_kwargs=model_kwargs,
            openai_api_key=model_config.get("api_key"),
            **kwargs,
        )  # type: ignore
        if model_config.get("temperature", None) is not None:
            llm.temperature = model_config.get("temperature")
    else:
        raise ValueError(f"Unsupported llm kind: {model_config.get('kind')}")

    return llm

# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Language model classes."""
import copy
import json
import os
from typing import Optional

from azure.core.credentials import TokenCredential
from azure.ai.resources.constants._common import USER_AGENT_HEADER_KEY
from azure.ai.resources._index._utils.connections import (
    connection_to_credential,
    get_connection_by_id_v2,
    get_connection_credential,
)
from azure.ai.resources._index._utils.logging import get_logger
from azure.ai.resources._user_agent import USER_AGENT

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

    if openai.api_type and "azure" in openai.api_type:
        config["api_version"] = config.get("api_version", "2023-03-15-preview")

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
    if model_config.get("kind") == "open_ai" and model_config.get("api_type") == "azure":
        model_config = init_open_ai_from_config(model_config, credential=None)
        if model_config["model"].startswith("gpt-3.5-turbo") or model_config["model"].startswith("gpt-35-turbo") or model_config["model"].startswith("gpt-4"):
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
                default_headers={USER_AGENT_HEADER_KEY: USER_AGENT},
                **kwargs
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
                default_headers={USER_AGENT_HEADER_KEY: USER_AGENT},
                **kwargs
            )  # type: ignore
            if model_config.get("temperature", None) is not None:
                llm.temperature = model_config.get("temperature")
    elif model_config.get("kind") == "open_ai" and model_config.get("api_type") == "open_ai":
        logger.info(f"Initializing OpenAI with model {model_config['model']} with kwargs: {model_kwargs}")
        model_config = init_open_ai_from_config(model_config, credential=None)
        llm = ChatOpenAI(
            model=model_config["model"],
            max_tokens=model_config.get("max_tokens"),
            model_kwargs=model_kwargs,
            openai_api_key=model_config.get("api_key"),
            default_headers={USER_AGENT_HEADER_KEY: USER_AGENT},
            **kwargs
        )  # type: ignore
        if model_config.get("temperature", None) is not None:
            llm.temperature = model_config.get("temperature")
    else:
        raise ValueError(f"Unsupported llm kind: {model_config.get('kind')}")

    return llm
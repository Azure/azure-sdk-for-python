# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from dataclasses import dataclass
from typing import Any, Dict, Optional
from azure.ai.resources.entities import AzureOpenAIConnection
from azure.ai.ml._utils.utils import camel_to_snake



@dataclass
class AzureOpenAIModelConfiguration:
    api_base: str
    api_key: str
    api_version: Optional[str]
    model_name: str
    deployment_name: str
    model_kwargs: Dict[str, Any]

    @staticmethod
    def from_connection(
        connection: AzureOpenAIConnection, model_name: str, deployment_name: str, **model_kwargs
    ) -> 'AzureOpenAIModelConfiguration':
        if not isinstance(connection, AzureOpenAIConnection) or camel_to_snake(connection.type) != "azure_open_ai":
            raise TypeError(
                "Only AzureOpenAI connection objects are supported."
            )
        key = connection.credentials.get("key")
        if key is None:
            raise ValueError("Unable to retrieve openai key from connection object.")

        return AzureOpenAIModelConfiguration(
            api_base=connection.target,
            api_key=connection.credentials.key,
            api_version=connection.api_version,
            model_name=model_name,
            deployment_name=deployment_name,
            model_kwargs=model_kwargs,
        )

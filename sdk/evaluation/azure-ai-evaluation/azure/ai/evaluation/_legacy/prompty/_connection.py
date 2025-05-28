# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, ClassVar, Mapping, Optional

from azure.ai.evaluation._legacy.prompty._exceptions import MissingRequiredInputError
from azure.ai.evaluation._legacy.prompty._utils import dataclass_from_dict


def _is_empty_connection_config(connection_dict: Mapping[str, Any]) -> bool:
    return any(key not in {"azure_deployment", "model", "type"} for key in connection_dict.keys())


@dataclass
class Connection(ABC):
    """Base class for all connection classes."""

    @property
    @abstractmethod
    def type(self) -> str:
        """Gets the type of the connection.

        :return: The type of the connection.
        :rtype: str"""
        ...

    @staticmethod
    def parse_from_config(model_configuration: Mapping[str, Any]) -> "Connection":
        """Parse a connection from a model configuration.

        :param model_configuration: The model configuration.
        :type model_configuration: Mapping[str, Any]
        :return: The connection.
        :rtype: Connection
        """
        connection_dict = {**model_configuration}
        connection_type = connection_dict.pop("type", "")

        connection: Connection
        if connection_type in [AzureOpenAIConnection.TYPE, "azure_openai"]:
            if not _is_empty_connection_config(connection_dict):
                connection = AzureOpenAIConnection.from_env()
            else:
                connection = dataclass_from_dict(AzureOpenAIConnection, connection_dict)

        elif connection_type in [OpenAIConnection.TYPE, "openai"]:
            if not _is_empty_connection_config(connection_dict):
                connection = OpenAIConnection.from_env()
            else:
                connection = dataclass_from_dict(OpenAIConnection, connection_dict)

        else:
            error_message = (
                f"'{connection_type}' is not a supported connection type. Valid values are "
                f"[{AzureOpenAIConnection.TYPE}, {OpenAIConnection.TYPE}]"
            )
            raise MissingRequiredInputError(error_message)

        return connection


@dataclass
class OpenAIConnection(Connection):
    """Connection class for OpenAI endpoints."""

    base_url: str
    model: str
    api_key: Optional[str] = None
    organization: Optional[str] = None

    TYPE: ClassVar[str] = "openai"

    @property
    def type(self) -> str:
        return OpenAIConnection.TYPE

    @classmethod
    def from_env(cls) -> "OpenAIConnection":
        return cls(
            base_url=os.environ.get("OPENAI_BASE_URL", ""),
            model=os.environ.get("OPENAI_MODEL", ""),
            api_key=os.environ.get("OPENAI_API_KEY"),
            organization=os.environ.get("OPENAI_ORG_ID"),
        )


@dataclass
class AzureOpenAIConnection(Connection):
    """Connection class for Azure OpenAI endpoints."""

    azure_endpoint: str
    azure_deployment: str
    api_key: Optional[str] = None
    api_version: Optional[str] = None
    resource_id: Optional[str] = None

    TYPE: ClassVar[str] = "azure_openai"

    @property
    def type(self) -> str:
        return AzureOpenAIConnection.TYPE

    @classmethod
    def from_env(cls) -> "AzureOpenAIConnection":
        return cls(
            azure_endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT", ""),
            azure_deployment=os.environ.get("AZURE_OPENAI_DEPLOYMENT", ""),
            api_key=os.environ.get("AZURE_OPENAI_API_KEY"),
            api_version=os.environ.get("AZURE_OPENAI_API_VERSION", "2024-02-01"),
        )

    def __post_init__(self):
        # set default API version
        if not self.api_version:
            self.api_version = "2024-02-01"

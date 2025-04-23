# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import os
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, ClassVar, Mapping, Optional, Set, Union

from azure.ai.evaluation._legacy.prompty._exceptions import MissingRequiredInputError
from azure.ai.evaluation._legacy.prompty._utils import dataclass_from_dict


ENV_VAR_PATTERN = re.compile(r"^\$\{env:(.*)\}$")


def _parse_environment_variable(value: Union[str, Any]) -> Union[str, Any]:
    """Get environment variable from ${env:ENV_NAME}. If not found, return original value.

    :param value: The value to parse.
    :type value: str | Any
    :return: The parsed value
    :rtype: str | Any"""
    if not isinstance(value, str):
        return value

    result = re.match(ENV_VAR_PATTERN, value)
    if result:
        env_name = result.groups()[0]
        return os.environ.get(env_name, value)

    return value


def _is_empty_connection_config(connection_dict: Mapping[str, Any]) -> bool:
    ignored_fields = set(["azure_deployment", "model"])
    keys = {k for k, v in connection_dict.items() if v}
    return len(keys - ignored_fields) == 0


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

    @abstractmethod
    def is_valid(self, missing_fields: Optional[Set[str]] = None) -> bool:
        """Check if the connection is valid.

        :param missing_fields: If set, this will be populated with the missing required fields.
        :type missing_fields: Set[str] | None
        :return: True if the connection is valid, False otherwise.
        :rtype: bool"""
        ...

    @staticmethod
    def parse_from_config(model_configuration: Mapping[str, Any]) -> "Connection":
        """Parse a connection from a model configuration.

        :param model_configuration: The model configuration.
        :type model_configuration: Mapping[str, Any]
        :return: The connection.
        :rtype: Connection
        """
        connection: Connection
        connection_dict = {k: _parse_environment_variable(v) for k, v in model_configuration.items()}
        connection_type = connection_dict.pop("type", "")

        if connection_type in [AzureOpenAIConnection.TYPE, "azure_openai"]:
            if _is_empty_connection_config(connection_dict):
                connection = AzureOpenAIConnection.from_env()
            else:
                connection = dataclass_from_dict(AzureOpenAIConnection, connection_dict)

        elif connection_type in [OpenAIConnection.TYPE, "openai"]:
            if _is_empty_connection_config(connection_dict):
                connection = OpenAIConnection.from_env()
            else:
                connection = dataclass_from_dict(OpenAIConnection, connection_dict)

        else:
            error_message = (
                f"'{connection_type}' is not a supported connection type. Valid values are "
                f"[{AzureOpenAIConnection.TYPE}, {OpenAIConnection.TYPE}]"
            )
            raise MissingRequiredInputError(error_message)

        missing_fields: Set[str] = set()
        if not connection.is_valid(missing_fields):
            raise MissingRequiredInputError(
                f"The following required fields are missing for connection {connection.type}: "
                f"{', '.join(missing_fields)}"
            )

        return connection


@dataclass
class OpenAIConnection(Connection):
    """Connection class for OpenAI endpoints."""

    base_url: str
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
            api_key=os.environ.get("OPENAI_API_KEY"),
            organization=os.environ.get("OPENAI_ORG_ID"),
        )

    def is_valid(self, missing_fields: Optional[Set[str]] = None) -> bool:
        if missing_fields is None:
            missing_fields = set()
        if not self.base_url:
            missing_fields.add("base_url")
        if not self.api_key:
            missing_fields.add("api_key")
        if not self.organization:
            missing_fields.add("organization")
        return not bool(missing_fields)


@dataclass
class AzureOpenAIConnection(Connection):
    """Connection class for Azure OpenAI endpoints."""

    azure_endpoint: str
    api_key: Optional[str] = None  # TODO ralphe: Replace this TokenCredential to allow for more flexible authentication
    azure_deployment: Optional[str] = None
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
            api_key=os.environ.get("AZURE_OPENAI_API_KEY"),
            azure_deployment=os.environ.get("AZURE_OPENAI_DEPLOYMENT"),
            api_version=os.environ.get("AZURE_OPENAI_API_VERSION", "2024-02-01"),
        )

    def __post_init__(self):
        # set default API version
        if not self.api_version:
            self.api_version = "2024-02-01"

    def is_valid(self, missing_fields: Optional[Set[str]] = None) -> bool:
        if missing_fields is None:
            missing_fields = set()
        if not self.azure_endpoint:
            missing_fields.add("azure_endpoint")
        if not self.api_key:
            missing_fields.add("api_key")
        if not self.azure_deployment:
            missing_fields.add("azure_deployment")
        if not self.api_version:
            missing_fields.add("api_version")
        return not bool(missing_fields)

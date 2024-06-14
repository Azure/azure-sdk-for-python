# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from dataclasses import dataclass
from typing import Any, Dict, Optional
from azure.ai.ml._utils._experimental import experimental
from azure.ai.ml._utils.utils import camel_to_snake
from azure.ai.ml.entities._workspace.connections.workspace_connection import WorkspaceConnection
from azure.ai.ml.entities._workspace.connections.connection_subtypes import (
    AzureOpenAIConnection,
    AadCredentialConfiguration,
)


@experimental
@dataclass
class ModelConfiguration:
    """Configuration for a embedding model.

    :param api_base: The base URL for the API.
    :type api_base: Optional[str]
    :param api_key: The API key.
    :type api_key: Optional[str]
    :param api_version: The API version.
    :type api_version: Optional[str]
    :param model_name: The name of the model.
    :type model_name: Optional[str]
    :param model_name: The deployment name of the model.
    :type model_name: Optional[str]
    :param connection_name: The name of the workspace connection of this model.
    :type connection_name: Optional[str]
    :param connection_type: The type of the workspace connection of this model.
    :type connection_type: Optional[str]
    :param model_kwargs: Additional keyword arguments for the model.
    :type model_kwargs: Dict[str, Any]
    """

    api_base: Optional[str]
    api_key: Optional[str]
    api_version: Optional[str]
    connection_name: Optional[str]
    connection_type: Optional[str]
    model_name: Optional[str]
    deployment_name: Optional[str]
    model_kwargs: Dict[str, Any]

    def __init__(
        self,
        *,
        api_base: Optional[str],
        api_key: Optional[str],
        api_version: Optional[str],
        connection_name: Optional[str],
        connection_type: Optional[str],
        model_name: Optional[str],
        deployment_name: Optional[str],
        model_kwargs: Dict[str, Any]
    ):
        self.api_base = api_base
        self.api_key = api_key
        self.api_version = api_version
        self.connection_name = connection_name
        self.connection_type = connection_type
        self.model_name = model_name
        self.deployment_name = deployment_name
        self.model_kwargs = model_kwargs

    @staticmethod
    def from_connection(
        connection: WorkspaceConnection,
        model_name: Optional[str] = None,
        deployment_name: Optional[str] = None,
        **kwargs
    ) -> "ModelConfiguration":
        """Create an model configuration from a Connection.

        :param connection: The WorkspaceConnection object.
        :type connection: ~azure.ai.ml.entities.WorkspaceConnection
        :param model_name: The name of the model.
        :type model_name: Optional[str]
        :param deployment_name: The name of the deployment.
        :type deployment_name: Optional[str]
        :keyword kwargs: Additional keyword arguments for the model.
        :paramtype kwargs: Dict[str, Any]
        :return: The model configuration.
        :rtype: ~azure.ai.ml.entities._indexes.entities.ModelConfiguration
        :raises TypeError: If the connection is not an AzureOpenAIConnection.
        :raises ValueError: If the connection does not contain an OpenAI key.
        """
        if isinstance(connection, AzureOpenAIConnection) or camel_to_snake(connection.type) == "azure_open_ai":
            connection_type = "azure_open_ai"
            api_version = connection.api_version  # type: ignore[attr-defined]
            if not model_name or not deployment_name:
                raise ValueError("Please specify model_name and deployment_name.")
        elif connection.type and connection.type.lower() == "serverless":
            connection_type = "serverless"
            api_version = None
            if not connection.id:
                raise TypeError("The connection id is missing from the serverless connection object.")
        else:
            raise TypeError("Connection object is not supported.")

        if isinstance(connection.credentials, AadCredentialConfiguration):
            key = None
        else:
            key = connection.credentials.get("key")  # type: ignore[union-attr]
            if key is None and connection_type == "azure_open_ai":
                import os

                if "AZURE_OPENAI_API_KEY" in os.environ:
                    key = os.getenv("AZURE_OPENAI_API_KEY")
                else:
                    raise ValueError("Unable to retrieve openai key from connection object or env variable.")

        return ModelConfiguration(
            api_base=connection.target,
            api_key=key,
            api_version=api_version,
            connection_name=connection.name,
            connection_type=connection_type,
            model_name=model_name,
            deployment_name=deployment_name,
            model_kwargs=kwargs,
        )

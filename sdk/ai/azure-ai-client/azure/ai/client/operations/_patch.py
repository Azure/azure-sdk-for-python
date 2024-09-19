# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import List, Tuple, Union
from azure.core.credentials import AzureKeyCredential, TokenCredential
from ._operations import ConnectionsOperations as ConnectionsOperationsGenerated
from ..models._enums import AuthType, ConnectionCategory


class ConnectionsOperations(ConnectionsOperationsGenerated):

    def get_credential(
        self, *, connection_name: str = None, **kwargs
    ) -> Tuple[Union[str, AzureKeyCredential, TokenCredential], str]:

        if connection_name == "":
            raise ValueError("connection_name cannot be an empty string.")
        elif connection_name is None:
            response = self._get_connections()
            if len(response.value) == 0:
                raise ValueError("No connections found.")
            elif len(response.value) == 1:
                connection_name = response.value[0].name
            else:
                raise ValueError("There is more than one connection. Please specify the connection_name.")

        response = self._get_connection_secrets(
            connection_name_in_url=connection_name,
            connection_name=connection_name,
            subscription_id=self._config.subscription_id,
            resource_group_name=self._config.resource_group_name,
            workspace_name=self._config.workspace_name,
            api_version_in_body=self._config.api_version,
        )

        # Remove trailing slash from the endpoint if exist
        endpoint: str = (
            response.properties.target[:-1] if response.properties.target.endswith("/") else response.properties.target
        )

        if response.properties.auth_type == AuthType.API_KEY:
            if response.properties.category == ConnectionCategory.AZURE_OPEN_AI:
                key: str = response.properties.credentials.key
                return key, endpoint
            elif response.properties.category == ConnectionCategory.SERVERLESS:
                credential = AzureKeyCredential(response.properties.credentials.key)
                return credential, endpoint
            else:
                raise ValueError("Unknown connection category `{response.properties.category}`.")
        # elif response.properties.auth_type == AuthType.AAD:
        #    credentials = self._config.credential
        # elif response.properties.auth_type == AuthType.SAS:
        #    credentials =
        else:
            raise ValueError("Unknown authentication type `{response.properties.auth_type}`.")


__all__: List[str] = [
    "ConnectionsOperations"
]  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """

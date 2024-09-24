# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import List, Iterable
#from zoneinfo import ZoneInfo
from ._operations import ConnectionsOperations as ConnectionsOperationsGenerated
from ..models._enums import AuthenticationType, ConnectionType
from ..models._models import ConnectionsListSecretsResponse, ConnectionsListResponse

class ConnectionsOperations(ConnectionsOperationsGenerated):

    def get(
        self,
        *,
        connection_name: str,
        populate_secrets: bool = False
    ) -> ConnectionsListSecretsResponse:
        if not connection_name:
            raise ValueError("connection_name cannot be empty")
        if populate_secrets:
            connection: ConnectionsListSecretsResponse = self._list_secrets(
                connection_name_in_url=connection_name,
                connection_name=connection_name,
                subscription_id=self._config.subscription_id,
                resource_group_name=self._config.resource_group_name,
                workspace_name=self._config.workspace_name,
                api_version_in_body=self._config.api_version,
            )
            if connection.properties.auth_type == AuthenticationType.ENTRA_ID:
                connection.properties.token_credential = self._config.credential
                return connection
            elif connection.properties.auth_type == AuthenticationType.SAS:
                from .._patch import SASTokenCredential
                connection.properties.token_credentials = SASTokenCredential(
                    sas_token=connection.properties.credentials.sas,
                    credential=self._config.credential,
                    subscription_id=self._config.subscription_id,
                    resource_group_name=self._config.resource_group_name,
                    workspace_name=self._config.workspace_name,
                    connection_name=connection_name)
                return connection

            return connection
        else:
            internal_response: ConnectionsListResponse = self._list()
            for connection in internal_response.value:
                if connection_name == connection.name:
                    return connection
            return None

    def list(
        self,
        *,
        connection_type: ConnectionType | None = None,
        populate_secrets: bool = False
    ) -> Iterable[ConnectionsListSecretsResponse]:
        # First make a REST call to /list to get all the connections
        internal_response: ConnectionsListResponse = self._list()
        filtered_connections: List[ConnectionsListSecretsResponse] = []
        # Filter by connection type
        for connection in internal_response.value:
            if connection_type is None or connection.properties.category == connection_type:
                filtered_connections.append(connection)
        if not populate_secrets:
            # If no secrets are needed, we are done. Return filtered list.
            return filtered_connections
        else:
            # If secrets are needed, for each connection in the list, we now 
            # need to make a /listSecrets rest call to get the connection with secrets
            filtered_connections_with_secrets: List[ConnectionsListSecretsResponse] = []
            for connection in filtered_connections:
               filtered_connections_with_secrets.append(
                   self.get(connection_name=connection.name, populate_secrets=True)
               )
            return filtered_connections_with_secrets


__all__: List[str] = [
    "ConnectionsOperations"
]  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """

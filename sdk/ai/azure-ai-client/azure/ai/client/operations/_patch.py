# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
import base64
import json
from typing import List, Tuple, Union, Iterable, Any
from datetime import datetime, timedelta
#from zoneinfo import ZoneInfo
from azure.core.credentials import AzureKeyCredential, TokenCredential, AccessToken
from ._operations import ConnectionsOperations as ConnectionsOperationsGenerated
from ..models._enums import AuthenticationType, ConnectionType
from ..models._models import ConnectionsListSecretsResponse, ConnectionsListResponse
from .._patch import AzureAIClient

class SASTokenCredential(TokenCredential):
    def __init__(
            self,
            *,
            sas_token: str,
            credential: TokenCredential,
            subscription_id: str,
            resource_group_name: str,
            workspace_name: str,
            connection_name: str
        ):
        self._sas_token = sas_token
        self._credential = credential
        self._subscription_id = subscription_id
        self._resource_group_name = resource_group_name
        self._workspace_name = workspace_name
        self._connection_name = connection_name
        self._expires_on = SASTokenCredential._get_expiration_date_from_token(self.sas_token)

    @classmethod
    def _get_expiration_date_from_token(jwt_token: str) -> datetime:
        payload = jwt_token.split('.')[1]
        padded_payload = payload + '=' * (4 - len(payload) % 4)  # Add padding if necessary
        decoded_bytes = base64.urlsafe_b64decode(padded_payload)
        decoded_str = decoded_bytes.decode('utf-8')
        decoded_payload = json.loads(decoded_str)
        expiration_date = decoded_payload.get('exp')
        return datetime.fromtimestamp(expiration_date, datetime.timezone.utc)

    def _refresh_token(self) -> None:
        ai_client = AzureAIClient(
            credential=self._credential,
            subscription_id=self._subscription_id,
            resource_group_name=self._resource_group_name,
            workspace_name=self._workspace_name,
        )

        connection = ai_client.connections.get(
            connection_name=self._connection_name,
            populate_secrets=True
        )

        self._sas_token = connection.properties.credentials.sas
        self._expires_on = SASTokenCredential._get_expiration_date_from_token(self._sas_token)

    def get_token(
            self,
            *scopes: str,
            claims: str | None = None,
            tenant_id: str | None = None,
            enable_cae: bool = False,
            **kwargs: Any
    ) -> AccessToken:
        if self.expires_on < datetime.datetime.now(datetime.timezone.utc):
            self._refresh_token()
        return AccessToken(self.sas_token, self.expires_on.timestamp())


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

# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import List, Iterable

# from zoneinfo import ZoneInfo
from ._operations import EndpointsOperations as EndpointsOperationsGenerated
from ..models._enums import AuthenticationType, EndpointType
from ..models._models import ConnectionsListSecretsResponse, ConnectionsListResponse
from ..models._patch import EndpointProperties


class EndpointsOperations(EndpointsOperationsGenerated):

    def get_default(self, *, endpoint_type: EndpointType, populate_secrets: bool = False) -> EndpointProperties:
        if not endpoint_type:
            raise ValueError("You must specify an endpoint type")
        endpoint_properties_list = self.list(endpoint_type=endpoint_type, populate_secrets=populate_secrets)
        # Since there is no notion of service default at the moment, always return the first one
        if len(endpoint_properties_list) > 0:
            return endpoint_properties_list[0]
        else:
            return None

    def get(self, *, endpoint_name: str, populate_secrets: bool = False) -> ConnectionsListSecretsResponse:
        if not endpoint_name:
            raise ValueError("Endpoint name cannot be empty")
        if populate_secrets:
            connection: ConnectionsListSecretsResponse = self._list_secrets(
                connection_name_in_url=endpoint_name,
                connection_name=endpoint_name,
                subscription_id=self._config.subscription_id,
                resource_group_name=self._config.resource_group_name,
                workspace_name=self._config.workspace_name,
                api_version_in_body=self._config.api_version,
            )
            if connection.properties.auth_type == AuthenticationType.AAD:
                return EndpointProperties(connection=connection, token_credential=self._config.credential)
            elif connection.properties.auth_type == AuthenticationType.SAS:
                from .._patch import SASTokenCredential

                token_credential = SASTokenCredential(
                    sas_token=connection.properties.credentials.sas,
                    credential=self._config.credential,
                    subscription_id=self._config.subscription_id,
                    resource_group_name=self._config.resource_group_name,
                    workspace_name=self._config.workspace_name,
                    connection_name=endpoint_name,
                )
                return EndpointProperties(connection=connection, token_credential=token_credential)

            return EndpointProperties(connection=connection)
        else:
            internal_response: ConnectionsListResponse = self._list()
            for connection in internal_response.value:
                if endpoint_name == connection.name:
                    return EndpointProperties(connection=connection)
            return None

    def list(
        self, *, endpoint_type: EndpointType | None = None, populate_secrets: bool = False
    ) -> Iterable[EndpointProperties]:

        # First make a REST call to /list to get all the connections, without secrets
        connections_list: ConnectionsListResponse = self._list()
        endpoint_properties_list: List[EndpointProperties] = []

        # Filter by connection type
        for connection in connections_list.value:
            if endpoint_type is None or connection.properties.category == endpoint_type:
                if not populate_secrets:
                    endpoint_properties_list.append(EndpointProperties(connection=connection))
                else:
                    endpoint_properties_list.append(self.get(endpoint_name=connection.name, populate_secrets=True))

        return endpoint_properties_list


__all__: List[str] = [
    "EndpointsOperations"
]  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """

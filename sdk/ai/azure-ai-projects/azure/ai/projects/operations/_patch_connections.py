# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import Optional, Any, Union
from azure.core.tracing.decorator import distributed_trace
from ._operations import ConnectionsOperations as ConnectionsOperationsGenerated
from ..models._models import Connection
from ..models._enums import ConnectionType


class ConnectionsOperations(ConnectionsOperationsGenerated):
    """
    .. warning::
        **DO NOT** instantiate this class directly.

        Instead, you should access the following operations through
        :class:`~azure.ai.projects.AIProjectClient`'s
        :attr:`connections` attribute.
    """

    @distributed_trace
    def get(self, name: str, *, include_credentials: Optional[bool] = False, **kwargs: Any) -> Connection:
        """Get a connection by name.

        :param name: The name of the connection. Required.
        :type name: str
        :keyword include_credentials: Whether to include credentials in the response. Default is False.
        :paramtype include_credentials: bool
        :return: Connection. The Connection is compatible with MutableMapping
        :rtype: ~azure.ai.projects.models.Connection
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        if include_credentials:
            return super()._get_with_credentials(name, **kwargs)

        return super()._get(name, **kwargs)

    @distributed_trace
    def get_default(
        self, connection_type: Union[str, ConnectionType], *, include_credentials: Optional[bool] = False, **kwargs: Any
    ) -> Connection:
        """Get the default connection for a given connection type.

        :param connection_type: The type of the connection. Required.
        :type connection_type: str or ~azure.ai.projects.models.ConnectionType
        :keyword include_credentials: Whether to include credentials in the response. Default is False.
        :paramtype include_credentials: bool
        :return: Connection. The Connection is compatible with MutableMapping
        :rtype: ~azure.ai.projects.models.Connection
        :raises ValueError: If no default connection is found for the given type.
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        connections = super().list(connection_type=connection_type, default_connection=True, **kwargs)
        for connection in connections:
            if include_credentials:
                connection = super()._get_with_credentials(connection.name, **kwargs)
            return connection
        raise ValueError(f"No default connection found for type: {connection_type}.")

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
            connection = super()._get_with_credentials(name, **kwargs)
            if connection.type == ConnectionType.CUSTOM:
                # Fix for GitHub issue https://github.com/Azure/azure-sdk-for-net/issues/52355
                # Although the issue was filed on C# Projects SDK, the same problem exists in Python SDK.
                # Assume your Foundry project has a connection of type `Custom`, named "test_custom_connection",
                # and you defined two public and two secrete (private) keys. When you get the connection, the response
                # payload will look something like this:
                #     {
                #         "name": "test_custom_connection",
                #         "id": "/subscriptions/.../connections/test_custom_connection",
                #         "type": "CustomKeys",
                #         "target": "_",
                #         "isDefault": true,
                #         "credentials": {
                #             "nameofprivatekey1": "PrivateKey1",
                #             "nameofprivatekey2": "PrivateKey2",
                #             "type": "CustomKeys"
                #         },
                #         "metadata": {
                #             "NameOfPublicKey1": "PublicKey1",
                #             "NameOfPublicKey2": "PublicKey2"
                #         }
                #     }
                # We would like to add a new Dict property on the Python `credentials` object, named `credential_keys`,
                # to hold all the secret keys. This is done by the line below.
                setattr(
                    connection.credentials,
                    "credential_keys",
                    {k: v for k, v in connection.credentials.as_dict().items() if k != "type"},
                )

            return connection

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
            return self.get(connection.name, include_credentials=include_credentials, **kwargs)
        raise ValueError(f"No default connection found for type: {connection_type}.")

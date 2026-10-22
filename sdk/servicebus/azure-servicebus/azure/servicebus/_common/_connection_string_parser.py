# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from typing import Optional
from ..management._models import DictMixin
from .._base_handler import _parse_conn_str


class ServiceBusConnectionStringProperties(DictMixin):
    """
    Properties of a connection string.
    """

    def __init__(
        self,
        *,
        fully_qualified_namespace: str,
        endpoint: str,
        entity_path: Optional[str] = None,
        shared_access_signature: Optional[str] = None,
        shared_access_key_name: Optional[str] = None,
        shared_access_key: Optional[str] = None
    ):
        self._fully_qualified_namespace = fully_qualified_namespace
        self._endpoint = endpoint
        self._entity_path = entity_path
        self._shared_access_signature = shared_access_signature
        self._shared_access_key_name = shared_access_key_name
        self._shared_access_key = shared_access_key

    @property
    def fully_qualified_namespace(self) -> str:
        """The fully qualified host name for the Service Bus namespace.
        The namespace format is: `<yournamespace>.servicebus.windows.net`.
        :rtype: str
        """
        return self._fully_qualified_namespace

    @property
    def endpoint(self) -> str:
        """The endpoint for the Service Bus resource. In the format sb://<FQDN>/
        :rtype: str
        """
        return self._endpoint

    @property
    def entity_path(self) -> Optional[str]:
        """Optional. Represents the name of the queue/topic.
        :rtype: str or None
        """

        return self._entity_path

    @property
    def shared_access_signature(self) -> Optional[str]:
        """
        This can be provided instead of the shared_access_key_name and the shared_access_key.
        :rtype: str or None
        """
        return self._shared_access_signature

    @property
    def shared_access_key_name(self) -> Optional[str]:
        """
        The name of the shared_access_key. This must be used along with the shared_access_key.
        :rtype: str or None
        """
        return self._shared_access_key_name

    @property
    def shared_access_key(self) -> Optional[str]:
        """
        The shared_access_key can be used along with the shared_access_key_name as a credential.
        :rtype: str or None
        """
        return self._shared_access_key


def parse_connection_string(conn_str: str) -> "ServiceBusConnectionStringProperties":
    """Parse the connection string into a properties bag containing its component parts.

    :param conn_str: The connection string that has to be parsed.
    :type conn_str: str
    :return: A properties model containing the parsed connection string.
    :rtype: ~azure.servicebus.ServiceBusConnectionStringProperties
    """
    fully_qualified_namespace, policy, key, entity, signature, emulator = _parse_conn_str(conn_str, True)[ # pylint: disable=unused-variable
        :-1
    ]
    endpoint = "sb://" + fully_qualified_namespace + "/"
    return ServiceBusConnectionStringProperties(
        fully_qualified_namespace=fully_qualified_namespace,
        endpoint=endpoint,
        entity_path=entity,
        shared_access_signature=signature,
        shared_access_key_name=policy,
        shared_access_key=key,
    )

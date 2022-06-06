# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from ..management._models import DictMixin
from .._base_handler import _parse_conn_str


class ServiceBusConnectionStringProperties(DictMixin):
    """
    Properties of a connection string.
    """

    def __init__(self, **kwargs):
        self._fully_qualified_namespace = kwargs.pop("fully_qualified_namespace", None)
        self._endpoint = kwargs.pop("endpoint", None)
        self._entity_path = kwargs.pop("entity_path", None)
        self._shared_access_signature = kwargs.pop("shared_access_signature", None)
        self._shared_access_key_name = kwargs.pop("shared_access_key_name", None)
        self._shared_access_key = kwargs.pop("shared_access_key", None)

    @property
    def fully_qualified_namespace(self):
        """The fully qualified host name for the Service Bus namespace.
        The namespace format is: `<yournamespace>.servicebus.windows.net`.
        """
        return self._fully_qualified_namespace

    @property
    def endpoint(self):
        """The endpoint for the Service Bus resource. In the format sb://<FQDN>/"""
        return self._endpoint

    @property
    def entity_path(self):
        """Optional. Represents the name of the queue/topic."""
        return self._entity_path

    @property
    def shared_access_signature(self):
        """
        This can be provided instead of the shared_access_key_name and the shared_access_key.
        """
        return self._shared_access_signature

    @property
    def shared_access_key_name(self):
        """
        The name of the shared_access_key. This must be used along with the shared_access_key.
        """
        return self._shared_access_key_name

    @property
    def shared_access_key(self):
        """
        The shared_access_key can be used along with the shared_access_key_name as a credential.
        """
        return self._shared_access_key


def parse_connection_string(conn_str):
    # type(str) -> ServiceBusConnectionStringProperties
    """Parse the connection string into a properties bag containing its component parts.

    :param conn_str: The connection string that has to be parsed.
    :type conn_str: str
    :rtype: ~azure.servicebus.ServiceBusConnectionStringProperties
    """
    fully_qualified_namespace, policy, key, entity, signature = _parse_conn_str(
        conn_str, True
    )[:-1]
    endpoint = "sb://" + fully_qualified_namespace + "/"
    props = {
        "fully_qualified_namespace": fully_qualified_namespace,
        "endpoint": endpoint,
        "entity_path": entity,
        "shared_access_signature": signature,
        "shared_access_key_name": policy,
        "shared_access_key": key,
    }
    return ServiceBusConnectionStringProperties(**props)

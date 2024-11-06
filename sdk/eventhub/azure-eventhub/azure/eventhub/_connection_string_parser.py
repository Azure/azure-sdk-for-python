# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from typing import Any, Dict, Optional
from ._mixin import DictMixin
from ._client_base import _parse_conn_str


class EventHubConnectionStringProperties(DictMixin):
    """
    Properties of a connection string.
    """

    def __init__(  # pylint: disable=unused-argument
        self,
        *,
        fully_qualified_namespace: str,
        endpoint: str,
        eventhub_name: Optional[str] = None,
        shared_access_signature: Optional[str] = None,
        shared_access_key_name: Optional[str] = None,
        shared_access_key: Optional[str] = None,
        **kwargs: Any
    ) -> None:
        self._fully_qualified_namespace: str = fully_qualified_namespace
        self._endpoint: str = endpoint
        self._eventhub_name: Optional[str] = eventhub_name
        self._shared_access_signature: Optional[str] = shared_access_signature
        self._shared_access_key_name: Optional[str] = shared_access_key_name
        self._shared_access_key: Optional[str] = shared_access_key

    @property
    def fully_qualified_namespace(self) -> str:
        """The fully qualified host name for the Event Hubs namespace.
        The namespace format is: `<yournamespace>.servicebus.windows.net`.

        :rtype: str
        """
        return self._fully_qualified_namespace

    @property
    def endpoint(self) -> str:
        """The endpoint for the Event Hubs resource. In the format sb://<FQDN>/

        :rtype: str
        """
        return self._endpoint

    @property
    def eventhub_name(self) -> Optional[str]:
        """Optional. The name of the Event Hub, represented by `EntityPath` in the connection string.

        :rtype: str
        """
        return self._eventhub_name

    @property
    def shared_access_signature(self) -> Optional[str]:
        """
        This can be provided instead of the shared_access_key_name and the shared_access_key.

        :rtype: str
        """
        return self._shared_access_signature

    @property
    def shared_access_key_name(self) -> Optional[str]:
        """
        The name of the shared_access_key. This must be used along with the shared_access_key.

        :rtype: str
        """
        return self._shared_access_key_name

    @property
    def shared_access_key(self) -> Optional[str]:
        """
        The shared_access_key can be used along with the shared_access_key_name as a credential.

        :rtype: str
        """
        return self._shared_access_key


def parse_connection_string(conn_str: str) -> "EventHubConnectionStringProperties":
    """Parse the connection string into a properties bag containing its component parts.

    :param conn_str: The connection string that has to be parsed.
    :type conn_str: str
    :return: A properties bag containing the parsed connection string.
    :rtype: ~azure.eventhub.EventHubConnectionStringProperties
    """
    fully_qualified_namespace, policy, key, entity, signature, emulator = _parse_conn_str(conn_str, check_case=True)[
        :-1
    ]
    endpoint = "sb://" + fully_qualified_namespace + "/"
    props: Dict[str, Any] = {
        "fully_qualified_namespace": fully_qualified_namespace,
        "endpoint": endpoint,
        "eventhub_name": entity,
        "shared_access_signature": signature,
        "shared_access_key_name": policy,
        "shared_access_key": key,
        "emulator": emulator,
    }
    return EventHubConnectionStringProperties(**props)

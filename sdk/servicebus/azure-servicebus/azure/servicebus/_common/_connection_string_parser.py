# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse  # type: ignore

class ServiceBusConnectionStringProperties(object):
    """
    Properties of a connection string.
    """
    def __init__(self, **kwargs):
        self.fully_qualified_namespace = kwargs.pop('fully_qualified_namespace', None)
        self.endpoint = kwargs.pop('endpoint', None)
        self.entity_path = kwargs.pop('entity_path', None)
        self.shared_access_signature = kwargs.pop('shared_access_signature', None)
        self.shared_access_key_name = kwargs.pop('shared_access_key_name', None)
        self.shared_access_key = kwargs.pop('shared_access_key', None)


class ServiceBusConnectionStringParser(object):
    """Parse the connection string.

    :param conn_str: The connection string that has to be parsed.
    """
    def __init__(self, conn_str, **kwargs):
        # type: (str, Any) -> None
        """
        :param conn_str: The connection string to parse.
        :type conn_str: str
        """
        self._conn_str = conn_str

    def parse(self, **kwargs):
        # type(Any) -> ServiceBusConnectionStringProperties
        """
        Parse the connection string.
        """
        conn_str = self._conn_str.rstrip(";")
        conn_settings = [s.split("=", 1) for s in conn_str.split(";")]
        if any(len(tup) != 2 for tup in conn_settings):
            raise ValueError("Connection string is either blank or malformed.")
        conn_settings = dict(conn_settings)
        shared_access_signature = conn_settings.get('SharedAccessSignature')
        shared_access_key = conn_settings.get('SharedAccessKey')
        if shared_access_signature is not None and shared_access_key is not None:
            raise ValueError("Only one of the SharedAccessKey or SharedAccessSignature must be present.")
        endpoint = conn_settings.get('Endpoint')
        if not endpoint:
            raise ValueError("Connection string is either blank or malformed.")
        parsed = urlparse(endpoint.rstrip('/'))
        if not parsed.netloc:
            raise ValueError("Invalid Endpoint on the Connection String.")
        namespace = parsed.netloc.strip()
        props = {
            'fully_qualified_namespace': namespace,
            'endpoint': endpoint,
            'entity_path': conn_settings.get('EntityPath'),
            'shared_access_signature': shared_access_signature,
            'shared_access_key_name': conn_settings.get('SharedAccessKeyName'),
            'shared_access_key': shared_access_key
        }
        return ServiceBusConnectionStringProperties(**props)

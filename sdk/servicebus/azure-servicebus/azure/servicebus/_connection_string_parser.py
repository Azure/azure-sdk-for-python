# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


class ServiceBusConnectionStringParser(object):
    """
    Parse the connection string.
    """
    def __init__(self, conn_str, **kwargs):
        """
        :param conn_str: The connection string.
        :type conn_str: str
        """
        self._conn_str = conn_str
        self.fully_qualified_namespace = None
        self.endpoint = None
        self.entity_path = None
        self.shared_access_signature = None
        self.shared_access_key_name = None
        self.shared_access_key = None


    def parse(self, **kwargs):
        """
        Parse the connection string.
        """
        conn_str = self._conn_str.rstrip(";")
        conn_settings = [s.split("=", 1) for s in conn_str.split(";")]
        if any(len(tup) != 2 for tup in conn_settings):
            raise ValueError("Connection string is either blank or malformed.")
        conn_settings = dict(conn_settings)
        endpoints = _SERVICE_PARAMS[service]
        primary = None
        secondary = None
        if not credential:
            try:
                credential = {"account_name": conn_settings["AccountName"], "account_key": conn_settings["AccountKey"]}
            except KeyError:
                credential = conn_settings.get("SharedAccessSignature")
        if endpoints["primary"] in conn_settings:
            primary = conn_settings[endpoints["primary"]]
            if endpoints["secondary"] in conn_settings:
                secondary = conn_settings[endpoints["secondary"]]
        else:
            if endpoints["secondary"] in conn_settings:
                raise ValueError("Connection string specifies only secondary endpoint.")
            try:
                primary = "{}://{}.{}.{}".format(
                    conn_settings["DefaultEndpointsProtocol"],
                    conn_settings["AccountName"],
                    service,
                    conn_settings["EndpointSuffix"],
                )
                secondary = "{}-secondary.{}.{}".format(
                    conn_settings["AccountName"], service, conn_settings["EndpointSuffix"]
                )
            except KeyError:
                pass

        if not primary:
            try:
                primary = "https://{}.{}.{}".format(
                    conn_settings["AccountName"], service, conn_settings.get("EndpointSuffix", SERVICE_HOST_BASE)
                )
            except KeyError:
                raise ValueError("Connection string missing required connection details.")
        return primary, secondary, credential

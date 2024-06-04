# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
import os
import re
import typing

LIVE_ENDPOINT = "liveendpoint"
INGESTION_ENDPOINT = "ingestionendpoint"
INSTRUMENTATION_KEY = "instrumentationkey"

# Validate UUID format
# Specs taken from https://tools.ietf.org/html/rfc4122
uuid_regex_pattern = re.compile(
    "^[0-9a-f]{8}-"
    "[0-9a-f]{4}-"
    "[0-9a-f]{4}-"
    "[0-9a-f]{4}-"
    "[0-9a-f]{12}$"
)


class ConnectionStringParser:
    """ConnectionString parser.

    :param connection_string: Azure Connection String.
    :type: str
    :rtype: None
    """

    def __init__(
        self,
        connection_string: typing.Optional[str] = None
    ) -> None:
        self.instrumentation_key = None
        self.endpoint = ""
        self.live_endpoint = ""
        self._connection_string = connection_string
        self._initialize()
        self._validate_instrumentation_key()

    def _initialize(self) -> None:
        # connection string and ikey
        code_cs = self._parse_connection_string(self._connection_string)
        code_ikey = self.instrumentation_key
        env_cs = self._parse_connection_string(
            os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING")
        )
        env_ikey = os.getenv("APPINSIGHTS_INSTRUMENTATIONKEY")

        # The priority of which value takes on the instrumentation key is:
        # 1. Key from explicitly passed in connection string
        # 2. Key from explicitly passed in instrumentation key
        # 3. Key from connection string in environment variable
        # 4. Key from instrumentation key in environment variable
        self.instrumentation_key = (
            code_cs.get(INSTRUMENTATION_KEY) # type: ignore
            or code_ikey
            or env_cs.get(INSTRUMENTATION_KEY)
            or env_ikey
        )
        # The priority of the endpoints is as follows:
        # 1. The endpoint explicitly passed in connection string
        # 2. The endpoint from the connection string in environment variable
        # 3. The default breeze endpoint
        self.endpoint = (
            code_cs.get(INGESTION_ENDPOINT)
            or env_cs.get(INGESTION_ENDPOINT)
            or "https://dc.services.visualstudio.com"
        )
        self.live_endpoint = (
            code_cs.get(LIVE_ENDPOINT)
            or env_cs.get(LIVE_ENDPOINT)
            or "https://rt.services.visualstudio.com"
        )


    def _validate_instrumentation_key(self) -> None:
        """Validates the instrumentation key used for Azure Monitor.

        An instrumentation key cannot be null or empty. An instrumentation key
        is valid for Azure Monitor only if it is a valid UUID.
        """
        if not self.instrumentation_key:
            raise ValueError("Instrumentation key cannot be none or empty.")
        match = uuid_regex_pattern.match(self.instrumentation_key)
        if not match:
            raise ValueError(
                "Invalid instrumentation key. It should be a valid UUID.")

    def _parse_connection_string(self, connection_string) -> typing.Dict:
        if connection_string is None:
            return {}
        try:
            pairs = connection_string.split(";")
            result = dict(s.split("=") for s in pairs)
            # Convert keys to lower-case due to case type-insensitive checking
            result = {key.lower(): value for key, value in result.items()}
        except Exception as exc:
            raise ValueError("Invalid connection string") from exc
        # Validate authorization
        auth = result.get("authorization")
        if auth is not None and auth.lower() != "ikey":
            raise ValueError("Invalid authorization mechanism")

        # Construct the endpoints if not passed in explicitly
        endpoint_suffix = ""
        location_prefix = ""
        suffix = result.get("endpointsuffix")
        # Get regional information if provided
        prefix = result.get("location")
        if suffix is not None:
            endpoint_suffix = suffix
            # Get regional information if provided
            prefix = result.get("location")
            if prefix is not None:
                location_prefix = prefix + "."
        # Construct the endpoints if not passed in explicitly
        if result.get(INGESTION_ENDPOINT) is None:
            if endpoint_suffix:
                result[INGESTION_ENDPOINT] = "https://{0}dc.{1}".format(
                    location_prefix, endpoint_suffix
                )
            else:
                # Default to None if cannot construct
                result[INGESTION_ENDPOINT] = None
        if result.get(LIVE_ENDPOINT) is None:
            if endpoint_suffix:
                result[LIVE_ENDPOINT] = "https://{0}live.{1}".format(
                    location_prefix, endpoint_suffix
                )
            else:
                result[LIVE_ENDPOINT] = None

        return result

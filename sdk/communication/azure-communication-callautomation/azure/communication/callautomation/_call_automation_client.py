# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from typing import Any  # pylint: disable=unused-import
from urllib.parse import urlparse
from azure.core.credentials import TokenCredential

from ._version import SDK_MONIKER
from ._api_versions import DEFAULT_VERSION
from ._call_connection import CallConnection
from ._call_recording import CallRecording
from ._generated._client import AzureCommunicationCallAutomationService
from ._shared.utils import get_authentication_policy, parse_connection_str

class CallAutomationClient(object):
    def __init__(
            self,
            endpoint,  # type: str
            credential,  # type: TokenCredential
            **kwargs  # type: Any
    ):
        # type: (...) -> None
        if not credential:
            raise ValueError("credential can not be None")

        try:
            if not endpoint.lower().startswith('http'):
                endpoint = "https://" + endpoint
        except AttributeError:
            raise ValueError("Host URL must be a string")

        parsed_url = urlparse(endpoint.rstrip('/'))
        if not parsed_url.netloc:
            raise ValueError("Invalid URL: {}".format(endpoint))

        self._endpoint = endpoint
        self._api_version = kwargs.pop("api_version", DEFAULT_VERSION)
        self._credential = credential

        self._client = AzureCommunicationCallAutomationService(
            self._endpoint,
            api_version = self._api_version,
            authentication_policy=get_authentication_policy(endpoint, credential),
            sdk_moniker = SDK_MONIKER,
            **kwargs)

        self._call_connection_client = self._client.call_connection
        self._call_media = self._client.call_media
        self._call_recording_client = self._client.call_recording

    @classmethod
    def from_connection_string(
        cls,
        conn_str,  # type: str
        **kwargs  # type: Any
    ):  # type: (...) -> CallAutomationClient
        endpoint, access_key = parse_connection_str(conn_str)

        return cls(endpoint, access_key, **kwargs)

    def get_call_connection(
        self,
        call_connection_id,  # type: str
        **kwargs  # type: Any
    ):  # type: (...) -> CallConnection

        if not call_connection_id:
            raise ValueError("call_connection_id can not be None")

        return CallConnection(
            call_connection_id,
            self._call_connection_client,
            self._call_media,
            **kwargs
            )

    def get_call_recording(
        self,
        **kwargs  # type: Any
    ):  # type: (...) -> CallRecording

        return CallRecording(
            self._call_recording_client,
            **kwargs
            )

# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from typing import TYPE_CHECKING

from azure.core import PipelineClient
from azure.core.credentials import TokenCredential
from azure.core.pipeline import policies

from ._configuration import CodeTransparencyClientConfiguration
from ._version import VERSION

if TYPE_CHECKING:
    from typing import Any


class CodeTransparencyClient:
    """Microsoft Code Transparency Service.

    :param endpoint: The Code Transparency Service endpoint.
    :type endpoint: str
    :param credential: Credential needed for the client to connect to Azure.
    :type credential: ~azure.core.credentials.TokenCredential
    :keyword api_version: API version to use for the request. Default is "2024-01-11-preview".
    :paramtype api_version: str
    """

    def __init__(
        self,
        endpoint: str,
        credential: TokenCredential,
        **kwargs: Any
    ) -> None:
        _endpoint = '{endpoint}'
        self._config = CodeTransparencyClientConfiguration(
            endpoint=endpoint, credential=credential, **kwargs
        )
        self._client: PipelineClient = PipelineClient(
            base_url=_endpoint, config=self._config, **kwargs
        )

    def close(self) -> None:
        """Close the client."""
        self._client.close()

    def __enter__(self) -> "CodeTransparencyClient":
        self._client.__enter__()
        return self

    def __exit__(self, *exc_details) -> None:
        self._client.__exit__(*exc_details)
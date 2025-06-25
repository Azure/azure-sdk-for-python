# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from typing import TYPE_CHECKING

from azure.core.pipeline import AsyncPipeline
from azure.core.credentials_async import AsyncTokenCredential

from .._configuration import CodeTransparencyClientConfiguration
from .._version import VERSION

if TYPE_CHECKING:
    from typing import Any


class AsyncCodeTransparencyClient:
    """Microsoft Code Transparency Service (Async).

    :param endpoint: The Code Transparency Service endpoint.
    :type endpoint: str
    :param credential: Credential needed for the client to connect to Azure.
    :type credential: ~azure.core.credentials_async.AsyncTokenCredential
    :keyword api_version: API version to use for the request. Default is "2024-01-11-preview".
    :paramtype api_version: str
    """

    def __init__(
        self,
        endpoint: str,
        credential: AsyncTokenCredential,
        **kwargs: "Any"
    ) -> None:
        _endpoint = '{endpoint}'
        self._config = CodeTransparencyClientConfiguration(
            endpoint=endpoint, credential=credential, **kwargs
        )
        self._client = AsyncPipeline(
            base_url=_endpoint, config=self._config, **kwargs
        )

    async def close(self) -> None:
        """Close the client."""
        await self._client.close()

    async def __aenter__(self) -> "AsyncCodeTransparencyClient":
        await self._client.__aenter__()
        return self

    async def __aexit__(self, *exc_details) -> None:
        await self._client.__aexit__(*exc_details)
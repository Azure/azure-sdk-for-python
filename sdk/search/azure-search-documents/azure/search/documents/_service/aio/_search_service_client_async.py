# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from typing import TYPE_CHECKING

from azure.core.pipeline.policies import HeadersPolicy
from azure.core.tracing.decorator_async import distributed_trace_async
from .._generated.aio import SearchServiceClient as _SearchServiceClient
from ..._version import VERSION

if TYPE_CHECKING:
    # pylint:disable=unused-import,ungrouped-imports
    from typing import Any, Union
    from ... import SearchApiKeyCredential


class SearchServiceClient(object):
    """A client to interact with an existing Azure search service.

    :param endpoint: The URL endpoint of an Azure search service
    :type endpoint: str
    :param credential: A credential to authorize search client requests
    :type credential: SearchApiKeyCredential

    """

    def __init__(self, endpoint, credential, **kwargs):
        # type: (str, SearchApiKeyCredential, **Any) -> None

        headers_policy = HeadersPolicy(
            {
                "api-key": credential.api_key,
                "Accept": "application/json;odata.metadata=none",
            }
        )

        self._endpoint = endpoint  # type: str
        self._client = _SearchServiceClient(
            endpoint=endpoint,
            headers_policy=headers_policy,
            sdk_moniker="search/{}".format(VERSION),
            **kwargs
        )  # type: _SearchServiceClient

    def __repr__(self):
        # type: () -> str
        return "<SearchServiceClient [endpoint={}]>".format(repr(self._endpoint))[:1024]

    @distributed_trace_async
    async def get_service_statistics(self, **kwargs):
        # type: (**Any) -> dict
        """Get service level statistics for a search service.

        """
        result = await self._client.get_service_statistics(**kwargs)
        return result.as_dict()

    async def close(self):
        # type: () -> None
        """Close the :class:`~azure.search.SearchServiceClient` session.

        """
        return await self._client.close()

    async def __aenter__(self):
        # type: () -> SearchServiceClient
        await self._client.__aenter__()  # pylint:disable=no-member
        return self

    async def __aexit__(self, *args):
        # type: (*Any) -> None
        await self._client.__aexit__(*args)  # pylint:disable=no-member

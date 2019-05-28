# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from azure.core.pipeline import PipelineRequest, PipelineResponse
from azure.core.pipeline.policies import AsyncHTTPPolicy
from azure.core.pipeline.policies.credentials import _BearerTokenCredentialPolicyBase


class AsyncBearerTokenCredentialPolicy(_BearerTokenCredentialPolicyBase, AsyncHTTPPolicy):
    # pylint:disable=too-few-public-methods
    """Adds a bearer token Authorization header to requests."""

    async def send(self, request: PipelineRequest) -> PipelineResponse:
        token = await self._credential.get_token(self._scopes) # type: ignore
        self._update_headers(request.http_request.headers, token) # type: ignore
        return await self.next.send(request) # type: ignore

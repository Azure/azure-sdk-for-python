# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from azure.core.pipeline.policies import AsyncHTTPPolicy
from azure.core.pipeline import PipelineRequest
from . import token_utils


class EntraTokenGuardPolicy(AsyncHTTPPolicy):
    """Async pipeline policy that caches the response for a given Entra token and reuses it if valid."""

    def __init__(self):
        super().__init__()
        self._entra_token_cache = None
        self._response_cache = None

    async def send(self, request: PipelineRequest):
        cache_valid, token = token_utils.is_entra_token_cache_valid(self._entra_token_cache, request)
        if cache_valid and token_utils.is_acs_token_cache_valid(self._response_cache):
            response = self._response_cache
        else:
            self._entra_token_cache = token
            response = await self.next.send(request)
            self._response_cache = response
        if response is None:
            raise RuntimeError("Failed to obtain a valid PipelineResponse in AsyncEntraTokenGuardPolicy.send")
        return response

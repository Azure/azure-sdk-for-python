# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import json
from datetime import datetime, timezone
from azure.core.pipeline.policies import HTTPPolicy, AsyncHTTPPolicy
from azure.core.pipeline import PipelineRequest


class EntraTokenGuardPolicy(HTTPPolicy):
    """A pipeline policy that caches the response for a given Entra token and reuses it if valid."""

    def __init__(self):
        super().__init__()
        self._entra_token_cache = None
        self._response_cache = None

    def send(self, request: PipelineRequest):
        cache_valid, token = self._is_entra_token_cache_valid(request)
        if cache_valid and self._is_acs_token_cache_valid():
            response = self._response_cache
        else:
            self._entra_token_cache = token
            response = self.next.send(request)
            self._response_cache = response
        if response is None:
            raise RuntimeError("Failed to obtain a valid PipelineResponse in AsyncEntraTokenGuardPolicy.send")
        return response

    def _is_entra_token_cache_valid(self, request):
        current_entra_token = request.http_request.headers.get("Authorization", "")
        cache_valid = (
                self._entra_token_cache is not None and
                current_entra_token == self._entra_token_cache
        )
        return cache_valid, current_entra_token

    def _is_acs_token_cache_valid(self):
        if self._response_cache is None or self._response_cache.http_response.status_code != 200:
            return False
        return self._is_access_token_valid()

    def _is_access_token_valid(self):
        try:
            if self._response_cache is None or self._response_cache.http_response is None:
                return False
            content = self._response_cache.http_response.text()
            data = json.loads(content)
            expires_on = data["accessToken"]["expiresOn"]
            if isinstance(expires_on, int):
                expires_on_dt = datetime.fromtimestamp(expires_on, tz=timezone.utc)
            else:
                expires_on_dt = datetime.fromisoformat(expires_on)
            return datetime.now(timezone.utc) < expires_on_dt
        except Exception:
            return False


class AsyncEntraTokenGuardPolicy(AsyncHTTPPolicy):
    """Async pipeline policy that caches the response for a given Entra token and reuses it if valid."""

    def __init__(self):
        super().__init__()
        self._entra_token_cache = None
        self._response_cache = None

    async def send(self, request: PipelineRequest):
        cache_valid, token = self._is_entra_token_cache_valid(request)
        if cache_valid and self._is_acs_token_cache_valid():
            response = self._response_cache
        else:
            self._entra_token_cache = token
            response = await self.next.send(request)
            self._response_cache = response
        if response is None:
            raise RuntimeError("Failed to obtain a valid PipelineResponse in AsyncEntraTokenGuardPolicy.send")
        return response

    def _is_entra_token_cache_valid(self, request):
        current_entra_token = request.http_request.headers.get("Authorization", "")
        cache_valid = (
                self._entra_token_cache is not None and
                current_entra_token == self._entra_token_cache
        )
        return cache_valid, current_entra_token

    def _is_acs_token_cache_valid(self):
        if self._response_cache is None or self._response_cache.http_response.status_code != 200:
            return False
        return self._is_access_token_valid()

    def _is_access_token_valid(self):
        try:
            if self._response_cache is None or self._response_cache.http_response is None:
                return False
            content = self._response_cache.http_response.text()
            data = json.loads(content)
            expires_on = data["accessToken"]["expiresOn"]
            if isinstance(expires_on, int):
                expires_on_dt = datetime.fromtimestamp(expires_on, tz=timezone.utc)
            else:
                expires_on_dt = datetime.fromisoformat(expires_on)
            return datetime.now(timezone.utc) < expires_on_dt
        except Exception:
            return False

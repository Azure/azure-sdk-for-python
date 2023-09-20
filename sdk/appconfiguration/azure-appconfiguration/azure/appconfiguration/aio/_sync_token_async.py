# --------------------------------------------------------------------------
#
# Copyright (c) Microsoft Corporation. All rights reserved.
#
# The MIT License (MIT)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the ""Software""), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED *AS IS*, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.
#
# --------------------------------------------------------------------------
from typing import Any, Dict, Optional
from asyncio import Lock
from azure.core.pipeline import PipelineRequest, PipelineResponse
from azure.core.pipeline.policies import SansIOHTTPPolicy

from .._sync_token import SyncToken


class AsyncSyncTokenPolicy(SansIOHTTPPolicy):
    """A simple policy that enable the given callback with the response.

    :keyword callback raw_response_hook: Callback function. Will be invoked on response.
    """

    def __init__(self, **kwargs: Any) -> None:  # pylint: disable=unused-argument
        self._sync_token_header = "Sync-Token"
        self._sync_tokens: Dict[str, Any] = {}
        self._lock = Lock()

    async def on_request(self, request: PipelineRequest) -> None:  # pylint: disable=invalid-overridden-method
        """This is executed before sending the request to the next policy.

        :param request: The PipelineRequest object.
        :type request: ~azure.core.pipeline.PipelineRequest
        """
        async with self._lock:
            sync_token_header = ",".join(str(x) for x in self._sync_tokens.values())
            if sync_token_header:
                request.http_request.headers.update({self._sync_token_header: sync_token_header})

    async def on_response(  # pylint: disable=invalid-overridden-method
        self, request: PipelineRequest, response: PipelineResponse
    ) -> None:
        """This is executed after the request comes back from the policy.

        :param request: The PipelineRequest object.
        :type request: ~azure.core.pipeline.PipelineRequest
        :param response: The PipelineResponse object.
        :type response: ~azure.core.pipeline.PipelineResponse
        """
        sync_token_header = response.http_response.headers.get(self._sync_token_header)
        if not sync_token_header:
            return
        sync_token_strings = sync_token_header.split(",")
        if not sync_token_strings:
            return
        for sync_token_string in sync_token_strings:
            sync_token = SyncToken.from_sync_token_string(sync_token_string)
            await self._update_sync_token(sync_token)

    async def add_token(self, full_raw_tokens: str) -> None:
        raw_tokens = full_raw_tokens.split(",")
        for raw_token in raw_tokens:
            sync_token = SyncToken.from_sync_token_string(raw_token)
            await self._update_sync_token(sync_token)

    async def _update_sync_token(self, sync_token: Optional[SyncToken]) -> None:
        if not sync_token:
            return
        async with self._lock:
            existing_token = self._sync_tokens.get(sync_token.token_id, None)
            if not existing_token:
                self._sync_tokens[sync_token.token_id] = sync_token
                return
            if existing_token.sequence_number < sync_token.sequence_number:
                self._sync_tokens[sync_token.token_id] = sync_token

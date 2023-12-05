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
from threading import Lock
from azure.core.pipeline import PipelineRequest, PipelineResponse
from azure.core.pipeline.policies import SansIOHTTPPolicy


class SyncToken:
    """The sync token structure

    :param str token_id: The id of sync token.
    :param str value: The value of sync token.
    :param int sequence_number: The sequence number of sync token.
    """

    def __init__(self, token_id, value, sequence_number):
        self.token_id = token_id
        self.value = value
        self.sequence_number = sequence_number

    def __str__(self):
        return f"{self.token_id}={self.value}"

    @classmethod
    def from_sync_token_string(cls, sync_token):
        try:
            position = sync_token.index(";sn=")
            sequence_number = int(sync_token[position + 4 :])
            id_value = sync_token[:position]
            position = id_value.index("=")
            token_id = id_value[:position]
            value = id_value[position + 1 :]
            return SyncToken(token_id, value, sequence_number)
        except ValueError:
            return None


class SyncTokenPolicy(SansIOHTTPPolicy):
    """A simple policy that enable the given callback with the response.

    :keyword callback raw_response_hook: Callback function. Will be invoked on response.
    """

    def __init__(self, **kwargs: Any) -> None:  # pylint: disable=unused-argument
        self._sync_token_header = "Sync-Token"
        self._sync_tokens: Dict[str, Any] = {}
        self._lock = Lock()

    def on_request(self, request: PipelineRequest) -> None:
        """This is executed before sending the request to the next policy.
        :param request: The PipelineRequest object.
        :type request: ~azure.core.pipeline.PipelineRequest
        """
        with self._lock:
            sync_token_header = ",".join(str(x) for x in self._sync_tokens.values())
            if sync_token_header:
                request.http_request.headers.update({self._sync_token_header: sync_token_header})

    def on_response(self, request: PipelineRequest, response: PipelineResponse) -> None:
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
            self._update_sync_token(sync_token)

    def add_token(self, full_raw_tokens: str) -> None:
        raw_tokens = full_raw_tokens.split(",")
        for raw_token in raw_tokens:
            sync_token = SyncToken.from_sync_token_string(raw_token)
            self._update_sync_token(sync_token)

    def _update_sync_token(self, sync_token: Optional[SyncToken]) -> None:
        if not sync_token:
            return
        with self._lock:
            existing_token = self._sync_tokens.get(sync_token.token_id, None)
            if not existing_token:
                self._sync_tokens[sync_token.token_id] = sync_token
                return
            if existing_token.sequence_number < sync_token.sequence_number:
                self._sync_tokens[sync_token.token_id] = sync_token

# pylint: disable=W0231
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import asyncio
from typing import Union
import base64
from functools import partial

from azure.core.polling import AsyncPollingMethod

from .._phonenumber._generated.models import (
    PhoneNumberSearch,
    PhoneNumberRelease
)

class PhoneNumberPollingAsync(AsyncPollingMethod):
    def __init__(self, is_terminated, interval=5):
        self._response = None
        self._client = None
        self._query_status = None
        self._is_terminated = is_terminated
        self._polling_interval = interval

    async def _update_status(self):
        # type: () -> None
        if self._query_status is None:
            raise Exception("this poller has not been initialized")
        self._response = await self._query_status()

    def initialize(self, client, initial_response, _):
        # type: (Any, Any, Callable) -> None
        self._client = client
        self._response = initial_response
        self._query_status = partial(self._client.get_search_by_id, search_id=initial_response.search_id)

    async def run(self):
        # type: () -> None
        while not self.finished():
            await self._update_status()
            if not self.finished():
                await asyncio.sleep(self._polling_interval)

    def finished(self):
        # type: () -> bool
        if self._response.status is None:
            return False
        return self._is_terminated(self._response.status)

    def resource(self):
        # type: () -> Union[PhoneNumberSearch, PhoneNumberRelease]
        if not self.finished():
            return None
        return self._response

    def status(self):
        # type: () -> str
        return self._response.status

    def get_continuation_token(self):
        # type() -> str
        import pickle
        return base64.b64encode(pickle.dumps(self._response)).decode('ascii')

    @classmethod
    def from_continuation_token(cls, continuation_token, **kwargs):
        # type(str, Any) -> Tuple
        try:
            client = kwargs["client"]
        except KeyError:
            raise ValueError("Need kwarg 'client' to be recreated from continuation_token")
        import pickle
        initial_response = pickle.loads(base64.b64decode(continuation_token))  # nosec
        return client, initial_response, None

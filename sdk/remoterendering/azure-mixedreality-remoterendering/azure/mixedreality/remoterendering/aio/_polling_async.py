# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
import asyncio
import base64
from functools import partial
from typing import Any, Callable, Union

from azure.core.polling import AsyncPollingMethod
from azure.core.exceptions import HttpResponseError, ODataV4Format

from .._generated.aio import RemoteRenderingRestClient
from .._generated.models import (AssetConversion,
                                 AssetConversionStatus,
                                 RenderingSession,
                                 RenderingSessionStatus)

class RemoteRenderingPollingAsync(AsyncPollingMethod):
    """ABC class for remote rendering operations.
    """

    def __init__(self, account_id: str, is_terminated: Callable, polling_interval: int=5) -> None:
        self._account_id = account_id
        self._response: Union[AssetConversion, RenderingSession, None] = None
        self._client: Union[RemoteRenderingRestClient, None] = None
        self._query_status: Union[partial, None] = None
        self._is_terminated = is_terminated
        self._polling_interval = polling_interval

    async def _update_status(self) -> None:
        if self._query_status is None:
            raise RuntimeError("this poller has not been initialized")
        self._response = await self._query_status()  # pylint: disable=E1102
        if self._response is not None and self._response.error is not None:
            error = HttpResponseError("Polling returned a status indicating an error state.", model=self._response)
            error.error = ODataV4Format(self._response.error.serialize())
            raise error

    def initialize(self, client: Any, initial_response: Any, deserialization_callback: Callable) -> None:
        self._client = client
        self._response = initial_response

    async def run(self) -> None:
        while not self.finished():
            await self._update_status()
            if not self.finished():
                await asyncio.sleep(self._polling_interval)

    def status(self) -> str:
        raise NotImplementedError("This method needs to be implemented in a derived class.")

    def finished(self) -> bool:
        if self._response is None:
            return False
        if self._response.status is None:
            return False
        return self._is_terminated(self._response.status)

    def resource(self) -> Union[AssetConversion, RenderingSession, None]:
        if not self.finished():
            return None
        return self._response

    def get_continuation_token(self) -> str:
        # returns a Base64 encoded string of "<version>:<account_id>:<session_id/conversion_id>"
        token_str = "1:"+self._account_id+":"+self._response.id # type: ignore
        encoded = token_str.encode('ascii')
        base64_endcoded = base64.b64encode(encoded)
        return base64_endcoded.decode('ascii')


class ConversionPollingAsync(RemoteRenderingPollingAsync):
    def __init__(self, account_id: str, polling_interval: int=5) -> None:
        def is_terminated(status):
            return status in [
                AssetConversionStatus.FAILED,
                AssetConversionStatus.SUCCEEDED
            ]
        super(ConversionPollingAsync, self).__init__(account_id=account_id,
                                                     is_terminated=is_terminated,
                                                     polling_interval=polling_interval)

    def initialize(self,
                   client: RemoteRenderingRestClient,
                   initial_response: AssetConversion,
                   deserialization_callback: Callable) -> None:
        super().initialize(client, initial_response, deserialization_callback)
        if self._client is not None:
            self._query_status = partial(
                self._client.remote_rendering.get_conversion,
                account_id=self._account_id,
                conversion_id=initial_response.id)

    def status(self) -> str:
        if self._response is None:
            return AssetConversionStatus.NOT_STARTED
        return self._response.status

    @classmethod
    async def initial_response_from_continuation_token(cls,
                                                       continuation_token: str,
                                                       client: RemoteRenderingRestClient,
                                                       **kwargs) -> AssetConversion:

        version, account_id, conversion_id = base64.b64decode(
            continuation_token.encode('ascii')).decode('ascii').split(":")

        if version != "1":
            raise ValueError("Cannot continue from continuation token from a different/newer client version.")

        initial_response = await client.remote_rendering.get_conversion(
            account_id=account_id,
            conversion_id=conversion_id,
            **kwargs)

        return initial_response


class SessionPollingAsync(RemoteRenderingPollingAsync):
    def __init__(self, account_id: str, polling_interval: int=2) -> None:
        def is_terminated(status):
            return status in [
                RenderingSessionStatus.EXPIRED,
                RenderingSessionStatus.ERROR,
                RenderingSessionStatus.STOPPED,
                RenderingSessionStatus.READY
            ]
        super(SessionPollingAsync, self).__init__(account_id=account_id,
                                                  is_terminated=is_terminated,
                                                  polling_interval=polling_interval)

    def initialize(self,
                   client: RemoteRenderingRestClient,
                   initial_response: RenderingSession,
                   deserialization_callback: Callable) -> None:
        super().initialize(client, initial_response, deserialization_callback)
        if self._client is not None:
            self._query_status = partial(
                self._client.remote_rendering.get_session, account_id=self._account_id, session_id=initial_response.id)

    def status(self) -> str:
        if self._response is None:
            return RenderingSessionStatus.STARTING
        return self._response.status

    @classmethod
    async def initial_response_from_continuation_token(cls,
                                                       continuation_token: str,
                                                       client: RemoteRenderingRestClient,
                                                       **kwargs) -> RenderingSession:

        version, account_id, session_id = base64.b64decode(
            continuation_token.encode('ascii')).decode('ascii').split(":")

        if version != "1":
            raise ValueError("Cannot continue from continuation token from a different/newer client version.")

        initial_response = await client.remote_rendering.get_session(
            account_id=account_id,
            session_id=session_id,
            **kwargs)

        return initial_response

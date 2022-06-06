# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
import base64
import time
from functools import partial
from typing import TYPE_CHECKING

from azure.core.polling import PollingMethod
from azure.core.exceptions import HttpResponseError, ODataV4Format

from ._generated.models import (AssetConversion, AssetConversionStatus,
                                RenderingSession, RenderingSessionStatus)

# pylint: disable=unsubscriptable-object
if TYPE_CHECKING:
    # pylint: disable=unused-import,ungrouped-imports
    from typing import Any, Callable, Union

    from azure.core.credentials import TokenCredential

    from ._generated import RemoteRenderingRestClient


class RemoteRenderingPolling(PollingMethod):
    """ Abstract base class for polling.
    """

    def __init__(self, account_id, is_terminated, polling_interval=5):
        # type: (str, Callable, int) -> None
        self._account_id = account_id
        self._response = None  # type: Union[AssetConversion, RenderingSession, None]
        self._client = None  # type: Union[RemoteRenderingRestClient, None]
        self._query_status = None
        self._is_terminated = is_terminated
        self._polling_interval = polling_interval

    def _update_status(self):
        # type: () -> None
        if self._query_status is None:
            raise Exception("this poller has not been initialized")
        self._response = self._query_status()  # pylint: disable=E1102
        if self._response.error is not None:
            error = HttpResponseError("Polling returned a status indicating an error state.", model=self._response)
            error.error = ODataV4Format(self._response.error.serialize())
            raise error

    def initialize(self, client, initial_response, deserialization_callback):
        # type: (Any, Any, Callable) -> None
        self._client = client
        self._response = initial_response

    def run(self):
        # type: () -> None
        while not self.finished():
            self._update_status()
            if not self.finished():
                time.sleep(self._polling_interval)

    def status(self):
        # type: () -> str
        raise NotImplementedError("This method needs to be implemented")

    def finished(self):
        # type: () -> bool
        if self._response is None:
            return False
        if self._response.status is None:
            return False
        return self._is_terminated(self._response.status)

    def resource(self):
        # type: () -> Union[AssetConversion, RenderingSession, None]
        if not self.finished():
            return None
        return self._response

    def get_continuation_token(self):
        # type() -> str

        # returns a Base64 encoded string of "<version>:<account_id>:<session_id/conversion_id>"
        return base64.b64encode(("1:"+self._account_id+":"+self._response.id).encode('ascii')).decode('ascii')


class ConversionPolling(RemoteRenderingPolling):
    def __init__(self, account_id, polling_interval=5):
        # type: (str, int) -> None
        def is_terminated(status):
            return status in [
                AssetConversionStatus.FAILED,
                AssetConversionStatus.SUCCEEDED
            ]

        super(ConversionPolling, self).__init__(account_id=account_id,
                                                is_terminated=is_terminated,
                                                polling_interval=polling_interval)

    def initialize(self, client, initial_response, deserialization_callback):
        # type: (Any, Any, Any, Callable) -> None
        super(ConversionPolling, self).initialize(client=client,
                                                  initial_response=initial_response,
                                                  deserialization_callback=deserialization_callback)
        self._query_status = partial(
            self._client.remote_rendering.get_conversion,
            account_id=self._account_id,
            conversion_id=initial_response.id)

    def status(self):
        # type: () -> str
        if self._response is None:
            return AssetConversionStatus.NOT_STARTED
        return self._response.status

    @classmethod
    def from_continuation_token(cls, continuation_token, client, **kwargs):  # pylint: disable=W0221
        # type(str, RemoteRenderingRestClient, Any) -> Tuple

        version, account_id, conversion_id = base64.b64decode(
            continuation_token.encode('ascii')).decode('ascii').split(":")

        if version != "1":
            raise ValueError("Cannot continue from continuation token from a different/newer client version.")

        initial_response = client.remote_rendering.get_conversion(
            account_id=account_id,
            conversion_id=conversion_id,
            **kwargs)

        return client, initial_response, None


class SessionPolling(RemoteRenderingPolling):
    def __init__(self, account_id, polling_interval=2):
        # type: (str, int) -> None
        def is_terminated(status):
            return status in [
                RenderingSessionStatus.EXPIRED,
                RenderingSessionStatus.ERROR,
                RenderingSessionStatus.STOPPED,
                RenderingSessionStatus.READY
            ]
        super(SessionPolling, self).__init__(account_id=account_id,
                                             is_terminated=is_terminated,
                                             polling_interval=polling_interval)

    def initialize(self, client, initial_response, deserialization_callback):
        # type: (Any, Any, Any, Callable) -> None
        super(SessionPolling, self).initialize(client, initial_response, deserialization_callback)
        self._query_status = partial(
            self._client.remote_rendering.get_session, account_id=self._account_id, session_id=initial_response.id)

    def status(self):
        # type: () -> str
        if self._response is None:
            return RenderingSessionStatus.STARTING
        return self._response.status

    @classmethod
    def from_continuation_token(cls, continuation_token, client, **kwargs):  # pylint: disable=W0221
        # type(str, RemoteRenderingRestClient, Any) -> Tuple

        version, account_id, session_id = base64.b64decode(
            continuation_token.encode('ascii')).decode('ascii').split(":")

        if version != "1":
            raise ValueError("Cannot continue from continuation token from a different/newer client version.")

        initial_response = client.remote_rendering.get_session(
            account_id=account_id,
            session_id=session_id,
            **kwargs)

        return client, initial_response, None

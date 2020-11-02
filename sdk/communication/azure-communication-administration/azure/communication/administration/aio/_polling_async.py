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
    PhoneNumberReservation,
    PhoneNumberRelease
)

class PhoneNumberBasePollingAsync(AsyncPollingMethod):
    """ABC class for reserve/purchase/release phone number related polling.
    """
    def __init__(self, is_terminated, polling_interval=5):
        # type: (bool, int) -> None
        self._response = None
        self._client = None
        self._query_status = None
        self._is_terminated = is_terminated
        self._polling_interval = polling_interval

    async def _update_status(self):
        # type: () -> None
        if self._query_status is None:
            raise Exception("this poller has not been initialized")
        self._response = await self._query_status()  # pylint: disable=E1102

    def initialize(self, client, initial_response, deserialization_callback):
        # type: (Any, Any, Callable) -> None
        self._client = client
        self._response = initial_response

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
        # type: () -> Union[PhoneNumberReservation, PhoneNumberRelease]
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
    def from_continuation_token(cls, continuation_token, client, **kwargs):  # pylint: disable=W0221
        # type(str, PhoneNumberAdministrationClient, Any) -> Tuple
        import pickle
        initial_response = pickle.loads(base64.b64decode(continuation_token))  # nosec
        return client, initial_response, None

class ReservePhoneNumberPollingAsync(PhoneNumberBasePollingAsync):
    def initialize(self, client, initial_response, deserialization_callback):
        # type: (Any, Any, Callable) -> None
        super().initialize(client, initial_response, deserialization_callback)
        self._query_status = partial(self._client.get_search_by_id, search_id=initial_response.reservation_id)

class PurchaseReservationPollingAsync(PhoneNumberBasePollingAsync):
    def initialize(self, client, initial_response, deserialization_callback):
        # type: (Any, Any, Callable) -> None
        super().initialize(client, initial_response, deserialization_callback)
        self._query_status = partial(self._client.get_search_by_id, search_id=initial_response.reservation_id)

class ReleasePhoneNumberPollingAsync(PhoneNumberBasePollingAsync):
    def initialize(self, client, initial_response, deserialization_callback):
        # type: (Any, Any, Callable) -> None
        super().initialize(client, initial_response, deserialization_callback)
        self._query_status = partial(self._client.get_release_by_id, release_id=initial_response.release_id)

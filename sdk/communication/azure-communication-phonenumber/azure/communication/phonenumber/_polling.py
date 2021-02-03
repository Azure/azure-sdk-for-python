# pylint: disable=W0231
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import base64
import time
from typing import Union
from functools import partial
import pickle

from azure.core.polling import (
    PollingMethod
)
from ._phonenumber._generated.models import (
    PhoneNumberReservation,
    PhoneNumberRelease
)

class PhoneNumberBasePolling(PollingMethod):
    """ABC class for reserve/purchase/release phone number related polling.
    """
    def __init__(self, is_terminated, polling_interval=5):
        # type: (bool, int) -> None
        self._response = None
        self._client = None
        self._query_status = None
        self._is_terminated = is_terminated
        self._polling_interval = polling_interval

    def _update_status(self):
        # type: () -> None
        if self._query_status is None:
            raise Exception("this poller has not been initialized")
        self._response = self._query_status()  # pylint: disable=E1102

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
        return base64.b64encode(pickle.dumps(self._response)).decode('ascii')

    @classmethod
    def from_continuation_token(cls, continuation_token, client, **kwargs):  # pylint: disable=W0221
        # type(str, PhoneNumberAdministrationClient, Any) -> Tuple
        initial_response = pickle.loads(base64.b64decode(continuation_token))  # nosec
        return client, initial_response, None

class ReservePhoneNumberPolling(PhoneNumberBasePolling):
    def initialize(self, client, initial_response, deserialization_callback):
        # type: (Any, Any, Callable) -> None
        super().initialize(client, initial_response, deserialization_callback)
        self._query_status = partial(self._client.get_search_by_id, search_id=initial_response.reservation_id)

class PurchaseReservationPolling(PhoneNumberBasePolling):
    def initialize(self, client, initial_response, deserialization_callback):
        # type: (Any, Any, Callable) -> None
        super().initialize(client, initial_response, deserialization_callback)
        self._query_status = partial(self._client.get_search_by_id, search_id=initial_response.reservation_id)

class ReleasePhoneNumberPolling(PhoneNumberBasePolling):
    def initialize(self, client, initial_response, deserialization_callback):
        # type: (Any, Any, Callable) -> None
        super().initialize(client, initial_response, deserialization_callback)
        self._query_status = partial(self._client.get_release_by_id, release_id=initial_response.release_id)

# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""

import json
import time
from typing import Any, Callable, Iterator, List, Optional, cast

from azure.core.exceptions import HttpResponseError
from azure.core.polling import PollingMethod, LROPoller

from azure.codetransparency._operations._operations import (
    _CodeTransparencyClientOperationsMixin as GeneratedOperationsMixin,
)

from azure.codetransparency.cbor import (
    CBORDecoder,
)

__all__: List[str] = [
    "_CodeTransparencyClientOperationsMixin"
]  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """


class OperationPollingMethod(PollingMethod):
    """Polling method for operations responses"""

    def __init__(
        self,
        operation: Callable[[], Optional[bytes]],
        polling_interval_s: float,
    ):
        self._operation = operation
        self._polling_interval_s = polling_interval_s
        self._deserialization_callback = None
        self._status = "constructed"
        self._latest_response: Optional[bytes] = None

    def initialize(
        self, client, initial_response, deserialization_callback
    ):  # pylint: disable=unused-argument
        self._evaluate_response(initial_response)
        self._deserialization_callback = deserialization_callback

    def run(self) -> None:
        try:
            while not self.finished():
                response = self._operation()
                self._evaluate_response(response)
                if not self.finished():
                    time.sleep(self._polling_interval_s)
        except Exception:
            self._status = "failed"
            raise

    def _evaluate_response(self, response: Optional[bytes]) -> None:
        if response is None:
            return
        # {"OperationId": "some transaction num", "Status": "running"}
        # Status can be running, failed, succeeded
        decoded = CBORDecoder(response).decode()
        status = decoded.get("Status", None)
        if status == "succeeded":
            self._status = "finished"
        elif status == "failed":
            self._status = "failed"
        else:
            self._status = "polling"
        self._latest_response = response

    def status(self) -> str:
        return self._status

    def finished(self) -> bool:
        return self.status() in {"finished", "failed"}

    def resource(self):
        if self._deserialization_callback:
            return self._deserialization_callback(self._latest_response)
        return self._latest_response


def _error_from_response(
        http_response, body: Iterator[bytes]
) -> HttpResponseError:
    # decode response based on content-type
    # cbor when application/cbor or application/concise-problem-details+cbor
    body_bytes = b"".join(body)
    if len(body_bytes) > 0 and (
        http_response.headers.get("Content-Type", "") == "application/cbor"
        or http_response.headers.get("Content-Type", "")
        == "application/concise-problem-details+cbor"
    ):
        decoded = CBORDecoder(body_bytes).decode()
        error_title = decoded.get(-1, "Error response received")
        error_details = decoded.get(-2, None)
        return HttpResponseError(
            message=error_title,
            response=http_response,
            error=error_details,
        )
    if http_response.headers.get("Content-Type", "") == "application/json":
        return HttpResponseError(
            message="Error response received",
            response=http_response,
            error=json.loads(body_bytes.decode("utf-8")),
        )
    return HttpResponseError(
        message="Error response received",
        response=http_response,
    )


def _check_response_status(
    http_response, body: Iterator[bytes], expected_status_codes: List[int]
) -> None:
    if http_response.status_code not in expected_status_codes:
        raise _error_from_response(http_response, body)


class _CodeTransparencyClientOperationsMixin(GeneratedOperationsMixin):

    # Patch all the methods to make sure each of them raises an error with the details from the CBOR response.
    # This is needed because the generated code does not decode the CBOR error messages.
    ####################################################################

    def get_transparency_config_cbor(self, **kwargs: Any) -> Iterator[bytes]:
        kwargs["cls"] = lambda pipeline, body, headers: [
            pipeline.http_response,
            body,
        ]
        resp, iter_body = super(
            _CodeTransparencyClientOperationsMixin, self
        ).get_transparency_config_cbor(**kwargs)
        _check_response_status(
            resp, iter_body, expected_status_codes=[200]  # type: ignore
        )
        return iter_body  # type: ignore

    def get_public_keys(self, **kwargs: Any) -> Iterator[bytes]:
        kwargs["cls"] = lambda pipeline, body, headers: [
            pipeline.http_response,
            body,
        ]
        resp, iter_body = super(
            _CodeTransparencyClientOperationsMixin, self
        ).get_public_keys(**kwargs)
        _check_response_status(
            resp, iter_body, expected_status_codes=[200]  # type: ignore
        )
        return iter_body  # type: ignore

    def create_entry(self, body: bytes, **kwargs: Any) -> Iterator[bytes]:
        kwargs["cls"] = lambda pipeline, iter_body, headers: [
            pipeline.http_response,
            iter_body,
        ]
        resp, iter_body = super(
            _CodeTransparencyClientOperationsMixin, self
        ).create_entry(body, **kwargs)
        _check_response_status(
            resp, iter_body, expected_status_codes=[201, 202]  # type: ignore
        )
        return iter_body  # type: ignore

    def get_operation(self, operation_id: str, **kwargs: Any) -> Iterator[bytes]:
        kwargs["cls"] = lambda pipeline, iter_body, headers: [
            pipeline.http_response,
            iter_body,
        ]
        resp, iter_body = super(
            _CodeTransparencyClientOperationsMixin, self
        ).get_operation(
            operation_id, **kwargs
        )  # type: ignore
        _check_response_status(
            resp, iter_body, expected_status_codes=[200, 202]  # type: ignore
        )
        return iter_body  # type: ignore

    def get_entry(self, entry_id: str, **kwargs: Any) -> Iterator[bytes]:
        kwargs["cls"] = lambda pipeline, iter_body, headers: [
            pipeline.http_response,
            iter_body,
        ]
        resp, iter_body = super(_CodeTransparencyClientOperationsMixin, self).get_entry(
            entry_id, **kwargs
        )
        _check_response_status(
            resp, iter_body, expected_status_codes=[200]  # type: ignore
        )
        return iter_body  # type: ignore

    def get_entry_statement(self, entry_id: str, **kwargs: Any) -> Iterator[bytes]:
        kwargs["cls"] = lambda pipeline, iter_body, headers: [
            pipeline.http_response,
            iter_body,
        ]
        resp, iter_body = super(
            _CodeTransparencyClientOperationsMixin, self
        ).get_entry_statement(entry_id, **kwargs)
        _check_response_status(
            resp, iter_body, expected_status_codes=[200]  # type: ignore
        )
        return iter_body  # type: ignore

    # Add LRO methods for long-running operations
    ####################################################################

    def begin_create_entry(
        self,
        entry: bytes,
        **kwargs: Any,
    ) -> LROPoller[bytes]:
        """Writes an entry and returns a poller to wait for it to be durably committed. The
        poller returns the result for the initial call to create the entry.

        :param entry: Entry in the form of CoseSign1 message. Required.
        :type entry: bytes
        :return: Operation in CBOR format.
        :rtype: ~azure.core.polling.LROPoller[bytes]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

        # Pop arguments that are unexpected in the pipeline.
        polling = kwargs.pop("polling", True)
        lro_delay = kwargs.pop("polling_interval", 0.8)

        operation_body = self.create_entry(entry, **kwargs)

        operation_body_bytes = b"".join(operation_body)

        decoded = CBORDecoder(operation_body_bytes).decode()
        if decoded.get("Status", None) == "failed":
            raise ValueError("Create entry operation failed.")

        operation_id = decoded.get("OperationId", None)
        if operation_id is None:
            raise ValueError("Create entry operation ID missing.")

        kwargs["polling"] = polling
        kwargs["polling_interval"] = lro_delay
        kwargs["_create_entry_response"] = operation_body_bytes
        return self.begin_wait_for_operation(operation_id, **kwargs)

    def begin_wait_for_operation(
        self,
        operation_id,  # type: str
        **kwargs,  # type: Any
    ) -> LROPoller[bytes]:
        """Creates a poller that queries the state of the specified operation until it is
        complete, a state that indicates the transaction is durably stored in the Confidential
        Ledger.

        :param operation_id: Identifies async operation. Required.
        :type operation_id: str
        :return: An instance of LROPoller returning a Operation object describing the Entry status.
        :rtype: ~azure.core.polling.LROPoller[bytes]
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        _ = kwargs.pop("polling", True)
        lro_delay = kwargs.pop("polling_interval", 0.8)

        def operation() -> bytes:
            op = self.get_operation(operation_id=operation_id, **kwargs)
            op_bytes = b"".join(op)
            return op_bytes

        post_result: Optional[bytes] = kwargs.pop("_create_entry_response", None)

        initial_response = operation() if post_result is None else post_result

        polling_method = cast(
            PollingMethod,
            OperationPollingMethod(operation, lro_delay),
        )

        return LROPoller(
            client=self,
            initial_response=initial_response,
            deserialization_callback=lambda x: x,  # returning the result as-is
            polling_method=polling_method,
        )

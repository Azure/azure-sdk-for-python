# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""

import time
from typing import Any, Callable, IO, Iterator, List, Optional, Union, cast, Tuple

from azure.core.exceptions import HttpResponseError
from azure.core.polling import PollingMethod, LROPoller, NoPolling

from azure.codetransparency._operations._operations import (
    _CodeTransparencyClientOperationsMixin as GeneratedOperationsMixin,
)
from azure.codetransparency._operations._operations import ClsType
import azure.codetransparency.models as _models

from azure.codetransparency import (
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
        operation: Callable[[], Optional[Iterator[bytes]]],
        polling_interval_s: float,
    ):
        self._operation = operation
        self._polling_interval_s = polling_interval_s
        self._deserialization_callback = None
        self._status = "constructed"
        self._latest_response: Optional[Iterator[bytes]] = None

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

    def _evaluate_response(self, response: Optional[Iterator[bytes]]) -> None:
        if response is None:
            return
        # {"OperationId": "some transaction num", "Status": "running"}
        # Status can be running, failed, succeeded
        decoded = CBORDecoder.from_response(response).decode()
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


class Error503PollingMethod(PollingMethod):
    """Polling method for retriable 503 responses"""

    def __init__(
        self,
        operation: Callable[[], Tuple[int, Optional[Any]]],
        polling_interval_s: float,
    ):
        self._operation = operation
        self._polling_interval_s = polling_interval_s
        self._deserialization_callback = None
        self._status = "constructed"
        self._latest_response: Optional[Any] = None

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

    def _evaluate_response(self, response: Tuple[int, Optional[Any]]) -> None:
        status_code = response[0]
        if status_code >= 200 and status_code < 300:
            self._status = "finished"
        elif status_code == 503:
            self._status = "polling"
        else:
            self._status = "failed"
        self._latest_response = response[1]

    def status(self) -> str:
        return self._status

    def finished(self) -> bool:
        return self.status() in {"finished", "failed"}

    def resource(self):
        if self._deserialization_callback:
            return self._deserialization_callback(self._latest_response)
        return self._latest_response


class _CodeTransparencyClientOperationsMixin(GeneratedOperationsMixin):
    def begin_get_entry(
        self, entry_id: str, **kwargs: Any
    ) -> LROPoller[Iterator[bytes]]:
        """Returns a poller to fetch the ledger entry at the specified transaction id.

        To return older ledger entries, the relevant sections of the ledger must be
         read from disk and validated. To prevent blocking within the enclave, the
         response will indicate whether the entry is ready and part of the response, or
         if the loading is still ongoing.

         :param transaction_id: Identifies a write transaction. Required.
         :type transaction_id: str
         :return: An instance of LROPoller that returns a LedgerQueryResult object for the ledger entry.
         :rtype: ~azure.core.polling.LROPoller[~azure.confidentialledger.models.LedgerQueryResult]
         :raises ~azure.core.exceptions.HttpResponseError:
        """
        lro_delay = kwargs.pop("polling_interval", 0.5)

        def operation() -> Tuple[int, Optional[Iterator[bytes]]]:
            kwargs["cls"] = lambda pipeline, body, headers: [
                pipeline.http_response.status_code,
                body,
            ]
            val = super(_CodeTransparencyClientOperationsMixin, self).get_entry(
                entry_id, **kwargs
            )
            return val  # type: ignore

        initial_response = operation()

        polling_method = cast(
            PollingMethod, Error503PollingMethod(operation, lro_delay)
        )

        return LROPoller(
            client=self,
            initial_response=initial_response,
            deserialization_callback=lambda x: x,  # returning the result as-is
            polling_method=polling_method,
        )

    def begin_get_entry_statement(
        self, transaction_id: str, **kwargs: Any
    ) -> LROPoller[Iterator[bytes]]:
        """Returns a poller for getting a receipt certifying ledger contents at a particular
        transaction id.

        :param transaction_id: Identifies a write transaction. Required.
        :type transaction_id: str
        :return: An instance of LROPoller that returns a TransactionReceipt object for the receipt.
        :rtype: ~azure.core.polling.LROPoller[Iterator[bytes]]
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        lro_delay = kwargs.pop("polling_interval", 0.5)

        def operation() -> Tuple[int, Optional[Iterator[bytes]]]:
            kwargs["cls"] = lambda pipeline, body, headers: [
                pipeline.http_response.status_code,
                body,
            ]
            val = super(
                _CodeTransparencyClientOperationsMixin, self
            ).get_entry_statement(transaction_id=transaction_id, **kwargs)
            return val  # type: ignore

        initial_response = operation()

        polling_method = cast(
            PollingMethod, Error503PollingMethod(operation, lro_delay)
        )

        return LROPoller(
            client=self,
            initial_response=initial_response,
            deserialization_callback=lambda x: x,  # returning the result as-is
            polling_method=polling_method,
        )

    def begin_create_entry(
        self,
        entry: bytes,
        **kwargs: Any,
    ) -> LROPoller[Iterator[bytes]]:
        """Writes an entry and returns a poller to wait for it to be durably committed. The
        poller returns the result for the initial call to create the entry.

        :param entry: Entry in the form of CoseSign1 message. Required.
        :type entry: bytes
        :return: Operation in CBOR format.
        :rtype: ~azure.core.polling.LROPoller[Iterator[bytes]]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

        # Pop arguments that are unexpected in the pipeline.

        polling = kwargs.pop("polling", True)  # type: Union[bool, PollingMethod]
        lro_delay = kwargs.pop("polling_interval", 0.5)

        # Pop the custom deserializer, if any, so we know the format of the response and can
        # retrieve the transactionId. Serialize the response later.

        cls = kwargs.pop("cls", None)
        kwargs["cls"] = lambda pipeline_response, cbor_response, headers: (
            pipeline_response,
            cbor_response,
            headers,
        )

        post_pipeline_response, post_result, post_headers = self.create_entry(
            entry, **kwargs
        )
        # Delete the cls because it should only apply to the create_ledger_entry response, not the
        # wait_for_commit call.
        del kwargs["cls"]

        # FIXME: check if this is an error response, e.g. 5xx or 4xx, decode CBOR error message and raise
        decoded = CBORDecoder(post_result).decode()
        if decoded.get("Status", None) == "failed":
            raise HttpResponseError(response=post_pipeline_response)

        operation_id = post_result["OperationId"]  # type: ignore

        kwargs["polling"] = polling
        kwargs["polling_interval"] = lro_delay
        kwargs["_create_entry_response"] = post_result
        return self.begin_wait_for_operation(operation_id, **kwargs)

    def begin_wait_for_operation(
        self,
        operation_id,  # type: str
        **kwargs,  # type: Any
    ) -> LROPoller[Iterator[bytes]]:
        """Creates a poller that queries the state of the specified operation until it is
        complete, a state that indicates the transaction is durably stored in the Confidential
        Ledger.

        :param operation_id: Identifies async operation. Required.
        :type operation_id: str
        :return: An instance of LROPoller returning a TransactionStatus object describing the transaction status.
        :rtype: ~azure.core.polling.LROPoller[~azure.confidentialledger.models.TransactionStatus]
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        lro_delay = kwargs.pop("polling_interval", 0.5)

        def operation() -> Optional[Iterator[bytes]]:
            return super(_CodeTransparencyClientOperationsMixin, self).get_operation(
                operation_id=operation_id, **kwargs
            )

        post_result = kwargs.pop("_create_entry_response", None)

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

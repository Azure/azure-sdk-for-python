# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""

import time
from typing import Any, Callable, IO, Iterator, List, Optional, Union, cast

from azure.core.exceptions import ResourceNotFoundError
from azure.core.polling import PollingMethod, LROPoller, NoPolling

from azure.codetransparency._operations._operations import (
    _CodeTransparencyClientOperationsMixin as GeneratedOperationsMixin,
)
from azure.codetransparency._operations._operations import ClsType
import azure.codetransparency.models as _models

__all__: List[str] = [
    "_CodeTransparencyClientOperationsMixin"
]  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """


class BaseStatePollingMethod:
    """Base polling method for methods returning responses containing a 'state' field; the polling
    completes when 'state' becomes a desired value.
    """

    def __init__(
        self,
        operation: Callable[[], Any],
        desired_state: str,
        polling_interval_s: float,
    ):
        self._operation = operation
        self._desired_state = desired_state
        self._polling_interval_s = polling_interval_s

        self._deserialization_callback = None
        self._status = "constructed"
        self._latest_response: Optional[Iterator[bytes]] = None

    def initialize(
        self, client, initial_response, deserialization_callback
    ):  # pylint: disable=unused-argument
        self._evaluate_response(initial_response)
        self._deserialization_callback = deserialization_callback

    def _evaluate_response(self, response: Optional[Iterator[bytes]]) -> None:
        # FIXME: decode CBOR
        self._status = (
            "finished"
            if response.get("state", None) == self._desired_state
            else "polling"
        )
        self._latest_response = response

    def status(self) -> str:
        return self._status

    def finished(self) -> bool:
        return self.status() in {"finished", "failed"}

    def resource(self):
        if self._deserialization_callback:
            return self._deserialization_callback(self._latest_response)
        return self._latest_response


class StatePollingMethod(BaseStatePollingMethod, PollingMethod):
    """Polling method for methods returning responses containing a 'state' field; the polling
    completes when 'state' becomes a desired value.
    """

    def __init__(
        self,
        operation: Callable[[], Iterator[bytes]],
        desired_state: str,
        polling_interval_s: float,
    ):
        super().__init__(operation, desired_state, polling_interval_s)

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
        polling = kwargs.pop("polling", True)  # type: Union[bool, PollingMethod]
        lro_delay = kwargs.pop("polling_interval", 0.5)

        # FIXME MST returns 503 if the entry is not ready yet
        def operation() -> Iterator[bytes]:
            return super(_CodeTransparencyClientOperationsMixin, self).get_entry(
                entry_id, **kwargs
            )

        #
        initial_response = operation()

        if polling is True:
            polling_method = cast(
                PollingMethod, StatePollingMethod(operation, "Ready", lro_delay, False)
            )
        elif polling is False:
            polling_method = cast(PollingMethod, NoPolling())
        else:
            polling_method = polling
        return LROPoller(self._client, initial_response, lambda x: x, polling_method)

    def begin_get_receipt(
        self, transaction_id: str, **kwargs: Any
    ) -> LROPoller[_models.TransactionReceipt]:
        """Returns a poller for getting a receipt certifying ledger contents at a particular
        transaction id.

        :param transaction_id: Identifies a write transaction. Required.
        :type transaction_id: str
        :return: An instance of LROPoller that returns a TransactionReceipt object for the receipt.
        :rtype: ~azure.core.polling.LROPoller[~azure.confidentialledger.models.TransactionReceipt]
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        polling = kwargs.pop("polling", True)  # type: Union[bool, PollingMethod]
        lro_delay = kwargs.pop("polling_interval", 0.5)

        def operation() -> JSON:
            return super(_CodeTransparencyClientOperationsMixin, self).get_receipt(
                transaction_id=transaction_id, **kwargs
            )

        initial_response = operation()

        if polling is True:
            polling_method = cast(
                PollingMethod, StatePollingMethod(operation, "Ready", lro_delay, False)
            )
        elif polling is False:
            polling_method = cast(PollingMethod, NoPolling())
        else:
            polling_method = polling
        return LROPoller(self._client, initial_response, lambda x: x, polling_method)

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
        )\

        # Delete the cls because it should only apply to the create_ledger_entry response, not the
        # wait_for_commit call.
        del kwargs["cls"]

        # FIXME: check if this is an error response, e.g. 5xx or 4xx, decode CBOR error message and raise
        # FIXME: decode CBOR response to extract operationId from map {"OperationId": "some transaction num", "Status": "running"}

        operation_id = post_result["OperationId"]  # type: ignore

        kwargs["polling"] = polling
        kwargs["polling_interval"] = lro_delay

        # if cls was provided, use it now
        if cls:
            kwargs["_create_ledger_entry_response"] = cls(
                post_pipeline_response, post_result, post_headers  # type: ignore
            )
        else:
            kwargs["_create_ledger_entry_response"] = post_result
        return self.begin_wait_for_operation(operation_id, **kwargs)

    def begin_wait_for_operation(
        self,
        operation_id,  # type: str
        **kwargs,  # type: Any
    ) -> LROPoller[Iterator[bytes]]:
        """Creates a poller that queries the state of the specified transaction until it is
        Committed, a state that indicates the transaction is durably stored in the Confidential
        Ledger.

        :param operation_id: Identifies async operation. Required.
        :type operation_id: str
        :return: An instance of LROPoller returning a TransactionStatus object describing the transaction status.
        :rtype: ~azure.core.polling.LROPoller[~azure.confidentialledger.models.TransactionStatus]
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        polling = kwargs.pop("polling", True)  # type: Union[bool, PollingMethod]
        lro_delay = kwargs.pop("polling_interval", 0.5)

        # If this poller was called from begin_create_ledger_entry, we should return the
        # create_ledger_entry response, not the transaction status.

        post_result = kwargs.pop("_create_ledger_entry_response", None)

        def deserialization_callback(x):
            return x if post_result is None else post_result

        def operation() -> Optional[Iterator[bytes]]:
            return super(_CodeTransparencyClientOperationsMixin, self).get_operation(
                operation_id=operation_id, **kwargs
            )

        if polling is True:
            polling_method = cast(
                PollingMethod,
                StatePollingMethod(operation, "Committed", lro_delay, True),
            )
        elif polling is False:
            polling_method = cast(PollingMethod, NoPolling())
        else:
            polling_method = polling
        return LROPoller(
            self._client, operation(), deserialization_callback, polling_method
        )

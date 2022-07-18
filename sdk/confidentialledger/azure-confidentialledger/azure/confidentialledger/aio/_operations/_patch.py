# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""

import asyncio
from typing import Any, Callable, IO, Coroutine, List, Optional, Union, cast

from azure.core.exceptions import ResourceNotFoundError
from azure.core.polling import AsyncLROPoller, AsyncNoPolling, AsyncPollingMethod

from azure.confidentialledger.aio._operations._operations import (
    ConfidentialLedgerClientOperationsMixin as GeneratedOperationsMixin,
)
from azure.confidentialledger.aio._operations._operations import ClsType, JSON
from azure.confidentialledger._operations._patch import BaseStatePollingMethod

__all__: List[str] = [
    "ConfidentialLedgerClientOperationsMixin"
]  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """


class AsyncStatePollingMethod(BaseStatePollingMethod, AsyncPollingMethod):
    """Polling method for methods returning responses containing a 'state' field; the polling
    completes when 'state' becomes a desired value.
    """

    def __init__(
        self,
        operation: Callable[[], Coroutine[Any, Any, JSON]],
        desired_state: str,
        polling_interval_s: float,
        retry_not_found: bool,
    ):
        super().__init__(operation, desired_state, polling_interval_s, retry_not_found)

    async def run(self) -> None:
        try:
            while not self.finished():
                try:
                    response = await self._operation()
                    self._evaluate_response(response)
                except ResourceNotFoundError:
                    # We'll allow one instance of resource not found to account for replication
                    # delay.
                    if not self._retry_not_found or self._received_not_found_exception:
                        raise

                    self._received_not_found_exception = True

                if not self.finished():
                    await asyncio.sleep(self._polling_interval_s)
        except Exception:
            self._status = "failed"
            raise


class ConfidentialLedgerClientOperationsMixin(GeneratedOperationsMixin):
    async def begin_get_ledger_entry(
        self, transaction_id: str, *, collection_id: Optional[str] = None, **kwargs: Any
    ) -> AsyncLROPoller[JSON]:
        """Returns a poller to fetch the ledger entry at the specified transaction id.

        A collection id may optionally be specified to indicate the collection from which to fetch
        the value.

        :param transaction_id: Identifies a write transaction. Required.
        :type transaction_id: str
        :keyword collection_id: The collection id. Default value is None.
        :paramtype collection_id: str
        :return: An instance of LROPoller that returns a JSON object for the ledger entry.
        :rtype: ~azure.core.polling.LROPoller[JSON]
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        polling = kwargs.pop("polling", True)  # type: Union[bool, AsyncPollingMethod]
        lro_delay = kwargs.pop("polling_interval", 0.5)

        async def operation() -> JSON:
            return await super(ConfidentialLedgerClientOperationsMixin, self).get_ledger_entry(
                transaction_id, collection_id=collection_id, **kwargs
            )

        initial_response = await operation()

        if polling is True:
            polling_method = cast(AsyncPollingMethod, AsyncStatePollingMethod(operation, "Ready", lro_delay, False))
        elif polling is False:
            polling_method = cast(AsyncPollingMethod, AsyncNoPolling())
        else:
            polling_method = polling

        return AsyncLROPoller(self._client, initial_response, None, polling_method)

    async def begin_get_receipt(self, transaction_id: str, **kwargs: Any) -> AsyncLROPoller[JSON]:
        """Returns a poller for getting a receipt certifying ledger contents at a particular
        transaction id.

        :param transaction_id: Identifies a write transaction. Required.
        :type transaction_id: str
        :return: An instance of LROPoller that returns a JSON object for the receipt.
        :rtype: ~azure.core.polling.LROPoller[JSON]
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        polling = kwargs.pop("polling", True)  # type: Union[bool, AsyncPollingMethod]
        lro_delay = kwargs.pop("polling_interval", 0.5)

        async def operation() -> JSON:
            return await super(ConfidentialLedgerClientOperationsMixin, self).get_receipt(
                transaction_id=transaction_id, **kwargs
            )

        initial_response = await operation()

        if polling is True:
            polling_method = cast(AsyncPollingMethod, AsyncStatePollingMethod(operation, "Ready", lro_delay, False))
        elif polling is False:
            polling_method = cast(AsyncPollingMethod, AsyncNoPolling())
        else:
            polling_method = polling

        return AsyncLROPoller(self._client, initial_response, None, polling_method)

    async def begin_create_ledger_entry(
        self,
        entry: Union[JSON, IO],
        *,
        collection_id: Optional[str] = None,
        **kwargs: Any,
    ) -> AsyncLROPoller[JSON]:
        """Writes a ledger entry and returns a poller to wait for it to be durably committed. The
        poller returns the result for the initial call to create the ledger entry.

        A collection id may optionally be specified.

        :param entry: Ledger entry.
        :type entry: Union[JSON, IO]
        :keyword collection_id: The collection id. Default value is None.
        :paramtype collection_id: str
        :return: An instance of LROPoller that returns a JSON object
        :rtype: ~azure.core.polling.LROPoller[JSON]
        :raises: ~azure.core.exceptions.HttpResponseError
        """

        # Pop arguments that are unexpected in the pipeline.
        polling = kwargs.pop("polling", True)  # type: Union[bool, AsyncPollingMethod]
        lro_delay = kwargs.pop("polling_interval", 0.5)

        # Pop the custom deserializer, if any, so we know the format of the response and can
        # retrieve the transactionId. Serialize the response later.
        cls = kwargs.pop("cls", None)  # type: ClsType[JSON]
        kwargs["cls"] = lambda pipeline_response, json_response, headers: (
            pipeline_response,
            {
                **json_response,
                "transactionId": headers["x-ms-ccf-transaction-id"],
            },
            headers,
        )

        post_pipeline_response, post_result, post_headers = await self.create_ledger_entry(
            entry, collection_id=collection_id, **kwargs
        )

        # Delete the cls because it should only apply to the create_ledger_entry response, not the
        # wait_for_commit call.
        del kwargs["cls"]

        transaction_id = post_result["transactionId"]  # type: ignore

        kwargs["polling"] = polling
        kwargs["polling_interval"] = lro_delay

        if cls:
            kwargs["_create_ledger_entry_response"] = cls(
                post_pipeline_response, cast(JSON, post_result), post_headers  # type: ignore
            )
        else:
            kwargs["_create_ledger_entry_response"] = post_result

        return await self.begin_wait_for_commit(transaction_id, **kwargs)

    async def begin_wait_for_commit(
        self,
        transaction_id,  # type: str
        **kwargs,  # type: Any
    ) -> AsyncLROPoller[JSON]:
        """Creates a poller that queries the state of the specified transaction until it is
        Committed, a state that indicates the transaction is durably stored in the Confidential
        Ledger.

        :param transaction_id: Identifies a write transaction. Required.
        :type transaction_id: str
        :return: An instance of LROPoller returning a JSON object describing the transaction status.
        :rtype: ~azure.core.polling.LROPoller[JSON]
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        polling = kwargs.pop("polling", True)  # type: Union[bool, AsyncPollingMethod]
        lro_delay = kwargs.pop("polling_interval", 0.5)

        # If this poller was called from begin_create_ledger_entry, we should return the
        # create_ledger_entry response, not the transaction status.
        post_result = kwargs.pop("_create_ledger_entry_response", None)
        deserialization_callback = lambda x: x if post_result is None else post_result

        async def operation() -> JSON:
            return await super(ConfidentialLedgerClientOperationsMixin, self).get_transaction_status(
                transaction_id=transaction_id, **kwargs
            )

        initial_response = await operation()

        if polling is True:
            polling_method = cast(
                AsyncPollingMethod,
                AsyncStatePollingMethod(operation, "Committed", lro_delay, True),
            )
        elif polling is False:
            polling_method = cast(AsyncPollingMethod, AsyncNoPolling())
        else:
            polling_method = polling

        return AsyncLROPoller(self._client, initial_response, deserialization_callback, polling_method)

    async def create_ledger_entry(
        self,
        entry: Union[JSON, IO],
        *,
        collection_id: Optional[str] = None,
        **kwargs: Any,
    ) -> JSON:
        """Writes a ledger entry.

        The result is the expected JSON response with an additional field
        'transactionId' which represents the transaction identifier for this write operation.

        A collection id may optionally be specified.

        :param entry: Ledger entry.
        :type entry: Union[JSON, IO]
        :keyword collection_id: The collection id. Default value is None.
        :paramtype collection_id: str
        :return: JSON object
        :rtype: JSON
        :raises: ~azure.core.exceptions.HttpResponseError

        Example:
            .. code-block:: python

                # JSON input template you can fill out and use as your body input.
                entry = {
                    "collectionId": {
                        "collectionId": "str"  # Required.
                    },
                    "contents": "str",  # Required. Contents of the ledger entry.
                    "transactionId": "str"  # Optional. A unique identifier for the state of the
                      ledger. If returned as part of a LedgerEntry, it indicates the state from which
                      the entry was read.
                }
        """

        kwargs["cls"] = kwargs.get(
            "cls",
            lambda _, json_response, headers: {
                **json_response,
                "transactionId": headers["x-ms-ccf-transaction-id"],
            },
        )
        return await super().create_ledger_entry(entry, collection_id=collection_id, **kwargs)

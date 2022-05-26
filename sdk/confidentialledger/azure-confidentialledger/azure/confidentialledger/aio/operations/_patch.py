# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
import asyncio
from typing import Any, List, Optional

from azure.confidentialledger.aio.operations._operations import (
    ConfidentialLedgerOperations as GeneratedOperations,
)
from azure.confidentialledger.aio.operations._operations import JSON

__all__: List[str] = [
    "ConfidentialLedgerOperations"
]  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """


class ConfidentialLedgerOperations(GeneratedOperations):
    async def get_ledger_entry(
        self, transaction_id: str, *, collection_id: Optional[str] = None, **kwargs: Any
    ):
        """Gets the ledger entry at the specified transaction id. A collection id may optionally be
        specified to indicate the collection from which to fetch the value.

        To return older ledger entries, the relevant sections of the ledger must be read from disk and
        validated. To prevent blocking within the enclave, the response will indicate whether the entry
        is ready and part of the response, or if the loading is still ongoing.

        :param transaction_id: Identifies a write transaction.
        :type transaction_id: str
        :keyword collection_id: The collection id. Default value is None.
        :paramtype collection_id: str
        :keyword interval: Interval, in seconds, between retries while waiting for results,
            defaults to 0.5.
        :paramtype interval: float
        :keyword max_tries: Maximum number of times to try the query, defaults to 6. Retries are
            attempted if the result is not Ready.
        :paramtype max_tries: int
        :return: JSON object
        :rtype: JSON
        :raises: ~azure.core.exceptions.HttpResponseError

        Example:
            .. code-block:: python

                # response body for status code(s): 200
                response.json() == {
                    "entry": {
                        "collectionId": {
                            "collectionId": "str"  # Required.
                        },
                        "contents": "str",  # Required. Contents of the ledger entry.
                        "transactionId": "str"  # Optional. A unique identifier for the state
                          of the ledger. If returned as part of a LedgerEntry, it indicates the state
                          from which the entry was read.
                    },
                    "state": "str"  # Required. State of a ledger query. Known values are:
                      "Loading", "Ready".
                }
        """

        interval = kwargs.pop("interval", 0.5)
        max_tries = kwargs.pop("max_tries", 6)

        ready_const = "Ready"  # Value of 'state' field when the entry is available.
        most_recent_state = None
        for _ in range(max_tries):
            result = await super().get_ledger_entry(
                transaction_id, collection_id=collection_id, **kwargs
            )
            if result["state"] == ready_const:
                return result

            most_recent_state = result["state"]
            await asyncio.sleep(interval)

        raise TimeoutError(
            "After {0} attempts, the query still had state {1}, not {2}".format(
                max_tries, most_recent_state, ready_const
            )
        )

    async def get_receipt(self, transaction_id: str, **kwargs: Any) -> JSON:
        """Gets a receipt certifying ledger contents at a particular transaction id.

        Gets a receipt certifying ledger contents at a particular transaction id.

        :param transaction_id: Identifies a write transaction.
        :type transaction_id: str
        :keyword interval: Interval, in seconds, between retries while waiting for results,
            defaults to 0.5.
        :paramtype interval: float
        :keyword max_tries: Maximum number of times to try the query, defaults to 6. Retries are
            attempted if the result is not Ready.
        :paramtype max_tries: int
        :return: JSON object
        :rtype: JSON
        :raises: ~azure.core.exceptions.HttpResponseError

        Example:
            .. code-block:: python

                # response body for status code(s): 200
                response.json() == {
                    "receipt": {
                        "cert": "str",  # Optional.
                        "leaf": "str",  # Optional.
                        "leafComponents": {
                            "claimsDigest": "str",  # Optional.
                            "commitEvidence": "str",  # Optional.
                            "writeSetDigest": "str"  # Optional.
                        },
                        "nodeId": "str",  # Required.
                        "proof": [
                            {
                                "left": "str",  # Optional. Required.
                                "right": "str"  # Optional. Required.
                            }
                        ],
                        "root": "str",  # Optional.
                        "serviceEndorsements": [
                            "str"  # Optional.
                        ],
                        "signature": "str"  # Required.
                    },
                    "state": "str",  # Required. State of a ledger query. Known values are:
                      "Loading", "Ready".
                    "transactionId": "str"  # Required. A unique identifier for the state of the
                      ledger. If returned as part of a LedgerEntry, it indicates the state from which
                      the entry was read.
                }
        """

        interval = kwargs.pop("interval", 0.5)
        max_tries = kwargs.pop("max_tries", 6)

        ready_const = "Ready"  # Value of 'state' field when the receipt is available.
        most_recent_state = None
        for _ in range(max_tries):
            result = await super().get_receipt(transaction_id=transaction_id, **kwargs)
            if result["state"] == ready_const:
                return result

            most_recent_state = result["state"]
            await asyncio.sleep(interval)

        raise TimeoutError(
            "After {0} attempts, the query still had state {1}, not {2}".format(
                max_tries, most_recent_state, ready_const
            )
        )

    async def post_ledger_entry(
        self, entry: JSON, *, collection_id: Optional[str] = None, **kwargs: Any
    ) -> JSON:
        """Writes a ledger entry.

        The result is the expected JSON response with an additional field
        'transactionId' which represents the transaction identifier for this write operation.

        A collection id may optionally be specified.

        :param entry: Ledger entry.
        :type entry: JSON
        :keyword collection_id: The collection id. Default value is None.
        :paramtype collection_id: str
        :keyword interval: Interval, in seconds, between retries, defaults to 0.5.
        :paramtype interval: float
        :keyword max_tries: Maximum number of times to try the query, defaults to 3. Retries are
            attempted if the specified transaction is not Committed yet.
        :paramtype max_tries: int
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
        return await super().post_ledger_entry(
            entry, collection_id=collection_id, **kwargs
        )

    async def post_ledger_entry_and_wait_for_commit(
        self, entry: JSON, *, collection_id: Optional[str] = None, **kwargs: Any
    ):
        """Writes a ledger entry and waits for it to be durably committed.

        The result is the expected JSON response with an additional field
        'transactionId' which represents the transaction identifier for this write operation.

        A collection id may optionally be specified.

        :param entry: Ledger entry.
        :type entry: JSON
        :keyword collection_id: The collection id. Default value is None.
        :paramtype collection_id: str
        :keyword interval: Interval, in seconds, between retries, defaults to 0.5.
        :paramtype interval: float
        :keyword max_tries: Maximum number of times to try the query, defaults to 3. Retries are
            attempted if the specified transaction is not Committed yet.
        :paramtype max_tries: int
        :return: JSON object
        :rtype: JSON
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        kwargs["interval"] = kwargs.get("interval", 0.5)
        kwargs["max_tries"] = kwargs.get("max_tries", 3)

        post_result = await self.post_ledger_entry(
            entry, collection_id=collection_id, **kwargs
        )
        transaction_id = post_result["transactionId"]

        try:
            await self.wait_until_durable(transaction_id, **kwargs)
        except TimeoutError as e:
            raise TimeoutError(
                f"Timed out while waiting for commit; however, the entry may be successfully committed eventually."
            ) from e

        return post_result

    async def wait_until_durable(
        self,
        transaction_id,  # type: str
        **kwargs,  # type: Any
    ):
        # type: (...) -> None
        """Queries the status of the specified transaction until it is Committed, indicating that
        the transaction is durably stored in the Confidential Ledger. If this state is not reached
        by `max_queries`, a TimeoutError is raised.

        :param transaction_id: Identifies the transaction to wait for.
        :type transaction_id: str
        :keyword interval: Interval, in seconds, between retries, defaults to 0.5.
        :paramtype interval: float
        :keyword max_tries: Maximum number of times to try the query, defaults to 3. Retries are
            attempted if the specified transaction is not Committed yet.
        :paramtype max_tries: int
        :return: None.
        :rtype: None
        :raises: ~azure.core.exceptions.HttpResponseError
        :raises: TimeoutError
        """

        interval = kwargs.pop("interval", 0.5)
        max_tries = kwargs.pop("max_tries", 3)

        committed_const = "Committed"
        for attempt_num in range(max_tries):
            transaction_status = await self.get_transaction_status(
                transaction_id=transaction_id, **kwargs
            )
            if transaction_status["state"] == committed_const:
                return

            if attempt_num < max_tries - 1:
                await asyncio.sleep(interval)

        raise TimeoutError(
            "Transaction {0} is not {1} yet".format(transaction_id, committed_const)
        )

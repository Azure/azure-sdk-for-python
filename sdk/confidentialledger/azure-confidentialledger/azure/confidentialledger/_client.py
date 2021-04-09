# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import time

from azure.core.tracing.decorator import distributed_trace

from ._enums import LedgerUserRole, TransactionState
from ._generated_ledger.models import ConfidentialLedgerQueryState
from ._models import (
    AppendResult,
    Constitution,
    Consortium,
    ConsortiumMember,
    EnclaveQuote,
    LedgerEnclaves,
    LedgerEntry,
    LedgerUser,
    TransactionReceipt,
    TransactionStatus,
)
from ._shared import (
    ConfidentialLedgerCertificateCredential,
    ConfidentialLedgerClientBase,
)

try:
    from typing import TYPE_CHECKING
except ImportError:
    TYPE_CHECKING = False

if TYPE_CHECKING:
    from azure.core.credentials import TokenCredential
    from azure.core.paging import ItemPaged
    from typing import Any, Union


class ConfidentialLedgerClient(ConfidentialLedgerClientBase):
    """A client for putting data into and querying data from the Confidential Ledger service.

    The `transport` parameter is typically accepted by Azure SDK clients to provide a custom
    transport stage in the pipeline. Since this client makes modifications to the default transport,
    using a custom transport will override and remove the following functionality:
        1) Authentication using a client certificate.
        2) TLS verification using the Confidential Ledger TLS certificate.

    :param str ledger_url: URL of the Confidential Ledger service.
    :param credential: A credential object for authenticating with the Confidential Ledger.
    :type credential: ~azure.confidentialledger.ConfidentialLedgerCertificateCredential
    :param str ledger_certificate_path: The path to the ledger's TLS certificate.
    :keyword api_version: Version of the Confidential Ledger API to use. Defaults to the most recent.
    :type api_version: ~azure.confidentialledger.ApiVersion
    """

    def __init__(self, ledger_url, credential, ledger_certificate_path, **kwargs):
        # type: (str, Union[ConfidentialLedgerCertificateCredential, TokenCredential], str, Any) -> None

        super(ConfidentialLedgerClient, self).__init__(
            ledger_url=ledger_url,
            credential=credential,
            ledger_certificate_path=ledger_certificate_path,
            **kwargs,
        )

    @distributed_trace
    def append_to_ledger(
        self,
        entry_contents,  # type: str
        **kwargs,  # type: Any
    ):
        # type: (...) -> AppendResult
        """Appends an entry to the Confidential Ledger.

        :param entry_contents: Text to write to the ledger.
        :type entry_contents: str
        :keyword str sub_ledger_id: Identifies the sub-ledger to append to. If none is
            specified, the service will use the service-default sub-ledger id.
        :keyword bool wait_for_commit: If True, this method will not return until the write is
            durably saved to the ledger.
        """

        sub_ledger_id = kwargs.pop("sub_ledger_id", None)
        wait_for_commit = kwargs.pop("wait_for_commit", False)

        if entry_contents is None:
            raise ValueError("entry_contents must not be a string")

        result = self._client.post_ledger_entry(
            ledger_base_url=self._ledger_url,
            contents=entry_contents,
            sub_ledger_id=sub_ledger_id,
            cls=kwargs.pop("cls", AppendResult._from_pipeline_result),
            **kwargs,
        )

        if wait_for_commit:
            self.wait_until_durable(result.transaction_id, **kwargs)

        return result

    @distributed_trace
    def create_or_update_user(
        self,
        user_id,  # type: str
        role,  # type: LedgerUserRole
        **kwargs,  # type: Any
    ):
        # type: (...) -> LedgerUser
        """Creates a new Confidential Ledger user, or updates an existing one.

        :param user_id: Identifies the user to delete. This should be an AAD object id or
            certificate fingerprint.
        :type user_id: str
        :param role: Role to assigned to the user.
        :type role: LedgerUserRole
        :return: Details of the updated ledger user.
        :rtype: ~azure.confidentialledger.LedgerUser
        :raises: ~azure.core.exceptions.HttpResponseError
        """

        if user_id is None or role is None:
            raise ValueError("user_id and role cannot be None")

        result = self._client.patch_user(
            ledger_base_url=self._ledger_url,
            user_id=user_id,
            assigned_role=role,
            **kwargs,
        )
        return LedgerUser(
            user_id=result.user_id, role=LedgerUserRole(result.assigned_role)
        )

    @distributed_trace
    def delete_user(
        self,
        user_id,  # type: str
        **kwargs,  # type: Any
    ):
        # type: (...) -> None
        """Deletes a user from the Confidential Ledger.

        :param user_id: Identifies the user to delete. This should be an AAD object id or
            certificate fingerprint.
        :type user_id: str
        :return: None
        :rtype: None
        :raises: ~azure.core.exceptions.HttpResponseError
        """

        if user_id is None:
            raise ValueError("user_id cannot be None")

        self._client.delete_user(
            ledger_base_url=self._ledger_url, user_id=user_id, **kwargs
        )

    @distributed_trace
    def get_constitution(
        self, **kwargs  # type: Any
    ):
        # type: (...) -> Constitution
        """Gets the constitution used for governance.

        The constitution is a script that assesses and applies proposals from consortium members.

        :return: The contents of the constitution and its digest.
        :rtype: ~azure.confidentialledger.Constitution
        :raises: ~azure.core.exceptions.HttpResponseError
        """

        result = self._client.get_constitution(
            ledger_base_url=self._ledger_url, **kwargs
        )
        return Constitution(script=result.script, digest=result.digest)

    @distributed_trace
    def get_consortium(
        self,
        **kwargs,  # type: Any
    ):
        # type: (...) -> Consortium
        """Gets the consortium members.

        Consortium members can manage the Confidential Ledger.

        :return: Details about the consortium.
        :rtype: ~azure.confidentialledger.Consortium
        :raises: ~azure.core.exceptions.HttpResponseError
        """

        result = self._client.get_consortium_members(
            ledger_base_url=self._ledger_url, **kwargs
        )
        return Consortium(
            members=[
                ConsortiumMember(certificate=member.certificate, member_id=member.id)
                for member in result.members
            ]
        )

    @distributed_trace
    def get_enclave_quotes(
        self,
        **kwargs,  # type: Any
    ):
        # type: (...) -> LedgerEnclaves
        """Gets enclave quotes from all nodes in the Confidential Ledger network.

        :return: Enclave quotes for nodes in the Confidential Ledger.
        :rtype: ~azure.confidentialledger.LedgerEnclaves
        :raises: ~azure.core.exceptions.HttpResponseError
        """

        result = self._client.get_enclave_quotes(
            ledger_base_url=self._ledger_url, **kwargs
        )
        return LedgerEnclaves(
            {
                quote.node_id: EnclaveQuote(
                    node_id=quote.node_id,
                    mrenclave=quote.mrenclave,
                    raw_quote=quote.raw,
                    version=quote.quote_version,
                )
                for _, quote in result.enclave_quotes.items()
            },
            result.current_node_id,
        )

    @distributed_trace
    def get_ledger_entries(
        self,
        **kwargs,  # type: Any
    ):
        # type: (...) -> ItemPaged[LedgerEntry]
        """Gets a range of entries in the ledger.

        :keyword str from_transaction_id: Transaction identifier from which to start the query.
            If this is not specified, the query begins from the first transaction.
        :keyword str to_transaction_id: Transaction identifier at which to end the query
            (inclusive). If this is not specified, the query ends at the end of the ledger.
        :keyword str sub_ledger_id: Identifies the sub-ledger to fetch the ledger entry from.
        :return: An iterable for iterating over the entries in the range.
        :rtype: ~azure.core.paging.ItemPaged[LedgerEntry]
        :raises: ~azure.core.exceptions.HttpResponseError
        """

        from_transaction_id = kwargs.pop("from_transaction_id", None)
        to_transaction_id = kwargs.pop("to_transaction_id", None)
        sub_ledger_id = kwargs.pop("sub_ledger_id", None)

        return self._client.get_ledger_entries(
            ledger_base_url=self._ledger_url,
            from_transaction_id=from_transaction_id,
            to_transaction_id=to_transaction_id,
            sub_ledger_id=sub_ledger_id,
            cls=kwargs.pop(
                "cls",
                lambda entries: [
                    LedgerEntry._from_pipeline_result(entry) for entry in entries
                ]
                if entries is not None
                else [],
            ),
            **kwargs,
        )

    @distributed_trace
    def get_ledger_entry(
        self,
        interval=0.5,  # type: float
        max_tries=6,  # type: int
        **kwargs,  # type: Any
    ):
        # type: (...) -> LedgerEntry
        """Gets an entry in the ledger.

        :param interval: Interval, in seconds, between retries while waiting for results.
        :type interval: float
        :param max_tries: Maximum number of times to try the query. Retries are attempted if the
            result is not Ready.
        :type max_tries: int
        :keyword str transaction_id: A transaction identifier. If not specified, the latest
            transaction is fetched.
        :keyword sub_ledger_id: Identifies the sub-ledger to fetch the ledger entry from.
        :return: The corresponding ledger entry.
        :rtype: ~azure.confidentialledger.LedgerEntry
        :raises: ~azure.core.exceptions.HttpResponseError
        """

        sub_ledger_id = kwargs.pop("sub_ledger_id", None)
        transaction_id = kwargs.pop("transaction_id", None)

        if transaction_id is None:
            result = self._client.get_current_ledger_entry(
                ledger_base_url=self._ledger_url, sub_ledger_id=sub_ledger_id, **kwargs
            )
            return LedgerEntry(
                transaction_id=result.transaction_id,
                contents=result.contents,
                sub_ledger_id=result.sub_ledger_id,
            )
        else:
            ready = False
            result = None
            state = None
            for _ in range(max_tries):
                result = self._client.get_ledger_entry_for_transaction_id(
                    ledger_base_url=self._ledger_url,
                    transaction_id=transaction_id,
                    sub_ledger_id=sub_ledger_id,
                    **kwargs,
                )
                ready = result.state == ConfidentialLedgerQueryState.READY
                if not ready:
                    state = result.state
                    time.sleep(interval)
                else:
                    break
            if not ready:
                raise TimeoutError(
                    "After {0} attempts, the query still had state {1}, not {2}".format(
                        max_tries, state, ConfidentialLedgerQueryState.READY
                    )
                )

            return LedgerEntry(
                transaction_id=result.entry.transaction_id,
                contents=result.entry.contents,
                sub_ledger_id=result.entry.sub_ledger_id,
            )

    @distributed_trace
    def get_transaction_receipt(
        self,
        transaction_id,  # type: str
        interval=0.5,  # type: float
        max_tries=6,  # type: int
        **kwargs,  # type: Any
    ):
        # type: (...) -> TransactionReceipt
        """Get a receipt for a specific transaction.

        :param transaction_id: Transaction identifier.
        :type transaction_id: str
        :param interval: Interval, in seconds, between retries while waiting for results.
        :type interval: float
        :param max_tries: Maximum number of times to try the query. Retries are attempted if the
            result is not Ready.
        :type max_tries: int
        :return: Receipt certifying the specified transaction.
        :rtype: ~azure.confidentialledger.TransactionReceipt
        :raises: ~azure.core.exceptions.HttpResponseError
        """

        if transaction_id is None:
            raise ValueError("transaction_id cannot be None")

        ready = False
        result = None
        state = None
        for _ in range(max_tries):
            result = self._client.get_receipt(
                ledger_base_url=self._ledger_url,
                transaction_id=transaction_id,
                **kwargs,
            )

            ready = result.state == ConfidentialLedgerQueryState.READY
            if not ready:
                state = result.state
                time.sleep(interval)
            else:
                break
        if not ready:
            raise TimeoutError(
                "After {0} attempts, the query still had state {1}, not {2}".format(
                    max_tries, state, ConfidentialLedgerQueryState.READY
                )
            )

        return TransactionReceipt(
            transaction_id=result.transaction_id, receipt=result.receipt
        )

    @distributed_trace
    def get_transaction_status(
        self,
        transaction_id,  # type: str
        **kwargs,  # type: Any
    ):
        # type: (...) -> TransactionStatus
        """Gets the status of a transaction.

        :param transaction_id: Identifier for the transaction to get the status of.
        :type transaction_id: str
        :return: Status object describing the transaction status.
        :rtype: ~azure.confidentialledger.TransactionStatus
        :raises: ~azure.core.exceptions.HttpResponseError
        """

        if transaction_id is None:
            raise ValueError("transaction_id cannot be None")

        result = self._client.get_transaction_status(
            ledger_base_url=self._ledger_url, transaction_id=transaction_id, **kwargs
        )
        return TransactionStatus(
            transaction_id=result.transaction_id, state=TransactionState(result.state)
        )

    @distributed_trace
    def get_user(
        self,
        user_id,  # type: str
        **kwargs,  # type: Any
    ):
        # type: (...) -> LedgerUser
        """Gets a Confidential Ledger user.

        :param user_id: Identifies the user to delete. This should be an AAD object id or
            certificate fingerprint.
        :type user_id: str
        :return: Details about the user.
        :rtype: ~azure.confidentialledger.LedgerUser
        :raises: ~azure.core.exceptions.HttpResponseError
        """

        if user_id is None:
            raise ValueError("user_id cannot be None")

        result = self._client.get_user(
            ledger_base_url=self._ledger_url, user_id=user_id, **kwargs
        )
        return LedgerUser(
            user_id=result.user_id, role=LedgerUserRole(result.assigned_role)
        )

    @distributed_trace
    def wait_until_durable(
        self,
        transaction_id,  # type: str
        interval=0.5,  # type: float
        max_queries=3,  # type: int
        **kwargs,  # type: Any
    ):
        # type: (...) -> None
        """Queries the status of the specified transaction until it is Committed, indicating that
        the transaction is durably stored in the Confidential Ledger. If this state is not reached
        by `max_queries`, a TimeoutError is raised.

        :param transaction_id: Identifies the transaction to wait for.
        :type transaction_id: str
        :param interval: Time, in seconds, to wait between queries.
        :type interval: float
        :param max_queries: The maximum amount of queries to make before raising an exception.
        :type max_queries: int
        :return: None.
        :rtype: None
        :raises: ~azure.core.exceptions.HttpResponseError
        """

        for attempt_num in range(max_queries):
            transaction_status = self.get_transaction_status(
                transaction_id=transaction_id, **kwargs
            )
            if transaction_status.state is TransactionState.COMMITTED:
                return

            if attempt_num < max_queries - 1:
                time.sleep(interval)

        raise TimeoutError(
            "Transaction {0} is not {1} yet".format(
                transaction_id, TransactionState.COMMITTED
            )
        )

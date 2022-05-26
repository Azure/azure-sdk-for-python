# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import time

from azure.core.tracing.decorator import distributed_trace

from ._client_base import ConfidentialLedgerClientBase
from ._enums import LedgerUserRole, TransactionState
from ._generated._generated_ledger.v0_1_preview.models import (
    ConfidentialLedgerQueryState,
)
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
)
from ._shared import (
    ConfidentialLedgerCertificateCredential,
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

    :param str endpoint: URL of the Confidential Ledger service.
    :param credential: A credential object for authenticating with the Confidential Ledger.
    :type credential: ~azure.confidentialledger.ConfidentialLedgerCertificateCredential
    :param str ledger_certificate_path: The path to the ledger's TLS certificate.
    :keyword api_version: Version of the Confidential Ledger API to use. Defaults to the most recent.
        Support API versions:
            - 0.1-preview
    :type api_version: str
    """

    def __init__(self, endpoint, credential, ledger_certificate_path, **kwargs):
        # type: (str, Union[ConfidentialLedgerCertificateCredential, TokenCredential], str, Any) -> None
        super(ConfidentialLedgerClient, self).__init__(
            endpoint=endpoint,
            credential=credential,
            ledger_certificate_path=ledger_certificate_path,
            **kwargs
        )

    @distributed_trace
    def append_to_ledger(
        self,
        entry_contents,  # type: str
        **kwargs  # type: Any
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

        wait_for_commit = kwargs.pop("wait_for_commit", False)

        if entry_contents is None:
            raise ValueError("entry_contents must be a string")

        # pylint: disable=protected-access
        result = self._client.confidential_ledger.post_ledger_entry(
            contents=entry_contents,
            # Not a valid kwarg for wait_for_commit (will throw at requests layer),
            # so it has to be popped.
            sub_ledger_id=kwargs.pop("sub_ledger_id", None),
            cls=kwargs.pop("cls", AppendResult._from_pipeline_result),
            **kwargs
        )

        if wait_for_commit:
            self.wait_until_durable(result.transaction_id, **kwargs)

        return result

    @distributed_trace
    def create_or_update_user(
        self,
        user_id,  # type: str
        role,  # type: Union[str, LedgerUserRole]
        **kwargs  # type: Any
    ):
        # type: (...) -> LedgerUser
        """Creates a new Confidential Ledger user, or updates an existing one.

        :param user_id: Identifies the user to delete. This should be an AAD object id or
            certificate fingerprint.
        :type user_id: str
        :param role: Role to assigned to the user.
        :type role: str or LedgerUserRole
        :return: Details of the updated ledger user.
        :rtype: ~azure.confidentialledger.LedgerUser
        :raises: ~azure.core.exceptions.HttpResponseError
        """

        if user_id is None or role is None:
            raise ValueError("user_id or role cannot be None")

        result = self._client.confidential_ledger.create_or_update_user(
            user_id=user_id,
            assigned_role=role.value if isinstance(role, LedgerUserRole) else role,
            **kwargs
        )
        return LedgerUser(
            user_id=result.user_id, role=LedgerUserRole(result.assigned_role)
        )

    @distributed_trace
    def delete_user(
        self,
        user_id,  # type: str
        **kwargs  # type: Any
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

        self._client.confidential_ledger.delete_user(user_id=user_id, **kwargs)

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

        result = self._client.confidential_ledger.get_constitution(**kwargs)
        return Constitution(script=result.script, digest=result.digest)

    @distributed_trace
    def get_consortium(
        self, **kwargs  # type: Any
    ):
        # type: (...) -> Consortium
        """Gets the consortium members.

        Consortium members can manage the Confidential Ledger.

        :return: Details about the consortium.
        :rtype: ~azure.confidentialledger.Consortium
        :raises: ~azure.core.exceptions.HttpResponseError
        """

        result = self._client.confidential_ledger.get_consortium_members(**kwargs)
        return Consortium(
            members=[
                ConsortiumMember(certificate=member.certificate, member_id=member.id)
                for member in result.members
            ]
        )

    @distributed_trace
    def get_enclave_quotes(
        self, **kwargs  # type: Any
    ):
        # type: (...) -> LedgerEnclaves
        """Gets enclave quotes from all nodes in the Confidential Ledger network.

        :return: Enclave quotes for nodes in the Confidential Ledger.
        :rtype: ~azure.confidentialledger.LedgerEnclaves
        :raises: ~azure.core.exceptions.HttpResponseError
        """

        result = self._client.confidential_ledger.get_enclave_quotes(**kwargs)
        return LedgerEnclaves(
            {
                quote.node_id: EnclaveQuote(
                    node_id=quote.node_id,
                    mrenclave=quote.mrenclave,
                    raw_quote=quote.raw,
                    version=quote.quote_version,
                )
                for quote in result.enclave_quotes.values()
            },
            result.current_node_id,
        )

    @distributed_trace
    def get_ledger_entries(
        self, **kwargs  # type: Any
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

        if from_transaction_id is not None:
            if not from_transaction_id:
                raise ValueError(
                    "If not None, from_transaction_id must be a non-empty string"
                )
        if to_transaction_id is not None:
            if not to_transaction_id:
                raise ValueError(
                    "If not None, to_transaction_id must be a non-empty string"
                )

        # pylint: disable=protected-access
        return self._client.confidential_ledger.get_ledger_entries(
            from_transaction_id=from_transaction_id,
            to_transaction_id=to_transaction_id,
            cls=kwargs.pop(
                "cls",
                lambda entries: [
                    LedgerEntry._from_pipeline_result(entry) for entry in entries
                ]
                if entries is not None
                else [],
            ),
            **kwargs
        )

    @distributed_trace
    def get_ledger_entry(
        self, **kwargs  # type: Any
    ):
        # type: (...) -> LedgerEntry
        """Gets an entry in the ledger. The query may need to be retried while the
        service is loading results.

        :keyword float interval: Amount of time, in seconds, to sleep between attempts, defaults to
            0.8.
        :keyword int retry_total: Total number of retries to allow. Default value is 10.
        :keyword str transaction_id: A transaction identifier. If not specified, the latest
            transaction is fetched.
        :keyword sub_ledger_id: Identifies the sub-ledger to fetch the ledger entry from.
        :return: The corresponding ledger entry.
        :rtype: ~azure.confidentialledger.LedgerEntry
        :raises: ~azure.core.exceptions.HttpResponseError
        """

        retry_backoff_factor = kwargs.pop("retry_backoff_factor", 0.8)
        retry_total = kwargs.pop("retry_total", 10)
        transaction_id = kwargs.pop("transaction_id", None)

        if transaction_id is not None:
            if not transaction_id:
                raise ValueError(
                    "If not None, transaction_id must be a non-empty string"
                )

        if transaction_id is None:
            result = self._client.confidential_ledger.get_current_ledger_entry(**kwargs)
            return LedgerEntry(
                transaction_id=result.transaction_id,
                contents=result.contents,
                sub_ledger_id=result.sub_ledger_id,
            )

        ready = False
        result = None
        state = None
        for _ in range(retry_total):
            result = self._client.confidential_ledger.get_ledger_entry(
                transaction_id=transaction_id, **kwargs
            )
            ready = result.state == ConfidentialLedgerQueryState.READY
            if not ready:
                state = result.state
                time.sleep(retry_backoff_factor)
            else:
                break
        if not ready:
            raise TimeoutError(
                "After {0} attempts, the query still had state {1}, not {2}".format(
                    retry_total, state, ConfidentialLedgerQueryState.READY
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
        **kwargs  # type: Any
    ):
        # type: (...) -> TransactionReceipt
        """Get a receipt for a specific transaction. The query may need to be retried while the
        service is loading results.

        :param transaction_id: Transaction identifier.
        :type transaction_id: str
        :keyword float interval: Interval, in seconds, between retries while waiting for results,
            defaults to 0.5.
        :keyword int max_tries: Maximum number of times to try the query, defaults to 6. Retries are
            attempted if the result is not Ready.
        :return: Receipt certifying the specified transaction.
        :rtype: ~azure.confidentialledger.TransactionReceipt
        :raises: ~azure.core.exceptions.HttpResponseError
        """

        if transaction_id is None:
            raise ValueError("transaction_id cannot be None")

        interval = kwargs.pop("interval", 0.5)
        max_tries = kwargs.pop("max_tries", 6)

        state = None
        for _ in range(max_tries):
            result = self._client.confidential_ledger.get_receipt(
                transaction_id=transaction_id, **kwargs
            )

            if (
                ConfidentialLedgerQueryState(result.state)
                is not ConfidentialLedgerQueryState.READY
            ):
                state = result.state
                time.sleep(interval)
            else:
                return TransactionReceipt(
                    transaction_id=result.transaction_id, receipt=result.receipt
                )

        raise TimeoutError(
            "After {0} attempts, the query still had state {1}, not {2}".format(
                max_tries, state, ConfidentialLedgerQueryState.READY
            )
        )

    @distributed_trace
    def get_transaction_status(
        self,
        transaction_id,  # type: str
        **kwargs  # type: Any
    ):
        # type: (...) -> TransactionState
        """Gets the status of a transaction.

        :param transaction_id: Identifier for the transaction to get the status of.
        :type transaction_id: str
        :return: Status object describing the transaction state.
        :rtype: ~azure.confidentialledger.TransactionState
        :raises: ~azure.core.exceptions.HttpResponseError
        """

        if transaction_id is None:
            raise ValueError("transaction_id cannot be None")

        result = self._client.confidential_ledger.get_transaction_status(
            transaction_id=transaction_id, **kwargs
        )
        return TransactionState(result.state)

    @distributed_trace
    def get_user(
        self,
        user_id,  # type: str
        **kwargs  # type: Any
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

        result = self._client.confidential_ledger.get_user(user_id=user_id, **kwargs)
        return LedgerUser(
            user_id=result.user_id, role=LedgerUserRole(result.assigned_role)
        )

    @distributed_trace
    def wait_until_durable(
        self,
        transaction_id,  # type: str
        **kwargs  # type: Any
    ):
        # type: (...) -> None
        """Queries the status of the specified transaction until it is Committed, indicating that
        the transaction is durably stored in the Confidential Ledger. If this state is not reached
        by `max_queries`, a TimeoutError is raised.

        :param transaction_id: Identifies the transaction to wait for.
        :type transaction_id: str
        :keyword float interval: Interval, in seconds, between retries while waiting for results,
            defaults to 0.5.
        :keyword int max_queries: Maximum number of queries to make for durability, defaults to 3.
        :return: None.
        :rtype: None
        :raises: ~azure.core.exceptions.HttpResponseError
        :raises: TimeoutError
        """

        interval = kwargs.pop("interval", 0.5)
        max_queries = kwargs.pop("max_queries", 3)

        for attempt_num in range(max_queries):
            transaction_state = self.get_transaction_status(
                transaction_id=transaction_id, **kwargs
            )
            if transaction_state is TransactionState.COMMITTED:
                return

            if attempt_num < max_queries - 1:
                time.sleep(interval)

        raise TimeoutError(
            "Transaction {0} is not {1} yet".format(
                transaction_id, TransactionState.COMMITTED
            )
        )

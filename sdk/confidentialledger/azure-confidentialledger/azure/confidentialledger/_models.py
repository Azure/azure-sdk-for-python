# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from collections import namedtuple
from typing import Dict, List

from ._enums import LedgerUserRole, TransactionState


class AppendResult(namedtuple("AppendResult", ["sub_ledger_id", "transaction_id"])):
    """Result of appending to the ledger.

    :ivar str transaction_id: Identifier for when the append transaction was registered.
    :ivar str sub_ledger_id: Identifies the sub-ledger the entry was appended to.
    """

    __slots__ = ()

    def __new__(cls, sub_ledger_id, transaction_id):
        return super(AppendResult, cls).__new__(cls, sub_ledger_id, transaction_id)

    @classmethod
    def _from_pipeline_result(cls, _, deserialized, response_headers):
        transaction_id = response_headers["x-ms-ccf-transaction-id"]
        return cls(
            transaction_id=transaction_id, sub_ledger_id=deserialized.sub_ledger_id
        )


class ConsortiumMember(object):
    """Describes a member of the consortium.

    :param certificate: Certificate used by the member.
    :type certificate: str
    :param id: The member's assigned identifier.
    :type id: str
    """

    def __init__(
        self,
        certificate,  # type: str
        member_id,  # type: str
    ):
        if not certificate or not member_id:
            raise ValueError("certificate and member_id cannot be None")

        self._certificate = certificate
        self._member_id = member_id

    @property
    def certificate(self):
        # type: () -> str
        """The member's certificate."""
        return self._certificate

    @property
    def id(self):
        # type: () -> str
        """The member's identifier."""
        return self._member_id


class Consortium(object):
    """Describes the consortium.

    :param members: List of members of the consortium.
    :type members: List[ConsortiumMember]
    """

    def __init__(
        self, members  # type: List[ConsortiumMember]
    ):
        self._members = members

    @property
    def members(self):
        # type: () -> List[ConsortiumMember]
        """Members of the consortium."""
        return self._members


class Constitution(object):
    """Governance script for the Confidential Ledger.

    :param script: Contents of the constitution script.
    :type script: str
    :param digest: SHA256 digest of the script.
    :type digest: str
    """

    def __init__(
        self,
        script,  # type: str
        digest,  # type: str
    ):
        self._script = script
        self._digest = digest

    @property
    def contents(self):
        # type: () -> str
        """The contents of the constitution."""
        return self._script

    @property
    def digest(self):
        # type: () -> str
        """SHA256 of the constitution."""
        return self._digest


class EnclaveQuote(object):
    """Quote of an SGX enclave.

    :param node_id: ID assigned to this node by CCF.
    :type node_id: int
    :param mrenclave: MRENCLAVE value of the code running in the enclave.
    :type mrenclave: str
    :param raw_quote: Raw SGX quote, parsable by tools like Open Enclave's oeverify.
    :type raw_quote: str
    :param version: Version of the quote.
    :type version: str
    """

    def __init__(
        self,
        node_id,  # type: int
        mrenclave,  # type: str
        raw_quote,  # type: str
        version,  # type: str
    ):
        self._node_id = node_id
        self._mrenclave = mrenclave
        self._raw_quote = raw_quote
        self._version = version

    @property
    def node_id(self):
        # type: () -> int
        """The ID of the node identified by this quote."""
        return self._node_id

    @property
    def mrenclave(self):
        # type: () -> str
        """The MRENCLAVE value for this enclave."""
        return self._mrenclave

    @property
    def raw_quote(self):
        # type: () -> str
        """The raw quote for this enclave."""
        return self._raw_quote

    @property
    def version(self):
        # type: () -> str
        """The version of the quote."""
        return self._version


class LedgerEnclaves(object):
    """Collection of enclaves in the ledger.

    :param quotes: Dictionary of enclaves in the Confidential Ledger.
    :type quotes: Dict[str, EnclaveQuote]
    :param source_node: Id of the node providing the quotes.
    :type source_node: str
    """

    def __init__(
        self,
        quotes,  # type: Dict[str, EnclaveQuote]
        source_node,  # type: str
    ):
        self._quotes = quotes
        self._source_node = source_node

    @property
    def quotes(self):
        # type: (...) -> Dict[str, EnclaveQuote]
        """Get a dictionary of enclaves quotes."""
        return self._quotes

    @property
    def source_node(self):
        # type: (...) -> str
        """Identifies the node that returned the contained quotes."""
        return self._source_node


class LedgerEntry(object):
    """An entry in the ledger.

    :param transaction_id: Identifier for the transaction containing this ledger entry.
    :type transaction_id: str
    :param contents: Contents of the ledger entry.
    :type contents: str
    :param sub_ledger_id: Identifies the sub-ledger the entry is a part of.
    :type sub_ledger_id: str
    """

    def __init__(
        self,
        transaction_id,  # type: str
        contents,  # type: str
        sub_ledger_id,  # type: int
    ):
        self._transaction_id = transaction_id
        self._contents = contents
        self._sub_ledger_id = sub_ledger_id

    @property
    def transaction_id(self):
        # type: () -> str
        """Id of the ledger entry."""
        return self._transaction_id

    @property
    def contents(self):
        # type: () -> str
        """Contents of the ledger entry."""
        return self._contents

    @property
    def sub_ledger_id(self):
        # type: () -> int
        """Identifies the sub-ledger this entry is a part of."""
        return self._sub_ledger_id

    @classmethod
    def _from_pipeline_result(cls, deserialized):
        # type: (...) -> LedgerEntry
        return cls(
            transaction_id=deserialized.transaction_id,
            contents=deserialized.contents,
            sub_ledger_id=deserialized.sub_ledger_id,
        )


class LedgerUser(object):
    """Models a Confidential Ledger user.

    :param user_id: Identifier of the user.
    :type user_id: str
    :param role: Role assigned to the user.
    :type role: LedgerUserRole
    """

    def __init__(
        self,
        user_id,  # type: str
        role,  # type: LedgerUserRole
    ):
        self._id = user_id
        self._role = role

    @property
    def id(self):
        # type: () -> str
        """Returns the id of this user."""
        return self._id

    @property
    def role(self):
        # type: () -> LedgerUserRole
        """Returns the role assigned to this user."""
        return self._role


class TransactionReceipt(object):
    """Contains a receipt certifying a transaction.

    :param transaction_id: Unique identifier for a transaction.
    :type transaction_id: str
    :param receipt: The receipt, which is a list of integers comprising a Merkle proof.
    :type receipt: List[int]
    """

    def __init__(
        self,
        transaction_id: str,
        receipt: List[int],
    ) -> None:
        self._transaction_id = transaction_id
        self._contents = receipt

    @property
    def contents(self):
        # type: () -> List[int]
        """Contents of the receipt."""
        return self._contents

    @property
    def transaction_id(self):
        # type: () -> str
        """Identifier for the transaction certified by this receipt."""
        return self._transaction_id


class TransactionStatus(object):
    """Represents the status of a transaction.

    :param transaction_id: Identifier for the transaction.
    :type transaction_id: str
    :param state: State of the transation.
    :type state: ~azure.confidentialledger.TransactionState
    """

    def __init__(
        self,
        transaction_id,  # type: str
        state,  # type: TransactionState
    ):
        self._transaction_id = transaction_id
        self._state = state

    @property
    def transaction_id(self):
        # type: () -> str
        """The identifier for this transaction."""
        return self._transaction_id

    @property
    def state(self):
        # type: () -> TransactionState
        """The state of the transaction."""
        return self._state

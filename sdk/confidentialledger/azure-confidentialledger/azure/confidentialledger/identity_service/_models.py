# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------


try:
    from typing import TYPE_CHECKING
except ImportError:
    TYPE_CHECKING = False

if TYPE_CHECKING:
    # pylint:disable=unused-import
    pass


class LedgerIdentity(object):
    """Contains identification information about a Confidential Ledger.

    :param ledger_id: The id of the Confidential Ledger this object identifies.
    :type ledger_id: str
    :param ledger_tls_certificate: PEM-encoded certificate used for TLS by the Confidential Ledger.
    :type ledger_tls_certificate: str
    """

    def __init__(self, ledger_id, ledger_tls_certificate):
        self._ledger_id = ledger_id
        self._ledger_tls_certificate = ledger_tls_certificate.strip("\n\u0000")

    @property
    def ledger_id(self):
        # type: () -> str
        """ "The id for this Confidential Ledger."""
        return self._ledger_id

    @property
    def ledger_tls_certificate(self):
        # type: () -> str
        """The certificate used for TLS by this network."""
        return self._ledger_tls_certificate

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
    import os
    from typing import Union


class ConfidentialLedgerCertificateCredential(object):
    """A credential for authenticating with the Confidential Ledger using a certificate.

    :param str certificate_path: Path to the PEM-encoded certificate file including the private key.
    """

    def __init__(self, certificate_path):
        # type: (Union[str, bytes, os.PathLike]) -> None
        if not certificate_path:
            raise ValueError("certificate_path must be a non-empty string")

        self.certificate_path = certificate_path

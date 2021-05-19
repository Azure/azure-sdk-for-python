import sys

from azure.confidentialledger.identity_service import (
    ConfidentialLedgerIdentityServiceClient,
    LedgerIdentity,
)

from _shared.constants import NETWORK_CERTIFICATE
from _shared.testcase import ConfidentialLedgerTestCase

LEDGER_ID = "fake-ledger-id"


class ConfidentialLedgerIdentityServiceClientTest(ConfidentialLedgerTestCase):
    def setUp(self):
        super(ConfidentialLedgerIdentityServiceClientTest, self).setUp()

        self.ledger_id = self.set_value_to_scrub("CONFIDENTIAL_LEDGER_ID", LEDGER_ID)

    def test_get_ledger_identity(self):
        client = self.create_client_from_credential(
            ConfidentialLedgerIdentityServiceClient,
            credential=None,
            identity_service_url="https://eastus.identity.confidential-ledger.core.azure.com",
        )

        network_identity = client.get_ledger_identity(
            ledger_id=self.ledger_id
        )  # type: LedgerIdentity

        self.assertEqual(network_identity.ledger_id, self.ledger_id)

        cert_recv = network_identity.ledger_tls_certificate
        # Ledger certificate comes back as unicode in Python 2.7.
        if sys.version_info < (3, 0):
            cert_recv = cert_recv.strip("\n\x00").encode("ascii")

        self.assertEqual(cert_recv, NETWORK_CERTIFICATE)

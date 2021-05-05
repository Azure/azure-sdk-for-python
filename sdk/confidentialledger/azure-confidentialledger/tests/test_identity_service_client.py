from azure.confidentialledger.identity_service import (
    ConfidentialLedgerIdentityServiceClient,
    LedgerIdentity,
)
from azure.confidentialledger._generated_identity.v0_1_preview import ConfidentialLedgerClient

from ._shared.constants import NETWORK_CERTIFICATE
from ._shared.testcase import ConfidentialLedgerTestCase

LEDGER_ID = "fake-ledger-id"


class ConfidentialLedgerIdentityServiceClientTest(ConfidentialLedgerTestCase):
    def setUp(self):
        super(ConfidentialLedgerIdentityServiceClientTest, self).setUp()

        self.ledger_id = self.set_value_to_scrub("CONFIDENTIAL_LEDGER_ID", LEDGER_ID)

    def test_get_ledger_identity(self):
        credential = self.get_credential(ConfidentialLedgerClient)
        client = self.create_client_from_credential(
            ConfidentialLedgerIdentityServiceClient,
            credential=credential,
            identity_service_url="https://identity.accledger.azure.com",
        )

        network_identity = client.get_ledger_identity(
            ledger_id=self.ledger_id
        )  # type: LedgerIdentity
        self.assertEqual(network_identity.ledger_id, self.ledger_id)
        self.assertEqual(network_identity.ledger_tls_certificate, NETWORK_CERTIFICATE)

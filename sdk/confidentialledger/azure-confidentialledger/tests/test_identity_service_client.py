from azure.identity_service import (
    ConfidentialLedgerIdentityServiceClient,
)
from devtools_testutils import AzureTestCase

from .constants import NETWORK_CERTIFICATE
from .testcase import ConfidentialLedgerPreparer


class ConfidentialLedgerIdentityServiceClientTest(AzureTestCase):
    @ConfidentialLedgerPreparer()
    def test_get_ledger_identity(self, confidentialledger_endpoint):
        client = self.create_client_from_credential(
            ConfidentialLedgerIdentityServiceClient,
            credential=None,
            identity_service_url="https://identity.confidential-ledger.core.azure.com",
        )

        ledger_id = confidentialledger_endpoint.replace("https://", "").split(".")[0]
        network_identity = client.identity_service.get_ledger_identity(ledger_id=ledger_id)

        self.assertEqual(network_identity.ledger_id, ledger_id)

        cert_recv = network_identity.ledger_tls_certificate
        self.assertEqual(cert_recv, NETWORK_CERTIFICATE)

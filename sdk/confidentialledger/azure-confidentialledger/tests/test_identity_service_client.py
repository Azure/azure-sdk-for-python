from azure.acl_identity_service import (
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
        )

        ledger_id = confidentialledger_endpoint.replace("https://", "").split(".")[0]
        network_identity = (
            client.confidential_ledger_identity_service.get_ledger_identity(
                ledger_id=ledger_id
            )
        )

        self.assertEqual(network_identity["ledgerId"], ledger_id)

        cert_recv = network_identity["ledgerTlsCertificate"]
        self.assertEqual(cert_recv, NETWORK_CERTIFICATE)

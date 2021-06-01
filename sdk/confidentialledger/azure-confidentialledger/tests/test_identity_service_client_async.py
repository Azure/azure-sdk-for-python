from devtools_testutils import AzureTestCase

from azure.confidentialledger.identity_service import LedgerIdentity
from azure.confidentialledger.identity_service.aio import (
    ConfidentialLedgerIdentityServiceClient,
)

from _shared.constants import NETWORK_CERTIFICATE
from _shared.testcase_async import AsyncConfidentialLedgerTestCase

LEDGER_ID = "fake-ledger-id"


class ConfidentialLedgerIdentityServiceClientTest(AsyncConfidentialLedgerTestCase):
    def setUp(self):
        super(ConfidentialLedgerIdentityServiceClientTest, self).setUp()

        self.ledger_id = self.set_value_to_scrub("CONFIDENTIAL_LEDGER_ID", LEDGER_ID)

    @AzureTestCase.await_prepared_test
    async def test_get_ledger_identity(self):
        client = self.create_client_from_credential(
            ConfidentialLedgerIdentityServiceClient,
            credential=None,
            identity_service_url="https://eastus.identity.confidential-ledger.core.azure.com",
        )

        network_identity = await client.get_ledger_identity(
            ledger_id=self.ledger_id
        )  # type: LedgerIdentity
        self.assertEqual(network_identity.ledger_id, self.ledger_id)
        self.assertEqual(
            network_identity.ledger_tls_certificate,
            NETWORK_CERTIFICATE,
        )

        await client.close()

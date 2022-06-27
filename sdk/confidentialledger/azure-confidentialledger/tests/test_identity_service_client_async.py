from devtools_testutils import AzureTestCase

from azure.confidentialledger_identity_service.aio import (
    ConfidentialLedgerIdentityServiceClient,
)

from .testcase import ConfidentialLedgerPreparer


class ConfidentialLedgerIdentityServiceClientTest(AzureTestCase):
    @ConfidentialLedgerPreparer()
    async def test_get_ledger_identity(self, confidentialledger_id):
        client = self.create_client_from_credential(
            ConfidentialLedgerIdentityServiceClient,
            credential=None,
        )

        try:
            network_identity = (
                await client.get_ledger_identity(
                    ledger_id=confidentialledger_id
                )
            )

            self.assertEqual(network_identity["ledgerId"], confidentialledger_id)
            self.assertTrue(network_identity["ledgerTlsCertificate"])
        finally:
            await client.close()

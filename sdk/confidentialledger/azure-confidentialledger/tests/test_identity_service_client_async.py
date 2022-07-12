from devtools_testutils import AzureTestCase

from azure.confidentialledger.certificate.aio import (
    ConfidentialLedgerCertificateClient,
)

from .testcase import ConfidentialLedgerPreparer


class ConfidentialLedgerCertificateClientTest(AzureTestCase):
    @ConfidentialLedgerPreparer()
    async def test_get_ledger_identity(self, confidentialledger_id):
        client = self.create_client_from_credential(
            ConfidentialLedgerCertificateClient,
            credential=None,
        )

        try:
            network_identity = (
                await client.get_ledger_identity(
                    ledger_id=confidentialledger_id
                )
            )

            assert network_identity["ledgerId"] == confidentialledger_id
            assert network_identity["ledgerTlsCertificate"]
        finally:
            await client.close()

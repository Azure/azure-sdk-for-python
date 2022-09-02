from devtools_testutils import AzureRecordedTestCase
from devtools_testutils.aio import recorded_by_proxy_async

from azure.confidentialledger.certificate.aio import (
    ConfidentialLedgerCertificateClient,
)

from _shared.testcase import ConfidentialLedgerPreparer


class TestConfidentialLedgerCertificateClient(AzureRecordedTestCase):
    @ConfidentialLedgerPreparer()
    @recorded_by_proxy_async
    async def test_get_ledger_identity(self, **kwargs):
        confidentialledger_id = kwargs.pop("confidentialledger_id")

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

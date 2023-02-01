from devtools_testutils import AzureRecordedTestCase, recorded_by_proxy

from azure.confidentialledger.certificate import (
    ConfidentialLedgerCertificateClient,
)

from _shared.testcase import ConfidentialLedgerPreparer


class TestConfidentialLedgerCertificateClient(AzureRecordedTestCase):
    @ConfidentialLedgerPreparer()
    @recorded_by_proxy
    def test_get_ledger_identity(self, **kwargs):
        confidentialledger_id = kwargs.pop("confidentialledger_id")

        client = self.create_client_from_credential(
            ConfidentialLedgerCertificateClient,
            credential=None,
        )

        network_identity = (
            client.get_ledger_identity(
                ledger_id=confidentialledger_id
            )
        )

        assert network_identity["ledgerId"] == confidentialledger_id
        assert network_identity["ledgerTlsCertificate"]

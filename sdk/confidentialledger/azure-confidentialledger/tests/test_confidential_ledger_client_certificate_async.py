from azure.confidentialledger import (
    ConfidentialLedgerCertificateCredential,
)
from azure.confidentialledger.aio import ConfidentialLedgerClient

from _shared.client_test_common_async import AsyncConfidentialLedgerClientTestMixin


class AsyncCertificateCredentialClientTest(
    AsyncConfidentialLedgerClientTestMixin.AsyncBaseTest
):
    def setUp(self):
        super(AsyncCertificateCredentialClientTest, self).setUp()
        self.client = self.create_client_from_credential(
            ConfidentialLedgerClient,
            credential=ConfidentialLedgerCertificateCredential(
                self.user_certificate_path
            ),
            ledger_certificate_path=self.network_certificate_path,
            endpoint=self.confidential_ledger_url,
        )

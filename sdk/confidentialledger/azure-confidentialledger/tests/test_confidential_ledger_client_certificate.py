from azure.confidentialledger import (
    ConfidentialLedgerClient,
    ConfidentialLedgerCertificateCredential,
)

from _shared.client_test_common import ConfidentialLedgerClientTestMixin


class CertificateCredentialClientTest(ConfidentialLedgerClientTestMixin.BaseTest):
    def setUp(self):
        super(CertificateCredentialClientTest, self).setUp()
        self.client = self.create_client_from_credential(
            ConfidentialLedgerClient,
            credential=ConfidentialLedgerCertificateCredential(
                self.user_certificate_path
            ),
            ledger_certificate_path=self.network_certificate_path,
            endpoint=self.confidential_ledger_url,
        )

from azure.confidentialledger import (
    ConfidentialLedgerClient,
    ConfidentialLedgerCertificateCredential,
    LedgerUserRole,
)

from _shared.client_test_common import ConfidentialLedgerClientTestMixin

AAD_USER_OBJECT_ID = "a" * 36


class AadCredentialClientTest(ConfidentialLedgerClientTestMixin.BaseTest):
    def setUp(self):
        super(AadCredentialClientTest, self).setUp()
        self.client = self.create_client_from_credential(
            ConfidentialLedgerClient,
            credential=self.get_credential(ConfidentialLedgerClient),
            ledger_certificate_path=self.network_certificate_path,
            endpoint=self.confidential_ledger_url,
        )

        client = self.create_client_from_credential(
            ConfidentialLedgerClient,
            credential=ConfidentialLedgerCertificateCredential(
                self.user_certificate_path
            ),
            ledger_certificate_path=self.network_certificate_path,
            endpoint=self.confidential_ledger_url,
        )

        aad_object_id = self.set_value_to_scrub(
            "CONFIDENTIAL_LEDGER_AAD_USER_OBJECT_ID", AAD_USER_OBJECT_ID
        )
        client.create_or_update_user(aad_object_id, LedgerUserRole.ADMINISTRATOR)

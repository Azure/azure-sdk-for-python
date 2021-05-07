import asyncio
import time

from azure.confidentialledger import (
    ConfidentialLedgerCertificateCredential,
    LedgerUserRole,
)
from azure.confidentialledger.aio import ConfidentialLedgerClient

from _shared.client_test_common_async import AsyncConfidentialLedgerClientTestMixin

AAD_USER_OBJECT_ID = "a" * 36


class AsyncAadCredentialClientTest(
    AsyncConfidentialLedgerClientTestMixin.AsyncBaseTest
):
    def setUp(self):
        super().setUp()
        self.client = self.create_client_from_credential(
            ConfidentialLedgerClient,
            credential=self.get_credential(ConfidentialLedgerClient, is_async=True),
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

        # Since setUp cannot be async
        task = asyncio.ensure_future(
            client.create_or_update_user(aad_object_id, LedgerUserRole.ADMINISTRATOR)
        )
        while not task.done:
            time.sleep(0.5)

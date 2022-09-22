import functools
import os
import tempfile

from devtools_testutils import AzureTestCase, PowerShellPreparer

from azure.confidentialledger.certificate import (
    ConfidentialLedgerCertificateClient,
)

from .constants import USER_CERTIFICATE


ConfidentialLedgerPreparer = functools.partial(
    PowerShellPreparer,
    "confidentialledger",
    confidentialledger_id="fake",
    confidentialledger_endpoint="https://fake.confidential-ledger.azure.com",
    confidentialledger_resource_group="fakegroup",
)


class ConfidentialLedgerTestCase(AzureTestCase):
    def __init__(self, *args, **kwargs):
        super(ConfidentialLedgerTestCase, self).__init__(*args, **kwargs)

    def setUp(self):
        super().setUp()

        with tempfile.NamedTemporaryFile(
            "w", suffix=".pem", delete=False
        ) as tls_cert_file:
            self.network_certificate_path = tls_cert_file.name

        with tempfile.NamedTemporaryFile(
            "w", suffix=".pem", delete=False
        ) as user_cert_file:
            user_cert_file.write(USER_CERTIFICATE)
            self.user_certificate_path = user_cert_file.name

    def tearDown(self):
        os.remove(self.user_certificate_path)
        if self.network_certificate_path:
            os.remove(self.network_certificate_path)

        return super().tearDown()

    def set_ledger_identity(self, confidentialledger_id):
        client = self.create_client_from_credential(
            ConfidentialLedgerCertificateClient,
            credential=None,
        )

        network_identity = (
            client.get_ledger_identity(
                ledger_id=confidentialledger_id
            )
        )

        with open(self.network_certificate_path, "w", encoding="utf-8") as outfile:
            outfile.write(network_identity["ledgerTlsCertificate"])

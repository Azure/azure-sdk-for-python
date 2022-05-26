import functools
import os
import tempfile

from devtools_testutils import AzureTestCase, PowerShellPreparer

from .constants import NETWORK_CERTIFICATE, USER_CERTIFICATE


ConfidentialLedgerPreparer = functools.partial(
    PowerShellPreparer,
    "confidentialledger",
    confidentialledger_endpoint="https://fake.confidential-ledger.azure.com",
    confidentialledger_group="fakegroup",
)


class ConfidentialLedgerTestCase(AzureTestCase):
    def __init__(self, *args, **kwargs):
        super(ConfidentialLedgerTestCase, self).__init__(*args, **kwargs)

    def setUp(self):
        super().setUp()

        with tempfile.NamedTemporaryFile(
            "w", suffix=".pem", delete=False
        ) as tls_cert_file:
            tls_cert_file.write(NETWORK_CERTIFICATE)
            self.network_certificate_path = tls_cert_file.name

        with tempfile.NamedTemporaryFile(
            "w", suffix=".pem", delete=False
        ) as user_cert_file:
            user_cert_file.write(USER_CERTIFICATE)
            self.user_certificate_path = user_cert_file.name

    def tearDown(self):
        os.remove(self.user_certificate_path)
        os.remove(self.network_certificate_path)
        return super().tearDown()

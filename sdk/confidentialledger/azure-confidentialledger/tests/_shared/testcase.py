import functools
import os
import tempfile

from devtools_testutils import (
    AzureRecordedTestCase,
    PowerShellPreparer,
)

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


class ConfidentialLedgerTestCase(AzureRecordedTestCase):
    @classmethod
    def setup_class(cls):
        """setup any state specific to the execution of the given class (which
        usually contains tests).
        """

        with tempfile.NamedTemporaryFile(
            "w", suffix=".pem", delete=False
        ) as tls_cert_file:
            cls.network_certificate_path = tls_cert_file.name

        with tempfile.NamedTemporaryFile(
            "w", suffix=".pem", delete=False
        ) as user_cert_file:
            user_cert_file.write(USER_CERTIFICATE)
            cls.user_certificate_path = user_cert_file.name

    @classmethod
    def teardown_class(cls):
        """teardown any state that was previously setup with a call to
        setup_class.
        """
        os.remove(cls.user_certificate_path)
        if cls.network_certificate_path:
            os.remove(cls.network_certificate_path)

    def set_ledger_identity(self, confidentialledger_id: str) -> str:
        """Retrieves the Confidential Ledger's TLS certificate, saving it to the object's network
        certificate path as well as returning it directly.

        :param confidentialledger_id: Id of the Confidential Ledger.
        :type confidentialledger_id: str
        :return: The Confidential Ledger's TLS certificate.
        :rtype: str
        """
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

        return network_identity["ledgerTlsCertificate"]

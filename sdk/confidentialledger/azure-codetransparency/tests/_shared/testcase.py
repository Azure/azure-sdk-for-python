import functools
import os
import tempfile

from devtools_testutils import (
    AzureRecordedTestCase,
    EnvironmentVariableLoader,
)

from azure.confidentialledger.certificate import (
    ConfidentialLedgerCertificateClient,
)
from azure.confidentialledger.certificate.aio import (
    ConfidentialLedgerCertificateClient as ConfidentialLedgerCertificateClientAsync,
)


CodeTransparencyPreparer = functools.partial(
    EnvironmentVariableLoader,
    "codetransparency",
    codetransparency_id="fake",
    codetransparency_endpoint="https://fake.confidential-ledger.azure.com",
)


class CodeTransparencyClientTestBase(AzureRecordedTestCase):
    @classmethod
    def setup_class(cls):
        """setup any state specific to the execution of the given class (which
        usually contains tests).
        """

        with tempfile.NamedTemporaryFile(
            "w", suffix=".pem", delete=False
        ) as tls_cert_file:
            cls.network_certificate_path = tls_cert_file.name

    @classmethod
    def teardown_class(cls):
        """teardown any state that was previously setup with a call to
        setup_class.
        """
        if cls.network_certificate_path:
            try:
                os.remove(cls.network_certificate_path)
            except FileNotFoundError:
                pass

    def set_ledger_identity(self, codetransparency_id: str) -> str:
        """Retrieves the Confidential Ledger's TLS certificate, saving it to the object's network
        certificate path as well as returning it directly.

        :param codetransparency_id: Id of the Confidential Ledger.
        :type codetransparency_id: str
        :return: The Confidential Ledger's TLS certificate.
        :rtype: str
        """
        client = self.create_client_from_credential(
            ConfidentialLedgerCertificateClient,
            credential=None,
        )

        network_identity = client.get_ledger_identity(ledger_id=codetransparency_id)

        with open(self.network_certificate_path, "w", encoding="utf-8") as outfile:
            outfile.write(network_identity["ledgerTlsCertificate"])

        return network_identity["ledgerTlsCertificate"]

    async def set_ledger_identity_async(self, codetransparency_id: str) -> str:
        """Retrieves the Confidential Ledger's TLS certificate, saving it to the object's network
        certificate path as well as returning it directly.

        An async version of this method is needed so that this request is recorded by async tests.

        :param codetransparency_id: Id of the Confidential Ledger.
        :type codetransparency_id: str
        :return: The Confidential Ledger's TLS certificate.
        :rtype: str
        """
        client = self.create_client_from_credential(
            ConfidentialLedgerCertificateClientAsync,
            credential=None,
        )

        try:
            network_identity = await client.get_ledger_identity(
                ledger_id=codetransparency_id
            )

            with open(self.network_certificate_path, "w", encoding="utf-8") as outfile:
                outfile.write(network_identity["ledgerTlsCertificate"])

            return network_identity["ledgerTlsCertificate"]
        finally:
            await client.close()

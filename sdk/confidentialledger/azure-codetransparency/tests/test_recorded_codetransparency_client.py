# pylint: disable=line-too-long,useless-suppression
# cSpell:ignore operationid
from typing import Dict, List, Union
from urllib.parse import urlparse
from azure.core import exceptions
import pytest

from devtools_testutils import recorded_by_proxy
from devtools_testutils import (
    PemCertificate,
    create_combined_bundle,
    is_live,
    is_live_and_not_recording,
    set_function_recording_options,
)

from azure.codetransparency import (
    CodeTransparencyClient,
)
from azure.codetransparency.cbor import (
    CBORDecoder,
)

from _shared.constants import (
    TEST_PROXY_CERT,
)
from _shared.testcase import CodeTransparencyPreparer, CodeTransparencyClientTestBase


class TestCodetransparencyClient(CodeTransparencyClientTestBase):
    def create_client(
        self, endpoint, ledger_id
    ) -> CodeTransparencyClient:
        # Always explicitly fetch the TLS certificate.
        network_cert = self.set_ledger_identity(ledger_id)

        client = self.create_client_from_credential(
            CodeTransparencyClient,
            credential=None,
            endpoint=endpoint,
            ledger_certificate_path=self.network_certificate_path,  # type: ignore
        )

        # The Confidential Ledger always presents a self-signed certificate, so add that certificate
        # to the recording options for the Confidential Ledger endpoint.
        function_recording_options: Dict[str, Union[str, List[PemCertificate]]] = {
            "tls_certificate": network_cert,
            "tls_certificate_host": urlparse(endpoint).netloc,
        }
        if is_live():
            set_function_recording_options(**function_recording_options)

        if not is_live_and_not_recording():
            # For live, non-recorded tests, we want to test normal client behavior so the only
            # certificate used for TLS verification is the Confidential Ledger identity certificate.
            #
            # However, in this case outbound connections are to the proxy, so the certificate used
            # for verifying the TLS connection should actually be the test proxy's certificate.
            # With that in mind, we'll update the file at self.network_certificate_path to be a
            # certificate bundle including both the ledger's TLS certificate (though technically
            # unnecessary I think) and the test-proxy certificate. This way the client setup (i.e.
            # the logic for overriding the default certificate verification) is still tested when
            # the test-proxy is involved.
            #
            # Note the combined bundle should be created *after* any os.remove calls so we don't
            # interfere with auto-magic certificate retrieval tests.
            create_combined_bundle(
                [self.network_certificate_path, TEST_PROXY_CERT],
                self.network_certificate_path,
            )

        return client

    @CodeTransparencyPreparer()
    @recorded_by_proxy
    def test_register_signature_fails(self, **kwargs):
        codetransparency_endpoint = kwargs.pop("codetransparency_endpoint")
        codetransparency_id = kwargs.pop("codetransparency_id")
        client = self.create_client(
            codetransparency_endpoint, codetransparency_id
        )
        with pytest.raises(exceptions.HttpResponseError) as ex:
            client.create_entry(
                body=bytes("invalid cbor bytes", encoding="utf-8"),
                content_type="application/cose",
                accept="application/cose; application/cbor",
            )
        # Access the exception value and check error details
        error = ex.value
        assert error is not None, "Expected error details in exception"
        assert (
            error.message == "InvalidInput"
        ), f"Expected error code 'InvalidInput', but got: {error.message}"

    def create_valid_cose_sign1(self) -> bytes:
        import base64

        b64_sign1 = "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"
        return base64.b64decode(b64_sign1)

    @CodeTransparencyPreparer()
    @recorded_by_proxy
    def test_register_signature_returns_pending_operation(self, **kwargs):
        codetransparency_endpoint = kwargs.pop("codetransparency_endpoint")
        codetransparency_id = kwargs.pop("codetransparency_id")
        client = self.create_client(
            codetransparency_endpoint, codetransparency_id
        )
        register_result = client.create_entry(
            body=self.create_valid_cose_sign1(),
            content_type="application/cose",
            accept="application/cose; application/cbor",
        )
        # Collect the response bytes and check for error message about invalid input
        response_bytes = b"".join(register_result)
        # decode cbor and verify decoded output contains {"OperationId": "some transaction num", "Status": "running"}

        decoder = CBORDecoder(response_bytes)
        decoded_cbor = decoder.decode()
        assert (decoded_cbor["Status"] == "running"), f"Expected status 'running', but got: {decoded_cbor['Status']}"
        assert (
            "OperationId" in decoded_cbor
        ), "Expected 'OperationId' field in response, but it was missing."

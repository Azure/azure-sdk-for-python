# pylint: disable=line-too-long,useless-suppression
import pytest
import responses
import json
import os
from typing import Any, List, Optional, Tuple
from unittest.mock import MagicMock

from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import HttpResponseError
from azure.core.pipeline.transport import AsyncHttpTransport
from azure.core.rest._http_response_impl_async import AsyncHttpResponseImpl
from azure.codetransparency.aio import (
    CodeTransparencyClient,
)
from azure.codetransparency.cbor import (
    CBORDecoder,
)
from azure.codetransparency.receipt import (
    verify_transparent_statement,
    VerificationOptions,
    AuthorizedReceiptBehavior,
    UnauthorizedReceiptBehavior,
    OfflineKeysBehavior,
)

# Get the directory containing test files
TEST_FILES_DIR = os.path.join(os.path.dirname(__file__), "test_files")


def read_file_bytes(name: str) -> bytes:
    """Read a test file and return its bytes."""
    file_path = os.path.join(TEST_FILES_DIR, name)
    with open(file_path, "rb") as f:
        return f.read()


class MockAsyncResponse(AsyncHttpResponseImpl):
    """Mock async HTTP response for testing."""

    def __init__(
        self, request, body: bytes, status_code: int, headers: Optional[dict] = None
    ):
        headers = headers or {}
        super().__init__(
            request=request,
            internal_response=MagicMock(),
            content_type=headers.get("Content-Type", "application/octet-stream"),
            block_size=None,
            status_code=status_code,
            reason="OK" if status_code < 400 else "Error",
            headers=headers,
            stream_download_generator=None,
        )
        self._content = body
        self._is_closed = True
        self._is_stream_consumed = True


class MockAsyncTransport(AsyncHttpTransport):
    """Mock async transport that returns pre-configured responses."""

    def __init__(self, responses: List[Tuple[int, bytes, dict]]):
        """
        Initialize with a list of responses to return in order.
        Each response is a tuple of (status_code, body, headers).
        """
        self._responses = responses
        self._call_index = 0
        self.requests: List[Any] = []

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        pass

    async def open(self):
        pass

    async def close(self):
        pass

    async def send(self, request, **kwargs):
        self.requests.append(request)
        if self._call_index < len(self._responses):
            status_code, body, headers = self._responses[self._call_index]
            self._call_index += 1
            return MockAsyncResponse(request, body, status_code, headers)
        raise Exception("No more mock responses configured")


@pytest.fixture
def cert_file(tmp_path):
    """Create a pre-existing certificate file to skip identity service call."""
    cert_path = os.path.join(tmp_path, "ledger_cert.pem")
    # Write a dummy certificate - the content doesn't matter for mocked tests
    with open(cert_path, "w") as f:
        f.write(
            "-----BEGIN CERTIFICATE-----\nMIIB...IDAQAB\n-----END CERTIFICATE-----\n"  # cSpell:disable-line
        )  # cSpell:disable-line
    return cert_path


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "status_code,should_raise",
    [
        pytest.param(200, False, id="success_200"),
        pytest.param(500, True, id="error_500"),
    ],
)
async def test_get_transparency_config_cbor_with_data(
    cert_file, status_code, should_raise
):
    """Test that get_transparency_config_cbor returns CBOR data or raises on error."""
    # CBOR encoded empty map: 0xa0 = {}
    cbor_data = b"\xa0"

    transport = MockAsyncTransport(
        [(status_code, cbor_data, {"Content-Type": "application/cbor"})]
    )

    client = CodeTransparencyClient(
        endpoint="https://test.confidential-ledger.azure.com",
        credential=AzureKeyCredential("fakeCredential=="),
        ledger_certificate_path=cert_file,
        transport=transport,
        retry_total=0,  # Disable retries for testing error cases
    )

    if should_raise:
        with pytest.raises(HttpResponseError):
            await client.get_transparency_config_cbor()
    else:
        response = await client.get_transparency_config_cbor()
        # Collect all bytes from async iterator
        result_bytes = b"".join([chunk async for chunk in response])
        decoded = CBORDecoder(result_bytes).decode()

        assert isinstance(decoded, dict)
        assert decoded == {}  # Expecting an empty map

    await client.close()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "status_code,should_raise",
    [
        pytest.param(200, False, id="success_200"),
        pytest.param(500, True, id="error_500"),
    ],
)
async def test_get_public_keys(cert_file, status_code, should_raise):
    """Test that get_public_keys returns JSON data or raises on error."""
    json_data = json.dumps({"keys": []}).encode()

    transport = MockAsyncTransport(
        [(status_code, json_data, {"Content-Type": "application/json"})]
    )

    client = CodeTransparencyClient(
        endpoint="https://test.confidential-ledger.azure.com",
        credential=AzureKeyCredential("fakeCredential=="),
        ledger_certificate_path=cert_file,
        transport=transport,
        retry_total=0,  # Disable retries for testing error cases
    )

    if should_raise:
        with pytest.raises(HttpResponseError):
            await client.get_public_keys()
    else:
        response = await client.get_public_keys()
        # Response is AsyncIterator[bytes], collect all bytes
        result = b"".join([chunk async for chunk in response])
        assert json.loads(result) == {"keys": []}

    await client.close()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "status_code,should_raise",
    [
        pytest.param(201, False, id="success_201_created"),
        pytest.param(202, False, id="success_202_accepted"),
        pytest.param(500, True, id="error_500"),
    ],
)
async def test_create_entry(cert_file, status_code, should_raise):
    """Test that create_entry returns CBOR data or raises on error."""
    # CBOR encoded: {"OperationId": "123", "Status": "running"}
    cbor_data = b"\xa2jOperationIdc123fStatusgrunning"

    transport = MockAsyncTransport(
        [(status_code, cbor_data, {"Content-Type": "application/cbor"})]
    )

    client = CodeTransparencyClient(
        endpoint="https://test.confidential-ledger.azure.com",
        credential=AzureKeyCredential("fakeCredential=="),
        ledger_certificate_path=cert_file,
        transport=transport,
        retry_total=0,  # Disable retries for testing error cases
    )

    # Sample COSE_Sign1 entry (minimal valid structure)
    entry_body = b"\xd2\x84\x43\xa1\x01\x26\xa0\x44test\x40"

    if should_raise:
        with pytest.raises(HttpResponseError):
            await client.create_entry(entry_body)
    else:
        response = await client.create_entry(entry_body)
        # Response is AsyncIterator[bytes]
        result = b"".join([chunk async for chunk in response])
        assert len(result) > 0

    await client.close()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "status_code,should_raise",
    [
        pytest.param(200, False, id="success_200"),
        pytest.param(202, False, id="success_202_pending"),
        pytest.param(500, True, id="error_500"),
    ],
)
async def test_get_operation(cert_file, status_code, should_raise):
    """Test that get_operation returns CBOR data or raises on error."""
    # CBOR encoded: {"OperationId": "operation123", "Status": "succeeded"}
    cbor_data = b"\xa2jOperationIdeoperation123fStatusisucceeded"  # cSpell:disable-line

    transport = MockAsyncTransport(
        [(status_code, cbor_data, {"Content-Type": "application/cbor"})]
    )

    client = CodeTransparencyClient(
        endpoint="https://test.confidential-ledger.azure.com",
        credential=AzureKeyCredential("fakeCredential=="),
        ledger_certificate_path=cert_file,
        transport=transport,
        retry_total=0,  # Disable retries for testing error cases
    )

    if should_raise:
        with pytest.raises(HttpResponseError):
            await client.get_operation("operation123")
    else:
        response = await client.get_operation("operation123")
        result = b"".join([chunk async for chunk in response])
        assert len(result) > 0

    await client.close()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "status_code,should_raise",
    [
        pytest.param(200, False, id="success_200"),
        pytest.param(500, True, id="error_500"),
    ],
)
async def test_get_entry(cert_file, status_code, should_raise):
    """Test that get_entry returns COSE data or raises on error."""
    # Sample COSE_Sign1 response bytes
    cose_data = b"\xd2\x84\x43\xa1\x01\x26\xa0\x44test\x40"

    transport = MockAsyncTransport(
        [(status_code, cose_data, {"Content-Type": "application/cose"})]
    )

    client = CodeTransparencyClient(
        endpoint="https://test.confidential-ledger.azure.com",
        credential=AzureKeyCredential("fakeCredential=="),
        ledger_certificate_path=cert_file,
        transport=transport,
        retry_total=0,  # Disable retries for testing error cases
    )

    if should_raise:
        with pytest.raises(HttpResponseError):
            await client.get_entry("entry123")
    else:
        response = await client.get_entry("entry123")
        result = b"".join([chunk async for chunk in response])
        assert len(result) > 0

    await client.close()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "status_code,should_raise",
    [
        pytest.param(200, False, id="success_200"),
        pytest.param(500, True, id="error_500"),
    ],
)
async def test_get_entry_statement(cert_file, status_code, should_raise):
    """Test that get_entry_statement returns COSE data or raises on error."""
    # Sample COSE_Sign1 statement response bytes
    cose_data = b"\xd2\x84\x43\xa1\x01\x26\xa0\x44test\x40"

    transport = MockAsyncTransport(
        [(status_code, cose_data, {"Content-Type": "application/cose"})]
    )

    client = CodeTransparencyClient(
        endpoint="https://test.confidential-ledger.azure.com",
        credential=AzureKeyCredential("fakeCredential=="),
        ledger_certificate_path=cert_file,
        transport=transport,
        retry_total=0,  # Disable retries for testing error cases
    )

    if should_raise:
        with pytest.raises(HttpResponseError):
            await client.get_entry_statement("entry123")
    else:
        response = await client.get_entry_statement("entry123")
        result = b"".join([chunk async for chunk in response])
        assert len(result) > 0

    await client.close()


@pytest.mark.asyncio
async def test_begin_create_entry_with_polling(cert_file):
    """Test that begin_create_entry polls until operation succeeds."""
    # CBOR encoded: {"OperationId": "22.34", "Status": "running"}
    running_operation_hex = (
        "A26B4F7065726174696F6E49646532322E3334665374617475736772756E6E696E67"
    )
    running_operation_cbor = bytes.fromhex(running_operation_hex)
    # CBOR encoded: {"EntryId": "22.34", "Status": "succeeded"}
    operation_succeeded_hex = (
        "A267456E74727949646532322E33346653746174757369737563636565646564"
    )
    operation_succeeded_cbor = bytes.fromhex(operation_succeeded_hex)

    transport = MockAsyncTransport(
        [
            # create_entry POST request
            (202, running_operation_cbor, {"Content-Type": "application/cbor"}),
            # get_operation GET request (polling) - first returns running
            (200, running_operation_cbor, {"Content-Type": "application/cbor"}),
            # Second poll returns succeeded
            (200, operation_succeeded_cbor, {"Content-Type": "application/cbor"}),
        ]
    )

    client = CodeTransparencyClient(
        endpoint="https://test.confidential-ledger.azure.com",
        credential=AzureKeyCredential("fakeCredential=="),
        ledger_certificate_path=cert_file,
        transport=transport,
    )

    # Sample COSE_Sign1 entry (minimal valid structure)
    entry_body = b"\xd2\x84\x43\xa1\x01\x26\xa0\x44test\x40"

    poller = await client.begin_create_entry(entry_body, polling_interval=0.1)
    result = await poller.result()
    assert poller.status() == "finished"
    operation = CBORDecoder(result).decode()
    assert operation.get("Status") == "succeeded"
    # Verify polling happened: 1 POST + 2 GET operations
    assert len(transport.requests) == 3

    await client.close()


@pytest.mark.asyncio
async def test_begin_wait_for_operation_with_polling(cert_file):
    """Test that begin_wait_for_operation polls until operation succeeds."""
    # CBOR encoded: {"OperationId": "22.34", "Status": "running"}
    running_operation_hex = (
        "A26B4F7065726174696F6E49646532322E3334665374617475736772756E6E696E67"
    )
    running_operation_cbor = bytes.fromhex(running_operation_hex)
    # CBOR encoded: {"OperationId": "22.34", "Status": "succeeded"}
    operation_succeeded_hex = (
        "A26B4F7065726174696F6E49646532322E33346653746174757369737563636565646564"
    )
    operation_succeeded_cbor = bytes.fromhex(operation_succeeded_hex)

    transport = MockAsyncTransport(
        [
            # First poll returns running
            (200, running_operation_cbor, {"Content-Type": "application/cbor"}),
            # Second poll returns running
            (200, running_operation_cbor, {"Content-Type": "application/cbor"}),
            # Third poll returns succeeded
            (200, operation_succeeded_cbor, {"Content-Type": "application/cbor"}),
        ]
    )

    client = CodeTransparencyClient(
        endpoint="https://test.confidential-ledger.azure.com",
        credential=AzureKeyCredential("fakeCredential=="),
        ledger_certificate_path=cert_file,
        transport=transport,
    )

    poller = await client.begin_wait_for_operation("22.34", polling_interval=0.1)
    result = await poller.result()
    assert poller.status() == "finished"
    assert poller.done()
    # Verify polling happened: 3 GET operations
    assert len(transport.requests) == 3

    await client.close()


@responses.activate
@pytest.mark.asyncio
async def test_register_poll_verify(cert_file):
    """Test full flow: create_entry with polling, then get_entry_statement with default retries and verify."""
    # Create entry POST response. CBOR encoded: {"OperationId": "22.34", "Status": "running"}
    running_operation_hex = (
        "A26B4F7065726174696F6E49646532322E3334665374617475736772756E6E696E67"
    )
    running_operation_cbor = bytes.fromhex(running_operation_hex)
    # Create entry poll response. CBOR encoded: {"EntryId": "22.34", "Status": "succeeded"}
    operation_succeeded_hex = (
        "A267456E74727949646532322E33346653746174757369737563636565646564"
    )
    operation_succeeded_cbor = bytes.fromhex(operation_succeeded_hex)
    # Get statement error. CBOR encoded: {-1: "TransactionNotCached", -2: "Historical transaction 22.34 is not cached."}
    transaction_pending_hex = "A220745472616E73616374696F6E4E6F7443616368656421782B486973746F726963616C207472616E73616374696F6E2032322E3334206973206E6F74206361636865642E"
    transaction_pending_cbor = bytes.fromhex(transaction_pending_hex)
    # Get statement response is COSE_Sign1 bytes
    transparent_statement_bytes = read_file_bytes("transparent_statement.cose")
    # Verifier will download the valid JWKS for the issuer foo.bar.com
    valid_jwk = {
        "crv": "P-384",
        "kid": "fb29ce6d6b37e7a0b03a5fc94205490e1c37de1f41f68b92e3620021e9981d01",
        "kty": "EC",
        "x": "Tv_tP9eJIb5oJY9YB6iAzMfds4v3N84f8pgcPYLaxd_Nj3Nb_dBm6Fc8ViDZQhGR",
        "y": "xJ7fI2kA8gs11XDc9h2zodU-fZYRrE0UJHpzPfDVJrOpTvPcDoC5EWOBx9Fks0bZ",
    }
    jwks_document = {"keys": [valid_jwk]}

    main_client_transport_mocked = MockAsyncTransport(
        [
            # create_entry POST request
            (202, running_operation_cbor, {"Content-Type": "application/cbor"}),
            # get_operation GET request (polling) - first returns running
            (200, running_operation_cbor, {"Content-Type": "application/cbor"}),
            # Second poll returns succeeded
            (200, operation_succeeded_cbor, {"Content-Type": "application/cbor"}),
            # get_entry_statement GET request - first returns transaction not cached
            (
                503,
                transaction_pending_cbor,
                {"Content-Type": "application/concise-problem-details+cbor"},
            ),
            # Second get_entry_statement returns succeeded
            (200, transparent_statement_bytes, {"Content-Type": "application/cose"}),
        ]
    )

    client = CodeTransparencyClient(
        endpoint="https://test.confidential-ledger.azure.com",
        credential=None,
        ledger_certificate_path=cert_file,
        transport=main_client_transport_mocked,
    )

    # Sample COSE_Sign1 entry (minimal valid structure)
    entry_body = b"\xd2\x84\x43\xa1\x01\x26\xa0\x44test\x40"

    # Create entry with polling
    poller = await client.begin_create_entry(entry_body, polling_interval=0.1)
    result = await poller.result()
    assert poller.status() == "finished"
    operation = CBORDecoder(result).decode()
    assert operation.get("Status") == "succeeded"
    entry_id = operation.get("EntryId")
    assert entry_id == "22.34"
    # Get entry statement with retries
    transparent_statement = await client.get_entry_statement(entry_id)
    transparent_statement_bytes = b"".join(
        [chunk async for chunk in transparent_statement]
    )

    # Verify polling happened: 1 POST + 4 GET operations
    assert len(main_client_transport_mocked.requests) == 5
    await client.close()

    # Verify the transparent statement, it will use sync client under the hood which needs different response mocking
    responses.add(
        responses.GET,
        "https://foo.bar.com/jwks",
        body=json.dumps(jwks_document),
        status=200,
        content_type="application/json",
    )
    # use similar options as in the readme
    verification_options = VerificationOptions(
        authorized_domains=["foo.bar.com"],
        authorized_receipt_behavior=AuthorizedReceiptBehavior.VERIFY_ALL_MATCHING,
        unauthorized_receipt_behavior=UnauthorizedReceiptBehavior.FAIL_IF_PRESENT,
        offline_keys=None,  # No offline keys - force network fallback
        offline_keys_behavior=OfflineKeysBehavior.FALLBACK_TO_NETWORK,
    )
    try:
        verify_transparent_statement(
            transparent_statement_bytes,
            verification_options,
            ledger_certificate_path=cert_file,
        )
    except Exception as e:
        pytest.fail(f"Verification failed: {e}")

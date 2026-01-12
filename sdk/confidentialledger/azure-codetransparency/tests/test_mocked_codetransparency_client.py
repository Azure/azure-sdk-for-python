# pylint: disable=line-too-long,useless-suppression
import pytest
import responses
import json
import tempfile
import os
from unittest import TestCase
from unittest.mock import AsyncMock, Mock

from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import HttpResponseError
from azure.core.pipeline.policies import RetryPolicy
from azure.codetransparency import (
    CodeTransparencyClient,
)
from azure.codetransparency.cbor import (
    CBORDecoder,
)


@pytest.fixture
def mock_ledger_identity():
    """Reusable fixture for mocking ledger identity endpoint."""
    responses.add(
        responses.GET,
        "https://identity.confidential-ledger.core.azure.com/ledgerIdentity/test",
        body=json.dumps(
            {
                "ledgerTlsCertificate": "-----BEGIN CERTIFICATE-----\nMIIB...IDAQAB\n-----END CERTIFICATE-----\n"  # cSpell:disable-line
            }
        ),
        status=200,
        content_type="application/json",
    )


@responses.activate
@pytest.mark.parametrize(
    "status_code,should_raise",
    [
        pytest.param(200, False, id="success_200"),
        pytest.param(500, True, id="error_500"),
    ],
)
def test_get_transparency_config_cbor_with_data(
    mock_ledger_identity, tmp_path, status_code, should_raise
):
    """Test that get_transparency_config_cbor returns CBOR data or raises on error."""
    # CBOR encoded empty map: 0xa0 = {}
    cbor_data = b"\xa0"

    responses.add(
        responses.GET,
        "https://test.confidential-ledger.azure.com/.well-known/transparency-configuration",
        body=cbor_data,
        status=status_code,
        content_type="application/cbor",
    )

    cert_path = os.path.join(tmp_path, "ledger_cert.pem")

    client = CodeTransparencyClient(
        endpoint="https://test.confidential-ledger.azure.com",
        credential=AzureKeyCredential("fakeCredential=="),
        ledger_certificate_path=cert_path,
        policies=[RetryPolicy.no_retries()],
    )

    if should_raise:
        with pytest.raises(HttpResponseError):
            client.get_transparency_config_cbor()
    else:
        response = client.get_transparency_config_cbor()
        # Decode the CBOR response
        decoded = CBORDecoder.from_response(response).decode()

        assert isinstance(decoded, dict)
        assert decoded == {}  # Expecting an empty map


@responses.activate
@pytest.mark.parametrize(
    "status_code,should_raise",
    [
        pytest.param(200, False, id="success_200"),
        pytest.param(500, True, id="error_500"),
    ],
)
def test_get_public_keys(mock_ledger_identity, tmp_path, status_code, should_raise):
    """Test that get_public_keys returns JSON data or raises on error."""
    json_data = json.dumps({"keys": []})

    responses.add(
        responses.GET,
        "https://test.confidential-ledger.azure.com/jwks",
        body=json_data,
        status=status_code,
        content_type="application/json",
    )

    cert_path = os.path.join(tmp_path, "ledger_cert.pem")

    client = CodeTransparencyClient(
        endpoint="https://test.confidential-ledger.azure.com",
        credential=AzureKeyCredential("fakeCredential=="),
        ledger_certificate_path=cert_path,
        retry_total=0,
    )

    if should_raise:
        with pytest.raises(HttpResponseError):
            client.get_public_keys()
    else:
        response = client.get_public_keys()
        # Response is Iterator[bytes], collect all bytes
        result = b"".join(response)
        assert json.loads(result) == {"keys": []}


@responses.activate
@pytest.mark.parametrize(
    "status_code,should_raise",
    [
        pytest.param(201, False, id="success_201_created"),
        pytest.param(202, False, id="success_202_accepted"),
        pytest.param(500, True, id="error_500"),
    ],
)
def test_create_entry(mock_ledger_identity, tmp_path, status_code, should_raise):
    """Test that create_entry returns CBOR data or raises on error."""
    # CBOR encoded: {"OperationId": "123", "Status": "running"}
    cbor_data = b"\xa2jOperationIdc123fStatusgrunning"

    responses.add(
        responses.POST,
        "https://test.confidential-ledger.azure.com/entries",
        body=cbor_data,
        status=status_code,
        content_type="application/cbor",
    )

    cert_path = os.path.join(tmp_path, "ledger_cert.pem")

    client = CodeTransparencyClient(
        endpoint="https://test.confidential-ledger.azure.com",
        credential=AzureKeyCredential("fakeCredential=="),
        ledger_certificate_path=cert_path,
        policies=[RetryPolicy.no_retries()],
    )

    # Sample COSE_Sign1 entry (minimal valid structure)
    entry_body = b"\xd2\x84\x43\xa1\x01\x26\xa0\x44test\x40"

    if should_raise:
        with pytest.raises(HttpResponseError):
            client.create_entry(entry_body)
    else:
        response = client.create_entry(entry_body)
        # Response is Iterator[bytes]
        result = b"".join(response)
        assert len(result) > 0


@responses.activate
@pytest.mark.parametrize(
    "status_code,should_raise",
    [
        pytest.param(200, False, id="success_200"),
        pytest.param(202, False, id="success_202_pending"),
        pytest.param(500, True, id="error_500"),
    ],
)
def test_get_operation(mock_ledger_identity, tmp_path, status_code, should_raise):
    """Test that get_operation returns CBOR data or raises on error."""
    # CBOR encoded: {"OperationId": "op123", "Status": "succeeded"}
    cbor_data = b"\xa2jOperationIdeoperation123fStatusisucceeded"  # cSpell:disable-line

    responses.add(
        responses.GET,
        "https://test.confidential-ledger.azure.com/operations/operation123",
        body=cbor_data,
        status=status_code,
        content_type="application/cbor",
    )

    cert_path = os.path.join(tmp_path, "ledger_cert.pem")

    client = CodeTransparencyClient(
        endpoint="https://test.confidential-ledger.azure.com",
        credential=AzureKeyCredential("fakeCredential=="),
        ledger_certificate_path=cert_path,
        policies=[RetryPolicy.no_retries()],
    )

    if should_raise:
        with pytest.raises(HttpResponseError):
            client.get_operation("operation123")
    else:
        response = client.get_operation("operation123")
        result = b"".join(response)
        assert len(result) > 0


@responses.activate
@pytest.mark.parametrize(
    "status_code,should_raise",
    [
        pytest.param(200, False, id="success_200"),
        pytest.param(500, True, id="error_500"),
    ],
)
def test_get_entry(mock_ledger_identity, tmp_path, status_code, should_raise):
    """Test that get_entry returns COSE data or raises on error."""
    # Sample COSE_Sign1 response bytes
    cose_data = b"\xd2\x84\x43\xa1\x01\x26\xa0\x44test\x40"

    responses.add(
        responses.GET,
        "https://test.confidential-ledger.azure.com/entries/entry123",
        body=cose_data,
        status=status_code,
        content_type="application/cose",
    )

    cert_path = os.path.join(tmp_path, "ledger_cert.pem")

    client = CodeTransparencyClient(
        endpoint="https://test.confidential-ledger.azure.com",
        credential=AzureKeyCredential("fakeCredential=="),
        ledger_certificate_path=cert_path,
        policies=[RetryPolicy.no_retries()],
    )

    if should_raise:
        with pytest.raises(HttpResponseError):
            client.get_entry("entry123")
    else:
        response = client.get_entry("entry123")
        result = b"".join(response)
        assert len(result) > 0


@responses.activate
def test_get_entry_with_default_retry_policy(mock_ledger_identity, tmp_path):
    """Test that get_entry works with default retry policy."""
    # Sample COSE_Sign1 response bytes
    cose_data = b"\xd2\x84\x43\xa1\x01\x26\xa0\x44test\x40"

    responses.add(
        responses.GET,
        "https://test.confidential-ledger.azure.com/entries/entry123",
        status=503,
        adding_headers={"Retry-After": "1"},
        content_type="application/cbor",
    )

    responses.add(
        responses.GET,
        "https://test.confidential-ledger.azure.com/entries/entry123",
        status=503,
        adding_headers={"Retry-After": "1"},
        content_type="application/cbor",
    )

    # called last, after the retries
    responses.add(
        responses.GET,
        "https://test.confidential-ledger.azure.com/entries/entry123",
        status=200,
        content_type="application/cbor",
        body=cose_data,
    )

    cert_path = os.path.join(tmp_path, "ledger_cert.pem")
    client = CodeTransparencyClient(
        endpoint="https://test.confidential-ledger.azure.com",
        credential=AzureKeyCredential("fakeCredential=="),
        ledger_certificate_path=cert_path,
        # Use default retry policy
    )

    response = client.get_entry("entry123")
    result = b"".join(response)
    assert len(result) == len(cose_data)
    assert len(responses.calls) == 4  # number includes identity request


@responses.activate
@pytest.mark.parametrize(
    "status_code,should_raise",
    [
        pytest.param(200, False, id="success_200"),
        pytest.param(500, True, id="error_500"),
    ],
)
def test_get_entry_statement(mock_ledger_identity, tmp_path, status_code, should_raise):
    """Test that get_entry_statement returns COSE data or raises on error."""
    # Sample COSE_Sign1 statement response bytes
    cose_data = b"\xd2\x84\x43\xa1\x01\x26\xa0\x44test\x40"

    responses.add(
        responses.GET,
        "https://test.confidential-ledger.azure.com/entries/entry123/statement",
        body=cose_data,
        status=status_code,
        content_type="application/cose",
    )

    cert_path = os.path.join(tmp_path, "ledger_cert.pem")

    client = CodeTransparencyClient(
        endpoint="https://test.confidential-ledger.azure.com",
        credential=AzureKeyCredential("fakeCredential=="),
        ledger_certificate_path=cert_path,
        policies=[RetryPolicy.no_retries()],
    )

    if should_raise:
        with pytest.raises(HttpResponseError):
            client.get_entry_statement("entry123")
    else:
        response = client.get_entry_statement("entry123")
        result = b"".join(response)
        assert len(result) > 0


@responses.activate
def test_begin_create_entry_with_polling(mock_ledger_identity, tmp_path):
    """Test that begin_create_entry polls until operation succeeds."""
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

    # Mock the create_entry POST request
    responses.add(
        responses.POST,
        "https://test.confidential-ledger.azure.com/entries",
        body=running_operation_cbor,
        status=202,
        content_type="application/cbor",
    )

    # Mock the get_operation GET request (polling)
    responses.add(
        responses.GET,
        "https://test.confidential-ledger.azure.com/operations/22.34",
        body=running_operation_cbor,
        status=200,
        content_type="application/cbor",
    )

    responses.add(
        responses.GET,
        "https://test.confidential-ledger.azure.com/operations/22.34",
        body=operation_succeeded_cbor,
        status=200,
        content_type="application/cbor",
    )

    cert_path = os.path.join(tmp_path, "ledger_cert.pem")

    client = CodeTransparencyClient(
        endpoint="https://test.confidential-ledger.azure.com",
        credential=AzureKeyCredential("fakeCredential=="),
        ledger_certificate_path=cert_path,
        policies=[RetryPolicy.no_retries()],
    )

    # Sample COSE_Sign1 entry (minimal valid structure)
    entry_body = b"\xd2\x84\x43\xa1\x01\x26\xa0\x44test\x40"

    poller = client.begin_create_entry(entry_body, polling_interval=0.1)
    poller.wait(5.0)
    result = poller.result()
    assert poller.status() == "finished"
    operation = CBORDecoder(result).decode()
    assert operation.get("Status") == "succeeded"
    # Verify polling happened: 1 identity + 1 POST + 2 GET operations
    assert len(responses.calls) == 4


@responses.activate
def test_begin_wait_for_operation_with_polling(mock_ledger_identity, tmp_path):
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

    # First poll returns running
    responses.add(
        responses.GET,
        "https://test.confidential-ledger.azure.com/operations/22.34",
        body=running_operation_cbor,
        status=200,
        content_type="application/cbor",
    )

    # Second poll returns running
    responses.add(
        responses.GET,
        "https://test.confidential-ledger.azure.com/operations/22.34",
        body=running_operation_cbor,
        status=200,
        content_type="application/cbor",
    )

    # Third poll returns succeeded
    responses.add(
        responses.GET,
        "https://test.confidential-ledger.azure.com/operations/22.34",
        body=operation_succeeded_cbor,
        status=200,
        content_type="application/cbor",
    )

    cert_path = os.path.join(tmp_path, "ledger_cert.pem")

    client = CodeTransparencyClient(
        endpoint="https://test.confidential-ledger.azure.com",
        credential=AzureKeyCredential("fakeCredential=="),
        ledger_certificate_path=cert_path,
        policies=[RetryPolicy.no_retries()],
    )

    poller = client.begin_wait_for_operation("22.34", polling_interval=0.1)
    poller.wait(5.0)
    result = poller.result()
    assert poller.status() == "finished"
    assert poller.done()
    # Verify polling happened: 1 identity + 3 GET operations
    assert len(responses.calls) == 4

# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Unit tests for PFX-to-PEM conversion (outContentType) and previousVersion features."""
import json
from unittest import mock
from urllib import parse

import pytest

from azure.core.pipeline.transport import HttpRequest
from azure.keyvault.secrets import SecretClient, ContentType, SecretProperties
from azure.keyvault.secrets._generated import models as _models


VAULT_URL = "https://myvault.vault.azure.net"


def _make_pipeline_client(response_payload):
    """Build a SecretClient that returns the given JSON payload for every request."""
    raw_response = mock.Mock()
    raw_response.status_code = 200
    raw_response.headers = {"content-type": "application/json"}
    raw_response.content_type = "application/json"
    raw_response.text = lambda encoding=None: json.dumps(response_payload)
    raw_response.json = lambda: response_payload
    raw_response.read = mock.Mock(return_value=None)
    raw_response.is_stream_consumed = False

    def _send(request, **kwargs):
        # Store the last request for assertion
        _send.last_request = request
        return raw_response

    _send.last_request = None

    credential = mock.Mock()
    credential.get_token = mock.Mock(return_value=mock.Mock(token="fake_token", expires_on=9999999999))
    client = SecretClient(VAULT_URL, credential, api_version="2025-07-01")
    # client._client is the generated KeyVaultClient; _client._client is the PipelineClient
    client._client._client._pipeline._transport.send = _send  # pylint: disable=protected-access
    return client, _send


# ---------------------------------------------------------------------------
# Tests for previousVersion in SecretProperties
# ---------------------------------------------------------------------------

class TestPreviousVersion:
    """Tests for the previousVersion field in SecretBundle and SecretProperties."""

    def test_secret_properties_previous_version_from_bundle(self):
        """SecretProperties._from_secret_bundle should populate previous_version."""
        bundle = _models.SecretBundle(
            id=f"{VAULT_URL}/secrets/mysecret/abc123",
            value="my-cert-value",
            previous_version="xyz456",
        )
        props = SecretProperties._from_secret_bundle(bundle)
        assert props.previous_version == "xyz456"

    def test_secret_properties_previous_version_none_when_absent(self):
        """previous_version should be None when not present in the bundle."""
        bundle = _models.SecretBundle(
            id=f"{VAULT_URL}/secrets/mysecret/abc123",
            value="value",
        )
        props = SecretProperties._from_secret_bundle(bundle)
        assert props.previous_version is None

    def test_secret_properties_previous_version_constructor(self):
        """SecretProperties can be constructed with previous_version kwarg."""
        props = SecretProperties(None, f"{VAULT_URL}/secrets/test/v1", previous_version="v0")
        assert props.previous_version == "v0"

    def test_deleted_secret_bundle_previous_version(self):
        """DeletedSecretBundle previous_version should also be available via SecretProperties."""
        bundle = _models.DeletedSecretBundle(
            id=f"{VAULT_URL}/secrets/mysecret/abc123",
            value="value",
            previous_version="oldversion",
            recovery_id=f"{VAULT_URL}/deletedsecrets/mysecret",
        )
        props = SecretProperties._from_secret_bundle(bundle)
        assert props.previous_version == "oldversion"

    def test_previous_version_in_response(self):
        """get_secret response with previousVersion should be surfaced on KeyVaultSecret.properties."""
        payload = {
            "id": f"{VAULT_URL}/secrets/mysecret/abc123",
            "value": "supersecretvalue",
            "attributes": {"enabled": True, "created": 1000000, "updated": 1000000},
            "previousVersion": "oldabc",
        }
        client, _ = _make_pipeline_client(payload)
        secret = client.get_secret("mysecret")
        assert secret.properties.previous_version == "oldabc"

    def test_previous_version_absent_in_response(self):
        """get_secret response without previousVersion should return None."""
        payload = {
            "id": f"{VAULT_URL}/secrets/mysecret/abc123",
            "value": "supersecretvalue",
            "attributes": {"enabled": True, "created": 1000000, "updated": 1000000},
        }
        client, _ = _make_pipeline_client(payload)
        secret = client.get_secret("mysecret")
        assert secret.properties.previous_version is None


# ---------------------------------------------------------------------------
# Tests for outContentType (PFX-to-PEM conversion) in get_secret
# ---------------------------------------------------------------------------

class TestOutContentType:
    """Tests for the out_content_type parameter in SecretClient.get_secret."""

    def _get_request_query(self, send_mock):
        """Parse the query string of the last captured request."""
        url = send_mock.last_request.url
        parsed = parse.urlparse(url)
        return dict(parse.parse_qsl(parsed.query))

    def test_get_secret_without_out_content_type(self):
        """When out_content_type is not specified, outContentType should not appear in the query."""
        payload = {
            "id": f"{VAULT_URL}/secrets/mysecret/v1",
            "value": "data",
            "attributes": {"enabled": True, "created": 1000000, "updated": 1000000},
        }
        client, send = _make_pipeline_client(payload)
        client.get_secret("mysecret")
        query = self._get_request_query(send)
        assert "outContentType" not in query

    def test_get_secret_with_out_content_type_pem_string(self):
        """Passing out_content_type='application/x-pem-file' should add outContentType to the query."""
        payload = {
            "id": f"{VAULT_URL}/secrets/mysecret/v1",
            "value": "-----BEGIN CERTIFICATE-----\n...",
            "attributes": {"enabled": True, "created": 1000000, "updated": 1000000},
            "contentType": "application/x-pem-file",
        }
        client, send = _make_pipeline_client(payload)
        secret = client.get_secret("mysecret", out_content_type="application/x-pem-file")
        query = self._get_request_query(send)
        assert query.get("outContentType") == "application/x-pem-file"
        assert secret.value

    def test_get_secret_with_out_content_type_enum_pem(self):
        """Passing ContentType.PEM enum value should add outContentType to the query."""
        payload = {
            "id": f"{VAULT_URL}/secrets/mysecret/v1",
            "value": "-----BEGIN CERTIFICATE-----\n...",
            "attributes": {"enabled": True, "created": 1000000, "updated": 1000000},
        }
        client, send = _make_pipeline_client(payload)
        client.get_secret("mysecret", out_content_type=ContentType.PEM)
        query = self._get_request_query(send)
        assert query.get("outContentType") == "application/x-pem-file"

    def test_get_secret_with_out_content_type_enum_pfx(self):
        """Passing ContentType.PFX enum value should add outContentType=application/x-pkcs12 to the query."""
        payload = {
            "id": f"{VAULT_URL}/secrets/mysecret/v1",
            "value": "binary-pfx-data",
            "attributes": {"enabled": True, "created": 1000000, "updated": 1000000},
        }
        client, send = _make_pipeline_client(payload)
        client.get_secret("mysecret", out_content_type=ContentType.PFX)
        query = self._get_request_query(send)
        assert query.get("outContentType") == "application/x-pkcs12"

    def test_get_secret_with_version_and_out_content_type(self):
        """out_content_type should work together with an explicit secret version."""
        payload = {
            "id": f"{VAULT_URL}/secrets/mysecret/specificver",
            "value": "-----BEGIN CERTIFICATE-----\n...",
            "attributes": {"enabled": True, "created": 1000000, "updated": 1000000},
        }
        client, send = _make_pipeline_client(payload)
        client.get_secret("mysecret", version="specificver", out_content_type=ContentType.PEM)
        url = send.last_request.url
        query = dict(parse.parse_qsl(parse.urlparse(url).query))
        # Verify both version in path and outContentType in query
        assert "specificver" in url
        assert query.get("outContentType") == "application/x-pem-file"

    def test_content_type_enum_values(self):
        """ContentType enum should have expected values."""
        assert ContentType.PEM == "application/x-pem-file"
        assert ContentType.PFX == "application/x-pkcs12"

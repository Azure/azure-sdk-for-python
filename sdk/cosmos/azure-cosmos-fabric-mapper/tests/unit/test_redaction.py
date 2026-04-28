"""Redaction tests - ensure secrets never appear in diagnostic output."""

from azure.cosmos.fabric_mapper.diagnostics import DiagnosticPayload, redact


def test_redacts_password_like_fields():
    """Test that password-like fields are redacted."""
    s = "Server=tcp:example;Password=sekrit123;Database=test;"
    redacted_s = redact(s)
    assert "sekrit123" not in redacted_s
    assert "<redacted>" in redacted_s


def test_redacts_account_key():
    """Test that AccountKey is redacted."""
    s = "AccountKey=mySecretKey12345;Endpoint=https://example.com"
    redacted_s = redact(s)
    assert "mySecretKey12345" not in redacted_s
    assert "<redacted>" in redacted_s


def test_redacts_shared_access_key():
    """Test that SharedAccessKey is redacted."""
    s = "SharedAccessKey=abc123xyz;Other=value"
    redacted_s = redact(s)
    assert "abc123xyz" not in redacted_s
    assert "<redacted>" in redacted_s


def test_redacts_sig_in_sas_token():
    """Test that sig parameter in SAS tokens is redacted."""
    s = "https://example.com/path?sig=signature123&other=param"
    redacted_s = redact(s)
    assert "signature123" not in redacted_s
    assert "<redacted>" in redacted_s


def test_diagnostic_payload_safe_message():
    """Test that DiagnosticPayload.safe_message() redacts secrets."""
    payload = DiagnosticPayload(
        kind="error",
        message="Connection failed with Password=secret123",
        details={"server": "example.com", "database": "test"},
    )
    safe = payload.safe_message()
    assert "secret123" not in safe
    assert "<redacted>" in safe
    assert "details_keys=" in safe


def test_diagnostic_payload_without_details():
    """Test DiagnosticPayload with no details."""
    payload = DiagnosticPayload(kind="info", message="Query executed successfully")
    safe = payload.safe_message()
    assert safe == "Query executed successfully"


def test_redact_preserves_non_secrets():
    """Test that non-secret content is preserved."""
    s = "Server=tcp:example.com;Database=mydb;Timeout=30"
    redacted_s = redact(s)
    assert "example.com" in redacted_s
    assert "mydb" in redacted_s
    assert "Timeout=30" in redacted_s

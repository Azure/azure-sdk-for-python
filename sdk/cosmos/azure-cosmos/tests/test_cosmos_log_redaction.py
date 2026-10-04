# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
# -------------------------------------------------------------------------
"""Regression tests for CosmosHttpLoggingPolicy redaction.

Asserts the PROPERTY (sensitive headers and query-parameter values are never
logged), not a single input. Place under sdk/cosmos/azure-cosmos/tests/.
"""
import logging

from azure.cosmos._cosmos_http_logging_policy import _redact_url
from azure.cosmos.http_constants import _cosmos_allow_list


def test_sensitive_headers_are_not_in_allow_list():
    # These are redacted by azure-core's HttpLoggingPolicy by default and must
    # not be logged by the Cosmos policy either.
    for header in ("authorization", "proxy-authorization", "set-cookie",
                   "proxy-authenticate", "www-authenticate"):
        assert header not in _cosmos_allow_list, f"{header} must be redacted, not logged"


def test_redact_url_strips_query_values_keeps_path():
    url = "https://acct.documents.azure.com/dbs/d/colls/c/docs/x?sig=SECRET&%24filter=foo"
    redacted = _redact_url(url)
    assert "SECRET" not in redacted
    assert "foo" not in redacted
    # Path (database/collection/document identifiers) is preserved for diagnostics.
    assert "/dbs/d/colls/c/docs/x" in redacted


def test_redact_url_handles_no_query_and_none():
    plain = "https://acct.documents.azure.com/dbs/d/colls/c"
    assert _redact_url(plain) == plain
    assert _redact_url(None) is None
    assert _redact_url("") == ""


def test_error_path_logs_redacted_url(caplog):
    """The error path must log a URL with no query-parameter values."""
    from unittest.mock import MagicMock
    from azure.cosmos._cosmos_http_logging_policy import _log_diagnostics_error

    request = MagicMock()
    request.http_request.url = "https://acct.documents.azure.com/dbs/d/colls/c?sig=SECRET"
    request.http_request.method = "GET"
    request.http_request.headers = {}

    with caplog.at_level(logging.INFO, logger="azure.cosmos._cosmos_http_logging_policy"):
        _log_diagnostics_error(diagnostics_enabled=True, request=request,
                               response_headers={}, error=Exception("boom"))
    assert "SECRET" not in caplog.text

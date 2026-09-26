# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""The request-size estimator override preserves the default and rejects invalid values."""

from unittest.mock import Mock

import pytest
from azure.ai.finetuningsessions import _patch
from azure.ai.finetuningsessions._patch import (
    _DEFAULT_MAX_CHUNK_BYTES,
    _MAX_CHUNK_BYTES_ENV,
    _max_chunk_bytes_from_env,
)


def test_default_is_unchanged_when_unset(monkeypatch):
    monkeypatch.delenv(_MAX_CHUNK_BYTES_ENV, raising=False)
    assert _max_chunk_bytes_from_env() == _DEFAULT_MAX_CHUNK_BYTES == 5_000_000


def test_valid_positive_integer_is_honored(monkeypatch):
    monkeypatch.setenv(_MAX_CHUNK_BYTES_ENV, "10000000")
    assert _max_chunk_bytes_from_env() == 10_000_000


def test_underscored_integer_literal_is_honored(monkeypatch):
    monkeypatch.setenv(_MAX_CHUNK_BYTES_ENV, "10_000_000")
    assert _max_chunk_bytes_from_env() == 10_000_000


@pytest.mark.parametrize("invalid", ["0", "-1", "abc", "5000000.0", "", " "])
def test_invalid_values_fall_back_to_default(monkeypatch, invalid):
    monkeypatch.setenv(_MAX_CHUNK_BYTES_ENV, invalid)
    warning = Mock()
    monkeypatch.setattr(_patch._logging.getLogger(_patch.__name__), "warning", warning)
    result = _max_chunk_bytes_from_env()
    assert result == _DEFAULT_MAX_CHUNK_BYTES
    warning.assert_called_once()
    assert _MAX_CHUNK_BYTES_ENV in warning.call_args.args


def test_module_constant_reflects_env_at_import_time(monkeypatch):
    monkeypatch.setenv(_MAX_CHUNK_BYTES_ENV, "7000000")
    assert _max_chunk_bytes_from_env() == 7_000_000
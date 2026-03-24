# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""Unit tests for Directory SAS (sr=d / sdd) token generation.

These are pure unit tests — no live service calls, no recordings needed.
They verify that:
  - `sr=d` is emitted in the query parameters when is_directory=True
  - `sdd=N` is emitted with the correct depth value
  - `sdd` is NOT present in the string-to-sign (stringToSign)
  - Non-directory SAS produces `sr=b` and no `sdd`
"""

from datetime import datetime, timedelta, timezone
from urllib.parse import parse_qs

import pytest

from azure.storage.blob import BlobSasPermissions, generate_blob_sas

# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

FAKE_ACCOUNT_NAME = "fakestorageaccount"
# 64-byte base-64-like string — just needs to be a valid base64 value for HMAC
FAKE_ACCOUNT_KEY = "dGVzdGtleXRlc3RrZXl0ZXN0a2V5dGVzdGtleXRlc3RrZXl0ZXN0a2V5dGVzdGtleXRlc3Q="
FAKE_CONTAINER = "mycontainer"
EXPIRY = datetime(2030, 1, 1, tzinfo=timezone.utc)
PERMISSION = BlobSasPermissions(read=True, list=True)


def _generate(blob_name: str, is_directory: bool = False) -> tuple[str, str]:
    """Return (token, string_to_sign) for a directory or blob SAS."""
    captured = []

    token = generate_blob_sas(
        account_name=FAKE_ACCOUNT_NAME,
        container_name=FAKE_CONTAINER,
        blob_name=blob_name,
        account_key=FAKE_ACCOUNT_KEY,
        permission=PERMISSION,
        expiry=EXPIRY,
        is_directory=is_directory,
        sts_hook=captured.append,
    )
    return token, captured[0]


# ---------------------------------------------------------------------------
# Parameterized: directory depth calculation
# Each tuple: (blob_name, expected_sdd)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "blob_name, expected_sdd",
    [
        ("foo/bar/hello", 3),   # basic three-level path
        ("foo",           1),   # single level
        ("foo/bar",       2),   # two levels
        ("/",             0),   # root slash only → 0
        ("",              0),   # empty string → 0
        ("foo/bar/hello/", 3),  # trailing slash stripped → still 3
        ("/foo/bar",       2),  # leading slash stripped → 2 (not 3)
    ],
)
def test_directory_sas_depth(blob_name: str, expected_sdd: int) -> None:
    """sr=d is present, sdd equals the expected depth, sdd is absent from stringToSign."""
    token, sts = _generate(blob_name, is_directory=True)
    params = parse_qs(token)

    # sr must be 'd'
    assert params.get("sr") == ["d"], f"Expected sr=d, got {params.get('sr')}"

    # sdd must equal expected depth
    assert params.get("sdd") == [str(expected_sdd)], (
        f"blob_name={blob_name!r}: expected sdd={expected_sdd}, got {params.get('sdd')}"
    )

    # sdd must NOT appear in the string-to-sign
    assert "sdd" not in sts, (
        f"blob_name={blob_name!r}: 'sdd' should not be in stringToSign, but got:\n{sts}"
    )

    # '\nd\n' must appear in the string-to-sign (resource indicator)
    assert "\nd\n" in sts, (
        f"blob_name={blob_name!r}: expected '\\nd\\n' in stringToSign, but got:\n{sts}"
    )

    # sig must be present (token is properly signed)
    assert "sig" in params, "Token must contain a signature"


def test_non_directory_sas() -> None:
    """Without is_directory, sr=b and no sdd in the token or stringToSign."""
    token, sts = _generate("foo/bar/hello", is_directory=False)
    params = parse_qs(token)

    assert params.get("sr") == ["b"], f"Expected sr=b, got {params.get('sr')}"
    assert "sdd" not in params, f"sdd should not appear in a non-directory SAS, got {params.get('sdd')}"
    assert "sdd" not in sts, "sdd should not appear in stringToSign for a blob SAS"


def test_hns_sdd_zero_kwarg_not_dropped() -> None:
    """sdd=0 passed as an explicit kwarg (DataLake path) must not be silently dropped,
    and must override the depth computed by add_directory_depth from blob_name."""
    captured = []
    # blob_name has depth 2, but sdd=0 is passed explicitly (DataLake caller pattern)
    token = generate_blob_sas(
        account_name=FAKE_ACCOUNT_NAME,
        container_name=FAKE_CONTAINER,
        blob_name="foo/bar",
        account_key=FAKE_ACCOUNT_KEY,
        permission=PERMISSION,
        expiry=EXPIRY,
        is_directory=True,
        sdd=0,
        sts_hook=captured.append,
    )
    params = parse_qs(token)
    # sdd kwarg takes precedence over the depth computed from blob_name
    assert params.get("sdd") == ["0"], f"Expected sdd=0 in token, got {params.get('sdd')}"
    assert "sdd" not in captured[0], "sdd must not appear in stringToSign"

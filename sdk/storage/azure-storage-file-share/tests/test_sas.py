# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from base64 import b64encode
from datetime import date, datetime, timedelta, timezone
from urllib.parse import parse_qs

import pytest

from azure.storage.fileshare import generate_file_sas


@pytest.mark.parametrize(
    "expiry, expected",
    [
        (datetime(2026, 10, 13, 12, 34, 56), "2026-10-13T12:34:56Z"),
        (datetime(2026, 10, 13, 12, 34, 56, tzinfo=timezone.utc), "2026-10-13T12:34:56Z"),
        (
            datetime(2026, 10, 13, 12, 34, 56, tzinfo=timezone(timedelta(hours=5, minutes=30))),
            "2026-10-13T07:04:56Z",
        ),
        (
            datetime(2026, 10, 13, 12, 34, 56, tzinfo=timezone(timedelta(hours=-7))),
            "2026-10-13T19:34:56Z",
        ),
        (datetime(2026, 1, 1, 1, tzinfo=timezone(timedelta(hours=2))), "2025-12-31T23:00:00Z"),
        (datetime(2026, 12, 31, 23, tzinfo=timezone(timedelta(hours=-2))), "2027-01-01T01:00:00Z"),
        (datetime(2026, 10, 13, 12, 34, 56, 123456, tzinfo=timezone.utc), "2026-10-13T12:34:56Z"),
        (date(2026, 10, 13), "2026-10-13T00:00:00Z"),
    ],
)
def test_generate_file_sas_expiry(expiry, expected):
    sas = generate_file_sas(
        account_name="account",
        share_name="share",
        file_path=["directory", "file"],
        account_key=b64encode(b"fake-account-key").decode("ascii"),
        permission="r",
        expiry=expiry,
    )
    assert parse_qs(sas)["se"] == [expected]

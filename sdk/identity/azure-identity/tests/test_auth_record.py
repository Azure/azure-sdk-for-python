# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import json

from azure.identity import AuthenticationRecord
from azure.identity._auth_record import SUPPORTED_VERSIONS
import pytest


def test_serialization():
    expected = {
        "authority": "http://localhost",
        "clientId": "client-id",
        "homeAccountId": "object-id.tenant-id",
        "tenantId": "tenant-id",
        "username": "user",
        "version": "1.0",
    }

    record = AuthenticationRecord(
        expected["tenantId"],
        expected["clientId"],
        expected["authority"],
        expected["homeAccountId"],
        expected["username"],
    )
    serialized = record.serialize()

    assert json.loads(serialized) == expected

    deserialized = AuthenticationRecord.deserialize(serialized)

    assert sorted(vars(deserialized)) == sorted(vars(record))

    assert record.authority == deserialized.authority == expected["authority"]
    assert record.client_id == deserialized.client_id == expected["clientId"]
    assert record.home_account_id == deserialized.home_account_id == expected["homeAccountId"]
    assert record.tenant_id == deserialized.tenant_id == expected["tenantId"]
    assert record.username == deserialized.username == expected["username"]


@pytest.mark.parametrize("version", ("42", None))
def test_unknown_version(version):
    """deserialize should raise ValueError when the data doesn't contain a known version"""

    data = {
        "authority": "http://localhost",
        "clientId": "client-id",
        "homeAccountId": "object-id.tenant-id",
        "tenantId": "tenant-id",
        "username": "user",
    }

    if version:
        data["version"] = version

    with pytest.raises(ValueError, match=".*{}.*".format(version)) as ex:
        AuthenticationRecord.deserialize(json.dumps(data))
    assert str(SUPPORTED_VERSIONS) in str(ex.value)
